import React, { useState, useMemo, useEffect } from 'react';
import { MOCK_DATA } from '../utils/mockData';
import StockSelector from './StockSelector';
import StatsCard from './StatsCard';
import StockChart from './StockChart';

const Dashboard = () => {
    const [selectedStock, setSelectedStock] = useState(MOCK_DATA[0]);
    const [realTimeStats, setRealTimeStats] = useState({ latest: null, high: null, low: null });

    // Memoize data to prevent unnecessary re-renders
    const currentData = useMemo(() => {
        return MOCK_DATA.find(s => s.ticker === selectedStock.ticker) || MOCK_DATA[0];
    }, [selectedStock]);

    useEffect(() => {
        const fetchData = async () => {
            const symbol = selectedStock.ticker;
            const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

            try {
                const [latestRes, highRes, lowRes] = await Promise.all([
                    fetch(`${baseUrl}/api/latest/${symbol}`),
                    fetch(`${baseUrl}/api/highest/${symbol}`),
                    fetch(`${baseUrl}/api/lowest/${symbol}`)
                ]);

                const latest = await latestRes.json();
                const high = await highRes.json();
                const low = await lowRes.json();

                // Extract date from one of the responses (assuming they are consistent)
                const tradeDate = latest.trade_date || high.trade_date || low.trade_date || null;

                setRealTimeStats({
                    latest: latest.value,
                    high: high.value,
                    low: low.value,
                    date: tradeDate
                });
            } catch (error) {
                console.error("Failed to fetch real-time data:", error);
                // Fallback or keep null to indicate no data
                setRealTimeStats({ latest: null, high: null, low: null, date: null });
            }
        };

        fetchData();
        // Set up polling every 5 seconds
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, [selectedStock]);

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8 font-sans">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header & Selector */}
                <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight text-white">Stock Dashboard</h1>
                        <p className="text-gray-400 mt-1">Real-time market insights</p>
                    </div>

                    {/* Centered Date Display */}
                    <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 hidden md:block">
                        <div className="bg-gray-800/50 backdrop-blur-sm px-4 py-2 rounded-full border border-gray-700/50">
                            <span className="text-sm text-gray-400">Date: </span>
                            <span className="text-sm font-medium text-emerald-400">
                                {realTimeStats.date || new Date().toISOString().split('T')[0]}
                            </span>
                        </div>
                    </div>

                    <StockSelector
                        stocks={MOCK_DATA}
                        selected={selectedStock}
                        onSelect={setSelectedStock}
                    />
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <StatsCard
                        label="Latest Price"
                        value={realTimeStats.latest ?? currentData.stats.latest}
                        className="bg-gradient-to-br from-gray-800 to-gray-800/50"
                    />
                    <StatsCard
                        label="Highest Price"
                        value={realTimeStats.high ?? currentData.stats.high}
                        className="bg-gradient-to-br from-gray-800 to-gray-800/50"
                    />
                    <StatsCard
                        label="Lowest Price"
                        value={realTimeStats.low ?? currentData.stats.low}
                        className="bg-gradient-to-br from-gray-800 to-gray-800/50"
                    />
                </div>

                {/* Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[500px]">
                    <StockChart
                        data={currentData.data}
                        dataKey="vwap"
                        title="VWAP (Volume Weighted Average Price)"
                        color="#8b5cf6" // Violet
                    />
                    <StockChart
                        data={currentData.data}
                        dataKey="ma"
                        title="Moving Average"
                        color="#10b981" // Emerald
                    />
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
