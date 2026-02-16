import React, { useState } from 'react';
import { BookOpen, AlertTriangle, Smartphone, CreditCard, Percent, ArrowRight, CheckCircle } from 'lucide-react';

const FinancialCoach = () => {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('http://localhost:8000/ai/financial-literacy', {
                method: 'POST'
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to fetch data');
            }

            const result = await response.json();
            setData(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (!data && !loading && !error) {
        return (
            <div className="flex flex-col items-center justify-center p-12 bg-white rounded-2xl shadow-xl max-w-2xl mx-auto border border-blue-100">
                <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mb-6">
                    <BookOpen size={40} className="text-blue-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Ready to level up your finances?</h2>
                <p className="text-gray-500 text-center mb-8 max-w-md">
                    Get personalized, India-specific financial advice powered by local AI. No cloud APIs, completely private.
                </p>
                <button
                    onClick={fetchData}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-8 rounded-xl transition-all shadow-lg hover:shadow-blue-200"
                >
                    Start Coaching Session
                    <ArrowRight size={20} />
                </button>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center p-20">
                <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-6"></div>
                <p className="text-lg font-medium text-gray-600 animate-pulse">Consulting the AI Coach...</p>
                <p className="text-sm text-gray-400 mt-2">Running locally on Ollama</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="max-w-2xl mx-auto p-6 bg-red-50 rounded-xl border border-red-100 text-center">
                <AlertTriangle className="mx-auto text-red-500 mb-4" size={48} />
                <h3 className="text-xl font-bold text-red-800 mb-2">Connection Error</h3>
                <p className="text-red-600 mb-6">{error}</p>
                <button
                    onClick={fetchData}
                    className="bg-white border border-red-200 text-red-600 hover:bg-red-50 px-6 py-2 rounded-lg font-medium transition-colors"
                >
                    Try Again
                </button>
            </div>
        );
    }

    const sections = [
        { key: 'sip', title: 'SIP (Systematic Investment Plan)', icon: <BookOpen className="text-green-500" />, color: 'bg-green-50', border: 'border-green-100' },
        { key: 'emergency_fund', title: 'Emergency Fund', icon: <AlertTriangle className="text-orange-500" />, color: 'bg-orange-50', border: 'border-orange-100' },
        { key: 'upi_overspending', title: 'UPI Overspending', icon: <Smartphone className="text-purple-500" />, color: 'bg-purple-50', border: 'border-purple-100' },
        { key: 'credit_card', title: 'Credit Card Traps', icon: <CreditCard className="text-red-500" />, color: 'bg-red-50', border: 'border-red-100' },
        { key: 'emi', title: 'EMI Culture', icon: <Percent className="text-blue-500" />, color: 'bg-blue-50', border: 'border-blue-100' },
    ];

    return (
        <div className="max-w-5xl mx-auto space-y-8">
            <div className="flex justify-between items-center mb-8">
                <h2 className="text-2xl font-bold text-gray-800">Your Personal Plan</h2>
                <button onClick={fetchData} className="text-blue-600 font-medium hover:underline text-sm">
                    Refresh Advice
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {sections.map(({ key, title, icon, color, border }) => (
                    data[key] && (
                        <div key={key} className={`bg-white rounded-2xl p-6 shadow-sm border ${border} hover:shadow-md transition-shadow`}>
                            <div className={`w-12 h-12 ${color} rounded-xl flex items-center justify-center mb-4`}>
                                {icon}
                            </div>
                            <h3 className="text-lg font-bold text-gray-900 mb-3">{title}</h3>
                            <p className="text-gray-600 text-sm leading-relaxed mb-4">
                                {data[key].explanation}
                            </p>
                            <div className="bg-gray-50 rounded-lg p-3 mb-4">
                                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Example</p>
                                <p className="text-sm text-gray-800 italic">"{data[key].example}"</p>
                            </div>
                            <div className="flex items-start gap-3 mt-auto pt-4 border-t border-gray-100">
                                <CheckCircle size={18} className="text-blue-500 mt-0.5 shrink-0" />
                                <div>
                                    <p className="text-xs font-semibold text-blue-600 uppercase tracking-wide mb-1">Action Habit</p>
                                    <p className="text-sm font-medium text-gray-900">{data[key].habit_action}</p>
                                </div>
                            </div>
                        </div>
                    )
                ))}
            </div>
        </div>
    );
};

export default FinancialCoach;
