import React, { useState, useEffect, useRef } from 'react';
import { ChevronDown, Search, Check } from 'lucide-react';
import { cn } from '../utils/cn';

const StockSelector = ({ stocks, selected, onSelect }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState('');
    const [filteredStocks, setFilteredStocks] = useState(stocks);
    const wrapperRef = useRef(null);

    useEffect(() => {
        const filtered = stocks.filter(stock =>
            stock.ticker.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 5); // Limit to 5
        setFilteredStocks(filtered);
    }, [query, stocks]);

    useEffect(() => {
        function handleClickOutside(event) {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [wrapperRef]);

    return (
        <div className="relative w-64" ref={wrapperRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl text-white hover:bg-gray-750 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500/50"
            >
                <span className="font-semibold text-lg">{selected?.ticker || 'Select Stock'}</span>
                <ChevronDown className={cn("w-5 h-5 text-gray-400 transition-transform", isOpen && "transform rotate-180")} />
            </button>

            {isOpen && (
                <div className="absolute z-50 w-full mt-2 bg-gray-800 border border-gray-700 rounded-xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                    <div className="p-2 border-b border-gray-700">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search ticker..."
                                className="w-full bg-gray-900 text-white pl-9 pr-3 py-2 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                autoFocus
                            />
                        </div>
                    </div>
                    <div className="max-h-60 overflow-y-auto">
                        {filteredStocks.length === 0 ? (
                            <div className="px-4 py-3 text-sm text-gray-500 text-center">No stocks found</div>
                        ) : (
                            filteredStocks.map((stock) => (
                                <button
                                    key={stock.ticker}
                                    onClick={() => {
                                        onSelect(stock);
                                        setIsOpen(false);
                                        setQuery('');
                                    }}
                                    className={cn(
                                        "w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-700 transition-colors",
                                        selected?.ticker === stock.ticker && "bg-blue-500/10 text-blue-400"
                                    )}
                                >
                                    <span className="font-medium">{stock.ticker}</span>
                                    {selected?.ticker === stock.ticker && <Check className="w-4 h-4" />}
                                </button>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default StockSelector;
