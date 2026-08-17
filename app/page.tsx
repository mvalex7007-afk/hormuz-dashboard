'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';
import { TrendingUp, TrendingDown, AlertTriangle, DollarSign, Zap, Plus, Download, Info, ExternalLink, BookOpen, X } from 'lucide-react';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

const FINNHUB_API_KEY = process.env.NEXT_PUBLIC_FINNHUB_API_KEY ?? '';

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

export default function HormuzTradeImpactPlatform() {
  const [oilPrice, setOilPrice] = useState(93.75);
  const [oilChange, setOilChange] = useState(0.3);
  const [oilHistory, setOilHistory] = useState([93.2, 93.5, 93.8, 93.6, 93.75]);
  const [signal, setSignal] = useState('STRONG ESCALATION – BLOCKADE TIGHT');
  const [action, setAction] = useState('');
  const [context, setContext] = useState('');
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [trades, setTrades] = useState<Trade[]>([]);
  const [showLogger, setShowLogger] = useState(false);
  const [editingTradeId, setEditingTradeId] = useState<string | null>(null);
  const [exitPriceInput, setExitPriceInput] = useState(0);
  const [newTrade, setNewTrade] = useState({ ticker: 'ERX', entry_price: 0, position_size: 0, notes: '' });
  const [primaryTicker, setPrimaryTicker] = useState('ERX');
  const [beginnerMode, setBeginnerMode] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);

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

    // Current context (April 17, 2026)
    setSignal('STRONG ESCALATION – BLOCKADE TIGHT');
    setAction('🚀 BUY LEVERAGED ENERGY NOW\nERX (3x Bull), UCO (2x Oil), GUSH or calls on XOM/CVX');
    setContext(`Who: Energy companies (XOM, CVX) and defense contractors (LMT, RTX)\nWhat: High chance of 5–15% oil price spike in coming days\nWhen: Signal active now – ceasefire expires ~April 22\nWhere: Strait of Hormuz (major global oil chokepoint)\nWhy: US naval blockade on Iranian ports + severely reduced shipping volume creates supply risk`);
    setPrimaryTicker('ERX');

    const loadTrades = async () => {
      const { data } = await supabase.from('trades').select('*').order('created_at', { ascending: false });
      if (data) setTrades(data);
    };
    loadTrades();

    return () => clearInterval(interval);
  }, []);

  const robinhoodLink = `https://robinhood.com/us/en/stocks/${primaryTicker}/`;

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
    <div className="min-h-screen bg-zinc-950 text-white p-6 md:p-8">
      <div className="max-w-6xl mx-auto">
        <header className="flex flex-col md:flex-row justify-between mb-10 border-b border-zinc-800 pb-6">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold flex items-center gap-3">
              <Zap className="text-yellow-400" /> HORMUZ TRADE IMPACT
            </h1>
            <p className="text-emerald-400">Real-time signals from geopolitical disruptions</p>
          </div>
          <div className="flex items-center gap-4 mt-4 md:mt-0">
            <button
              onClick={() => setBeginnerMode(!beginnerMode)}
              className={`px-5 py-2 rounded-full flex items-center gap-2 ${beginnerMode ? 'bg-emerald-600' : 'bg-zinc-700'}`}
            >
              <BookOpen className="w-4 h-4" />
              {beginnerMode ? 'Beginner Mode: ON' : 'Beginner Mode: OFF'}
            </button>
            <button
              onClick={() => setShowOnboarding(true)}
              className="px-5 py-2 rounded-full bg-zinc-800 hover:bg-zinc-700 flex items-center gap-2 text-sm"
            >
              New Here? Take the Tour
            </button>
            <div className="text-right text-sm">
              Last updated: {lastUpdated.toLocaleTimeString()}<br />
              <span className="text-amber-400">Ceasefire fragile • Expires ~Apr 22</span>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Oil Card */}
          <div className="bg-zinc-900 border border-zinc-700 rounded-3xl p-8">
            <div className="flex items-center gap-3 mb-4">
              <DollarSign className="w-8 h-8 text-yellow-400" />
              <h2 className="text-xl">WTI Crude (Real)</h2>
            </div>
            <div className={`text-6xl font-mono font-bold mb-2 ${beginnerMode ? 'text-5xl' : ''}`}>${oilPrice}</div>
            <div className={`text-3xl flex items-center gap-2 ${oilChange >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {oilChange >= 0 ? <TrendingUp /> : <TrendingDown />} {oilChange}%
            </div>
            <div className="mt-6 h-14 flex items-end gap-1">
              {oilHistory.map((p, i) => (
                <div key={i} className="bg-yellow-400 w-4 rounded-t" style={{ height: `${(p - 90) * 7}px` }} />
              ))}
            </div>
          </div>

          {/* Trade Signal Card */}
          <div className={`lg:col-span-2 rounded-3xl p-8 border-4 ${signal.includes('ESCALATION') ? 'border-red-600 bg-red-950/50' : 'border-emerald-600 bg-emerald-950/50'}`}>
            <div className="flex items-center gap-3 mb-6">
              <AlertTriangle className={`w-8 h-8 ${signal.includes('ESCALATION') ? 'text-red-400' : 'text-emerald-400'}`} />
              <h2 className="text-xl font-semibold">TRADE SIGNAL</h2>
            </div>
            
            <div className={`text-4xl font-bold mb-6 ${beginnerMode ? 'text-5xl' : ''} ${signal.includes('ESCALATION') ? 'text-red-400' : 'text-emerald-400'}`}>
              {signal}
            </div>

            <div className="bg-black/70 p-6 rounded-2xl whitespace-pre-line text-base border border-zinc-700 mb-8">
              {action}
            </div>

            <div className="bg-zinc-900/80 border border-zinc-700 rounded-2xl p-6 mb-8">
              <div className="flex items-center gap-2 mb-3 text-sm text-zinc-400">
                <Info className="w-4 h-4" /> CONTEXT & RATIONALE (5-W)
              </div>
              <p className={`text-sm leading-relaxed whitespace-pre-line ${beginnerMode ? 'text-base' : ''}`}>
                {context}
              </p>
            </div>

            <div className="text-xs bg-red-900/50 border border-red-800 p-3 rounded-xl mb-6">
              ⚠️ Risk Warning: This could lose money. Only risk what you can afford to lose.
            </div>

            <a
              href={robinhoodLink}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full bg-emerald-500 hover:bg-emerald-400 text-white font-bold py-5 rounded-2xl flex items-center justify-center gap-3 text-lg transition mb-4"
            >
              <ExternalLink className="w-6 h-6" />
              BUY {primaryTicker} ON ROBINHOOD
            </a>

            <button
              onClick={() => setShowLogger(!showLogger)}
              className="w-full bg-yellow-400 hover:bg-yellow-300 text-black font-bold py-4 rounded-2xl flex items-center justify-center gap-2 transition"
            >
              <Plus className="w-5 h-5" /> LOG THIS TRADE
            </button>
          </div>
        </div>

        {/* Trade Logger */}
        {showLogger && (
          <div className="mt-8 bg-zinc-900 border border-zinc-700 rounded-3xl p-8">
            <h3 className="text-xl mb-6">Log New Trade</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input type="text" placeholder="Ticker (e.g. ERX)" value={newTrade.ticker} onChange={(e) => setNewTrade({ ...newTrade, ticker: e.target.value })} className="bg-zinc-800 p-4 rounded-2xl text-white" />
              <input type="number" step="0.01" placeholder="Entry Price" onChange={(e) => setNewTrade({ ...newTrade, entry_price: parseFloat(e.target.value) || 0 })} className="bg-zinc-800 p-4 rounded-2xl text-white" />
              <input type="number" placeholder="Position Size ($)" onChange={(e) => setNewTrade({ ...newTrade, position_size: parseFloat(e.target.value) || 0 })} className="bg-zinc-800 p-4 rounded-2xl text-white" />
              <input type="text" placeholder="Notes (optional)" onChange={(e) => setNewTrade({ ...newTrade, notes: e.target.value })} className="bg-zinc-800 p-4 rounded-2xl text-white" />
            </div>
            <button onClick={logTrade} className="mt-6 w-full bg-emerald-500 hover:bg-emerald-400 py-4 rounded-2xl font-bold">Save to Supabase</button>
          </div>
        )}

        {/* P/L Tracker */}
        <div className="mt-12">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl">Recent Trades & P/L</h2>
            <button onClick={withdrawProfits} className="flex items-center gap-2 bg-zinc-800 hover:bg-zinc-700 px-6 py-3 rounded-2xl">
              <Download className="w-5 h-5" /> Withdraw 30% to Family Fund
            </button>
          </div>
          <div className="bg-zinc-900 border border-zinc-700 rounded-3xl overflow-hidden">
            {trades.length === 0 ? (
              <p className="p-12 text-center text-zinc-500">No trades yet. Log your first leveraged move above!</p>
            ) : (
              <div className="divide-y divide-zinc-800">
                {trades.map((trade) => (
                  <div key={trade.id} className="p-6 flex flex-col md:flex-row justify-between items-center gap-4">
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
                      <div className="flex items-center gap-4">
                        Size: ${trade.position_size} | 
                        P/L: <span className={(trade.pnl && trade.pnl > 0) ? 'text-emerald-400' : 'text-red-400'}>
                          {trade.pnl ? `$${trade.pnl.toFixed(2)}` : 'Open'}
                        </span>
                        {!trade.exit_price && (
                          <button 
                            onClick={() => { setEditingTradeId(trade.id); setExitPriceInput(trade.entry_price * 1.1); }}
                            className="text-sm bg-zinc-800 hover:bg-zinc-700 px-4 py-2 rounded-xl"
                          >
                            Set Exit Price
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="mt-12 text-center text-zinc-500 text-sm">
          Real oil prices via Finnhub • Beginner Mode makes everything simpler and larger
        </div>
      </div>

      {/* Onboarding Modal */}
      {showOnboarding && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-6">
          <div className="bg-zinc-900 rounded-3xl max-w-md w-full p-8 relative">
            <button onClick={() => setShowOnboarding(false)} className="absolute top-4 right-4 text-zinc-400 hover:text-white">
              <X className="w-6 h-6" />
            </button>
            <h2 className="text-2xl font-bold mb-6">Welcome to Hormuz Trade Impact</h2>
            <div className="space-y-6 text-sm leading-relaxed">
              <p>This is like a weather forecast for oil and energy markets. When the "storm" (blockade or low shipping) is strong, we show clear opportunities to buy leveraged energy plays.</p>
              <p>The big signal box tells you what to do right now. The "5-W" box explains who is affected, what might happen, when, where, and why — all in plain English.</p>
              <p>Click the green button to go straight to Robinhood and buy. Use "Log This Trade" to track your moves and see how well they perform over time.</p>
              <p>Only risk money you can afford to lose. Start small.</p>
            </div>
            <button 
              onClick={() => setShowOnboarding(false)}
              className="mt-8 w-full bg-emerald-500 hover:bg-emerald-400 py-4 rounded-2xl font-bold"
            >
              Got it — Let's Go!
            </button>
          </div>
        </div>
      )}
    </div>
  );
}