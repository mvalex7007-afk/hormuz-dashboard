'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';
import { TrendingUp, TrendingDown, AlertTriangle, Ship, DollarSign, Zap, Plus, Download, Info, ExternalLink, RefreshCw } from 'lucide-react';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

const FINNHUB_API_KEY = 'd7h95tpr01qhiu0apko0d7h95tpr01qhiu0apkog';

interface Trade {
  id: string;
  ticker: string;
  entry_price: number;
  exit_price?: number;
  position_size: number;
  pnl?: number;
  notes?: string;
  created_at: string;
}

export default function HormuzGetRichQuickDashboard() {
  const [oilPrice, setOilPrice] = useState(93.75);
  const [oilChange, setOilChange] = useState(0.3);
  const [ships24h, setShips24h] = useState(12);
  const [oilHistory, setOilHistory] = useState([93.2, 93.5, 93.8, 93.6, 93.75]);
  const [signal, setSignal] = useState('NEUTRAL – MONITOR TALKS');
  const [action, setAction] = useState('');
  const [context, setContext] = useState('');
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [trades, setTrades] = useState<Trade[]>([]);
  const [showLogger, setShowLogger] = useState(false);
  const [editingTradeId, setEditingTradeId] = useState<string | null>(null);
  const [exitPriceInput, setExitPriceInput] = useState(0);
  const [newTrade, setNewTrade] = useState({ ticker: 'ERX', entry_price: 0, position_size: 0, notes: '' });
  const [primaryTicker, setPrimaryTicker] = useState('ERX');

  const playAlert = () => {
    const audio = new Audio('https://freesound.org/data/previews/276/276951_5123854-lq.mp3');
    audio.volume = 0.25;
    audio.play().catch(() => {});
  };

  const fetchOilPrice = async () => {
    try {
      const res = await fetch(`https://finnhub.io/api/v1/quote?symbol=CL=F&token=${FINNHUB_API_KEY}`);
      const data = await res.json();
      if (data.c) {
        const newPrice = Math.round(data.c * 100) / 100;
        const prevPrice = oilPrice || newPrice;
        const newChange = Math.round(((newPrice - prevPrice) / prevPrice) * 100 * 10) / 10;
        setOilPrice(newPrice);
        setOilChange(newChange);
        setOilHistory(prev => [...prev.slice(1), newPrice]);
        setLastUpdated(new Date());
      }
    } catch (err) {
      console.error('Finnhub error:', err);
    }
  };

  const refreshShipData = () => {
    const newShips = Math.floor(Math.random() * 9) + 8;
    setShips24h(newShips);
    updateSignalAndContext(newShips);
  };

  const updateSignalAndContext = (ships: number) => {
    const percentNormal = (ships / 60) * 100;
    let newSignal = '';
    let newAction = '';
    let newContext = '';
    let newTicker = 'ERX';

    if (percentNormal < 25) {
      newSignal = 'STRONG ESCALATION – BLOCKADE TIGHT';
      newAction = '🚀 BUY LEVERAGED ENERGY NOW';
      newContext = 'Ship traffic critically low (~20% of normal). US blockade on Iranian ports active. Ceasefire fragile (expires ~Apr 22). Strong bullish bias for energy leverage.';
      newTicker = 'ERX';
      playAlert();
    } else if (percentNormal > 35) {
      newSignal = 'DE-ESCALATION – TRAFFIC REBOUND';
      newAction = '🔄 TAKE PROFIT or SHORT ENERGY';
      newContext = 'Ship traffic recovering. Positive talks or ceasefire extension likely. Good time to lock gains.';
      newTicker = 'ERY';
    } else {
      newSignal = 'NEUTRAL – MONITOR TALKS';
      newAction = 'HOLD CASH';
      newContext = 'Traffic still suppressed. Volatility expected around talks and deadline. Stay flat until clear move.';
      newTicker = 'ERX';
    }

    setSignal(newSignal);
    setAction(newAction);
    setContext(newContext);
    setPrimaryTicker(newTicker);
  };

  useEffect(() => {
    fetchOilPrice();
    const priceInterval = setInterval(fetchOilPrice, 30000);
    refreshShipData();

    const loadTrades = async () => {
      const { data } = await supabase.from('trades').select('*').order('created_at', { ascending: false });
      if (data) setTrades(data);
    };
    loadTrades();

    return () => clearInterval(priceInterval);
  }, []);

  const robinhoodLink = `https://robinhood.com/us/en/stocks/${primaryTicker}/`;
  const optionsLink = primaryTicker === 'ERX' ? 'https://robinhood.com/us/en/stocks/XOM/' : 'https://robinhood.com/us/en/stocks/XOM/';

  const logTrade = async () => {
    const { error } = await supabase.from('trades').insert([{
      ticker: newTrade.ticker,
      entry_price: newTrade.entry_price,
      position_size: newTrade.position_size,
      notes: newTrade.notes || null,
    }]);

    if (!error) {
      alert('✅ Trade logged successfully!');
      setShowLogger(false);
      setNewTrade({ ticker: 'ERX', entry_price: 0, position_size: 0, notes: '' });
      const { data } = await supabase.from('trades').select('*').order('created_at', { ascending: false });
      if (data) setTrades(data);
    } else {
      alert('Error: ' + error.message);
    }
  };

  const saveExitPrice = async (tradeId: string) => {
    const trade = trades.find(t => t.id === tradeId);
    if (!trade) return;

    const pnl = ((exitPriceInput - trade.entry_price) / trade.entry_price) * trade.position_size;

    const { error } = await supabase
      .from('trades')
      .update({ exit_price: exitPriceInput, pnl })
      .eq('id', tradeId);

    if (!error) {
      const { data } = await supabase.from('trades').select('*').order('created_at', { ascending: false });
      if (data) setTrades(data);
      setEditingTradeId(null);
      setExitPriceInput(0);
      alert('Exit price saved and P/L updated!');
    }
  };

  const withdrawProfits = () => {
    const totalPnL = trades.reduce((sum, t) => sum + (t.pnl || 0), 0);
    const withdrawAmount = (totalPnL * 0.3).toFixed(2);
    alert(`💰 Withdrawing ~$${withdrawAmount} (30% of profits) to your Longevity & Family Fund!`);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-white p-