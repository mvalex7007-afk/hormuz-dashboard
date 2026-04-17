'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';
import { TrendingUp, TrendingDown, DollarSign, Zap, Plus, Download, ExternalLink } from 'lucide-react';

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

export default function HormuzSimplifiedDashboard() {
  const [oilPrice, setOilPrice] = useState(93.75);
  const [oilChange, setOilChange] = useState(0.3);
  const [oilHistory, setOilHistory] = useState([93.2, 93.5, 93.8, 93.6, 93.75]);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [trades, setTrades] = useState<Trade[]>([]);
  const [showLogger, setShowLogger] = useState(false);
  const [editingTradeId, setEditingTradeId] = useState<string | null>(null);
  const [exitPriceInput, setExitPriceInput] = useState(0);
  const [newTrade, setNewTrade] = useState({ ticker: 'ERX', entry_price: 0, position_size: 0, notes: '' });
  const [quickNotes, setQuickNotes] = useState('');

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

  useEffect(() => {
    fetchOilPrice();
    const interval = setInterval(fetchOilPrice, 30000);

    const loadTrades = async () => {
      const { data } = await supabase.from('trades').select('*').order('created_at', { ascending: false });
      if (data) setTrades(data);
    };
    loadTrades();

    return () => clearInterval(interval);
  }, []);

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
    <div className="min-h-screen bg-zinc-950 text-white p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <header className="flex flex-col md:flex-row justify-between mb-10 border-b border-zinc-800 pb-6">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold flex items-center gap-3">
              <Zap className="text-yellow-400" /> HORMUZ TRADING DASHBOARD
            </h1>
            <p className="text-emerald-400">Real Oil Price • Quick Execution • Trade Logger</p>
          </div>
          <div className="text-right text-sm mt-4 md:mt-0">
            Last updated: {lastUpdated.toLocaleTimeString()}<br />
            <span className="text-amber-400">Focus on oil volatility from current conflict</span>
          </div>
        </header>

        {/* Oil Price Card */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-zinc-900 border border-zinc-700 rounded-3xl p-8">
            <div className="flex items-center gap-3 mb-6">
              <DollarSign className="w-10 h-10 text-yellow-400" />
              <h2 className="text-2xl">WTI Crude Oil (Live)</h2>
            </div>
            <div className="text-7xl font-mono font-bold mb-4">${oilPrice}</div>
            <div className={`text-4xl flex items-center gap-3 ${oilChange >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {oilChange >= 0 ? <TrendingUp /> : <TrendingDown />} {oilChange}%
            </div>
            <div className="mt-8 h-16 flex items-end gap-2">
              {oilHistory.map((p, i) => (
                <div key={i} className="bg-yellow-400 w-5 rounded-t" style={{ height: `${(p - 90) * 8}px` }} />
              ))}
            </div>
          </div>

          {/* Quick Notes */}
          <div className="bg-zinc-900 border border-zinc-700 rounded-3xl p-8">
            <h2 className="text-xl mb-4">Quick Notes / Headlines</h2>
            <textarea
              value={quickNotes}
              onChange={(e) => setQuickNotes(e.target.value)}
              placeholder="Paste latest news, ship counts, Trump statements, or CENTCOM updates here..."
              className="w-full h-48 bg-zinc-800 p-4 rounded-2xl text-sm resize-y"
            />
            <p className="text-xs text-zinc-500 mt-3">Use this to track real developments manually</p>
          </div>
        </div>

        {/* Quick Buy Buttons */}
        <div className="mb-12">
          <h2 className="text-xl mb-4">Quick Execution</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {['ERX', 'UCO', 'GUSH', 'XOM'].map((ticker) => (
              <a
                key={ticker}
                href={`https://robinhood.com/us/en/stocks/${ticker}/`}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 rounded-3xl p-6 text-center transition flex flex-col items-center"
              >
                <div className="text-3xl font-mono font-bold mb-2">{ticker}</div>
                <div className="text-emerald-400 text-sm flex items-center gap-1">
                  <ExternalLink className="w-4 h-4" /> Open in Robinhood
                </div>
              </a>
            ))}
          </div>
          <p className="text-xs text-zinc-500 mt-4 text-center">Energy & Defense plays most relevant to current volatility</p>
        </div>

        {/* Trade Logger & P/L Tracker */}
        <div className="bg-zinc-900 border border-zinc-700 rounded-3xl p-8">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl">Trade Logger & P/L</h2>
            <button
              onClick={() => setShowLogger(!showLogger)}
              className="bg-yellow-400 hover:bg-yellow-300 text-black font-bold px-6 py-3 rounded-2xl flex items-center gap-2"
            >
              <Plus className="w-5 h-5" /> Log New Trade
            </button>
          </div>

          {/* Logger Form */}
          {showLogger && (
            <div className="mb-10 bg-zinc-950 border border-zinc-800 rounded-3xl p-8">
              <h3 className="text-lg mb-6">New Trade</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input type="text" placeholder="Ticker (ERX, UCO, etc.)" value={newTrade.ticker} onChange={(e) => setNewTrade({ ...newTrade, ticker: e.target.value })} className="bg-zinc-800 p-4 rounded-2xl" />
                <input type="number" step="0.01" placeholder="Entry Price" onChange={(e) => setNewTrade({ ...newTrade, entry_price: parseFloat(e.target.value) || 0 })} className="bg-zinc-800 p-4 rounded-2xl" />
                <input type="number" placeholder="Position Size ($)" onChange={(e) => setNewTrade({ ...newTrade, position_size: parseFloat(e.target.value) || 0 })} className="bg-zinc-800 p-4 rounded-2xl" />
                <input type="text" placeholder="Notes (optional)" onChange={(e) => setNewTrade({ ...newTrade, notes: e.target.value })} className="bg-zinc-800 p-4 rounded-2xl" />
              </div>
              <button onClick={logTrade} className="mt-6 w-full bg-emerald-500 hover:bg-emerald-400 py-4 rounded-2xl font-bold">Save Trade</button>
            </div>
          )}

          {/* P/L Tracker */}
          <div>
            {trades.length === 0 ? (
              <p className="text-center py-16 text-zinc-500">No trades logged yet. Add your first one above.</p>
            ) : (
              <div className="divide-y divide-zinc-800">
                {trades.map((trade) => (
                  <div key={trade.id} className="py-6 flex flex-col md:flex-row justify-between items-center gap-4">
                    <div>
                      <span className="font-mono text-lg">{trade.ticker}</span> @ ${trade.entry_price}
                      <span className="text-xs text-zinc-500 ml-4">{new Date(trade.created_at).toLocaleDateString()}</span>
                    </div>

                    {editingTradeId === trade.id ? (
                      <div className="flex gap-3">
                        <input 
                          type="number" 
                          step="0.01" 
                          value={exitPriceInput} 
                          onChange={(e) => setExitPriceInput(parseFloat(e.target.value) || 0)}
                          className="bg-zinc-800 p-3 rounded-xl w-32"
                        />
                        <button onClick={() => saveExitPrice(trade.id)} className="bg-emerald-500 px-5 py-2 rounded-xl">Save</button>
                        <button onClick={() => setEditingTradeId(null)} className="bg-zinc-700 px-5 py-2 rounded-xl">Cancel</button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-6">
                        <div>
                          Size: ${trade.position_size} | 
                          P/L: <span className={(trade.pnl && trade.pnl > 0) ? 'text-emerald-400' : 'text-red-400'}>
                            {trade.pnl ? `$${trade.pnl.toFixed(2)}` : 'Open'}
                          </span>
                        </div>
                        {!trade.exit_price && (
                          <button 
                            onClick={() => { setEditingTradeId(trade.id); setExitPriceInput(trade.entry_price * 1.1); }}
                            className="text-sm bg-zinc-800 hover:bg-zinc-700 px-4 py-2 rounded-xl"
                          >
                            Set Exit
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <button onClick={withdrawProfits} className="mt-8 w-full bg-zinc-800 hover:bg-zinc-700 py-4 rounded-2xl flex items-center justify-center gap-2">
            <Download className="w-5 h-5" /> Withdraw 30% Profits to Longevity & Family Fund
          </button>
        </div>
      </div>
    </div>
  );
}