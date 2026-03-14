import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Flame, 
  Share2, 
  TrendingUp, 
  AlertCircle, 
  UserPlus, 
  Skull, 
  CheckCircle2,
  ChevronRight,
  ChevronLeft,
  Instagram,
  Zap
} from 'lucide-react';

const IdentityDashboard = () => {
    const [streak, setStreak] = useState(7);
    const [benchmark, setBenchmark] = useState(null);
    const [flexCards, setFlexCards] = useState([]);
    const [activeCard, setActiveCard] = useState(0);
    const [roast, setRoast] = useState('');
    const [isRoasting, setIsRoasting] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch real data from our updated APIs
        const fetchData = async () => {
            try {
                // Fetch Benchmark
                const benchRes = await fetch('/api/gamification/benchmark');
                const benchData = await benchRes.json();
                setBenchmark(benchData);

                // Fetch Flex Cards
                const cardsRes = await fetch('/api/gamification/flex-cards');
                const cardsData = await cardsRes.json();
                setFlexCards(cardsData);

                setLoading(false);
            } catch (err) {
                console.error("Error fetching data:", err);
                // Fallback for demo if backend isn't running or error
                setBenchmark({
                    peer_avg_savings: 3200,
                    user_savings: 800,
                    percentile: 32,
                    social_proof: "Join 12,000 students who aren't broke in their 20s"
                });
                setFlexCards([
                    { id: '1', title: 'Saved ₹5,000 this month', icon: '💸', color: '#00C896', subtitle: 'FinTelligent | Financial Freedom' },
                    { id: '2', title: '₹10K Emergency Fund Hit! 🎯', icon: '🛡️', color: '#7C3AED', subtitle: 'Unbreakable. FinTelligent' }
                ]);
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const handleRoast = async () => {
        setIsRoasting(true);
        setRoast('');
        try {
            const response = await fetch('/api/ai/roast', { method: 'POST' });
            if (!response.ok) throw new Error('Roast failed');
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const dataStr = line.replace('data: ', '');
                        if (dataStr === '[DONE]') break;
                        try {
                            const parsed = JSON.parse(dataStr);
                            if (parsed.content) {
                                setRoast(prev => prev + parsed.content);
                            }
                        } catch (e) {}
                    }
                }
            }
        } catch (err) {
            setRoast("Wait, you haven't even logged anything? Too scared to see the truth?");
        } finally {
            setIsRoasting(false);
        }
    };

    if (loading) return (
        <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center">
            <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1 }}>
                <Zap className="text-blue-500 w-12 h-12" />
            </motion.div>
        </div>
    );

    return (
        <div className="min-h-screen bg-[#0A0A0F] text-white font-sans p-6 md:p-12">
            <header className="max-w-4xl mx-auto mb-12 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Fin<span className="text-blue-500">Telligent</span></h1>
                    <p className="text-gray-500 text-sm mt-1">Identity: The person who has it figured out.</p>
                </div>
                <div className="flex items-center gap-2 bg-gradient-to-r from-orange-500/20 to-orange-500/10 border border-orange-500/30 px-4 py-2 rounded-full">
                    <Flame className="text-orange-500 w-5 h-5 fill-orange-500" />
                    <span className="font-bold text-orange-500">{streak} Day Streak!</span>
                </div>
            </header>

            <main className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
                
                {/* 1. STREAK CULTURE HOOK */}
                <motion.section 
                    whileHover={{ y: -5 }}
                    className="bg-[#111118] border border-gray-800 rounded-2xl p-6 relative overflow-hidden"
                >
                    <div className="absolute top-0 right-0 p-4 opacity-10">
                        <Flame size={80} className="text-orange-500" />
                    </div>
                    <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <Flame className="text-orange-500" size={18} />
                        Daily Ritual
                    </h2>
                    <div className="flex items-end gap-3 mb-6">
                        <span className="text-5xl font-extrabold text-orange-500">₹200</span>
                        <span className="text-gray-400 mb-2 font-medium">saved today</span>
                    </div>
                    <p className="text-sm text-gray-400 mb-6">
                        "Your wealth is a daily habit. Break the streak and the owl gets mad. 🦉"
                    </p>
                    <div className="flex gap-2">
                        {[1, 2, 3, 4, 5, 6, 7].map(day => (
                            <div key={day} className={`h-1.5 flex-1 rounded-full ${day <= streak ? 'bg-orange-500' : 'bg-gray-800'}`} />
                        ))}
                    </div>
                    <div className="flex justify-between mt-2 text-[10px] text-gray-600 font-bold uppercase tracking-widest">
                        <span>Mon</span>
                        <span>Today</span>
                    </div>
                </motion.section>

                {/* 2. BROKE FRIEND FOMO */}
                <motion.section 
                    whileHover={{ y: -5 }}
                    className="bg-[#111118] border border-gray-800 rounded-2xl p-6 relative overflow-hidden"
                >
                    <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <TrendingUp className="text-blue-500" size={18} />
                        How you rank
                    </h2>
                    <div className="space-y-6">
                        <div>
                            <div className="flex justify-between text-xs text-gray-500 mb-2 font-medium">
                                <span>Your average peers</span>
                                <span className="text-white">₹3,200/mo</span>
                            </div>
                            <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                                <motion.div 
                                    initial={{ width: 0 }}
                                    animate={{ width: '100%' }}
                                    className="h-full bg-blue-500/30"
                                />
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-xs text-gray-400 mb-2 font-bold">
                                <span>YOU (This month)</span>
                                <span className="text-orange-500">₹{benchmark?.user_savings || 800}</span>
                            </div>
                            <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                                <motion.div 
                                    initial={{ width: 0 }}
                                    animate={{ width: `${(benchmark?.user_savings / 3200) * 100}%` }}
                                    className="h-full bg-orange-500 shadow-[0_0_10px_#f97316]"
                                />
                            </div>
                        </div>
                        <p className="text-xs text-blue-400 bg-blue-500/10 border border-blue-500/20 p-3 rounded-lg flex items-start gap-2">
                            <AlertCircle size={14} className="shrink-0 mt-0.5" />
                            <span>{benchmark?.social_proof}</span>
                        </p>
                    </div>
                </motion.section>

                {/* 3. MONEY FLEX CARDS */}
                <motion.section 
                    whileHover={{ y: -5 }}
                    className="bg-[#111118] border border-gray-800 rounded-2xl p-6 col-span-1 md:col-span-2 overflow-hidden"
                >
                     <div className="flex justify-between items-center mb-6">
                        <h2 className="text-lg font-bold flex items-center gap-2">
                            <Share2 className="text-emerald-500" size={18} />
                            Flex your cards
                        </h2>
                        <div className="flex gap-2">
                            <button onClick={() => setActiveCard(p => Math.max(0, p-1))} className="p-1 hover:bg-gray-800 rounded text-gray-400">
                                <ChevronLeft size={20} />
                            </button>
                            <button onClick={() => setActiveCard(p => Math.min(flexCards.length-1, p+1))} className="p-1 hover:bg-gray-800 rounded text-gray-400">
                                <ChevronRight size={20} />
                            </button>
                        </div>
                    </div>
                    
                    <div className="relative">
                        <AnimatePresence mode='wait'>
                            <motion.div
                                key={activeCard}
                                initial={{ opacity: 0, scale: 0.95, x: 20 }}
                                animate={{ opacity: 1, scale: 1, x: 0 }}
                                exit={{ opacity: 0, scale: 0.95, x: -20 }}
                                className="w-full max-w-sm mx-auto aspect-[4/5] rounded-3xl p-8 flex flex-col justify-between shadow-2xl relative"
                                style={{ 
                                    background: `linear-gradient(135deg, ${flexCards[activeCard]?.color}22 0%, #000 100%)`,
                                    border: `1px solid ${flexCards[activeCard]?.color}33`,
                                    boxShadow: `0 20px 50px -12px ${flexCards[activeCard]?.color}22`
                                }}
                            >
                                <div className="text-6xl">{flexCards[activeCard]?.icon}</div>
                                <div>
                                    <h3 className="text-2xl font-black mb-2 leading-tight uppercase italic">{flexCards[activeCard]?.title}</h3>
                                    <p className="text-sm font-mono text-gray-400">{flexCards[activeCard]?.subtitle}</p>
                                </div>
                                <div className="flex justify-between items-center">
                                    <div className="text-[10px] font-mono p-2 border border-gray-800 rounded opacity-50">#FinTelligent #MoneyFlex</div>
                                    <button className="bg-white text-black p-3 rounded-full hover:scale-110 transition shadow-lg">
                                        <Instagram size={20} />
                                    </button>
                                </div>
                            </motion.div>
                        </AnimatePresence>
                    </div>
                </motion.section>

                {/* 4. AI ROAST BOT */}
                <motion.section 
                    whileHover={{ scale: 1.02 }}
                    className="bg-gradient-to-br from-[#111118] to-pink-900/10 border border-pink-500/20 rounded-2xl p-6 md:p-8"
                >
                    <div className="flex items-center gap-3 mb-6">
                        <div className="bg-pink-500 p-2 rounded-lg">
                            <Skull className="text-white" size={20} />
                        </div>
                        <h2 className="text-xl font-black italic uppercase italic">Roast Me Bot</h2>
                    </div>
                    
                    <div className="bg-black/40 border border-gray-800 p-4 rounded-xl mb-6 min-h-[80px] text-pink-400 font-mono text-sm leading-relaxed italic">
                        {isRoasting ? "Scanning your poor life choices..." : roast || "Click to hear the brutal truth about your Zomato addiction. 💀"}
                    </div>

                    <button 
                        onClick={handleRoast}
                        disabled={isRoasting}
                        className="w-full bg-pink-600 hover:bg-pink-500 disabled:bg-gray-800 py-4 rounded-xl font-bold transition-all shadow-[0_0_20px_rgba(219,39,119,0.3)] flex items-center justify-center gap-2"
                    >
                        {isRoasting ? "Roasting..." : "Brutal Honest Truth"}
                    </button>
                </motion.section>

                {/* 5. FIRST SALARY HOOK */}
                <motion.section 
                    whileHover={{ scale: 1.02 }}
                    className="bg-gradient-to-br from-[#111118] to-blue-900/10 border border-blue-500/20 rounded-2xl p-6 md:p-8"
                >
                    <div className="flex items-center gap-3 mb-6">
                        <div className="bg-blue-600 p-2 rounded-lg">
                            <UserPlus className="text-white" size={20} />
                        </div>
                        <h2 className="text-xl font-black italic uppercase italic">The First Stipend</h2>
                    </div>
                    
                    <div className="space-y-4">
                        <p className="text-sm text-gray-400">
                             "Your first ₹15,000 is the most important ₹15,000 of your life. Don't waste it on things that don't matter."
                        </p>
                        <div className="p-4 bg-black/40 border border-gray-800 rounded-xl space-y-2">
                             <div className="flex items-center gap-2 text-xs font-bold text-blue-400 uppercase">
                                <CheckCircle2 size={14} />
                                Step 1: Open FinTelligent
                             </div>
                             <div className="flex items-center gap-2 text-xs font-bold text-gray-600 uppercase">
                                <CheckCircle2 size={14} />
                                Step 2: Set the 50-30-20 rule
                             </div>
                        </div>
                        <button className="w-full bg-blue-600 hover:bg-blue-500 py-4 rounded-xl font-bold transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)]">
                            Unlock Milestone Guide
                        </button>
                    </div>
                </motion.section>

            </main>

            <footer className="max-w-4xl mx-auto mt-20 text-center text-gray-700 font-mono text-[10px] pb-12">
                MADE FOR THE GENERATION THAT'S GETTING IT FIGURED OUT.
            </footer>
        </div>
    );
};

export default IdentityDashboard;
