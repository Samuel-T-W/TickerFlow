import React from 'react';
import { cn } from '../utils/cn';

const StatsCard = ({ label, value, prefix = '$', className }) => {
    return (
        <div className={cn("bg-gray-800 p-6 rounded-2xl border border-gray-700/50 shadow-lg", className)}>
            <p className="text-gray-400 text-sm font-medium uppercase tracking-wider mb-1">{label}</p>
            <div className="flex items-baseline gap-1">
                <span className="text-2xl font-bold text-white tracking-tight">
                    {prefix}{typeof value === 'number' ? value.toFixed(2) : value}
                </span>
            </div>
        </div>
    );
};

export default StatsCard;
