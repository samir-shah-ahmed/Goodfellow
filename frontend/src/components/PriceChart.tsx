"use client";

import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { getTickerHistory, PricePoint } from '@/lib/api';
import { Loader2 } from 'lucide-react';

interface PriceChartProps {
    symbol: string;
}

const RANGES = [
    { label: '1D', value: '1d' },
    { label: '1W', value: '5d' },
    { label: '1M', value: '1mo' },
    { label: '6M', value: '6mo' },
    { label: '1Y', value: '1y' },
    { label: 'All', value: 'max' },
];

export function PriceChart({ symbol }: PriceChartProps) {
    const [data, setData] = useState<PricePoint[]>([]);
    const [range, setRange] = useState('1mo');
    const [maType, setMaType] = useState<'SMA' | 'EMA'>('SMA');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const history = await getTickerHistory(symbol, range);
                setData(history);
            } catch (error) {
                console.error("Failed to load history", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [symbol, range]);

    if (loading && data.length === 0) {
        return (
            <div className="h-64 flex items-center justify-center bg-white rounded-lg border border-slate-200">
                <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
            </div>
        );
    }

    // Calculate min/max for Y-axis domain to make chart look good
    const prices = data.map(d => d.price);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const padding = (maxPrice - minPrice) * 0.1;

    return (
        <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200 mb-6">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                    <h3 className="text-sm font-semibold text-slate-500">Price History</h3>
                    <div className="flex bg-slate-100 p-0.5 rounded-md">
                        <button
                            onClick={() => setMaType('SMA')}
                            className={`px-2 py-0.5 text-xs font-medium rounded-sm transition-colors ${maType === 'SMA' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                                }`}
                        >
                            SMA
                        </button>
                        <button
                            onClick={() => setMaType('EMA')}
                            className={`px-2 py-0.5 text-xs font-medium rounded-sm transition-colors ${maType === 'EMA' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                                }`}
                        >
                            EMA
                        </button>
                    </div>
                </div>
                <div className="flex gap-1 bg-slate-100 p-1 rounded-md">
                    {RANGES.map((r) => (
                        <button
                            key={r.value}
                            onClick={() => setRange(r.value)}
                            className={`px-3 py-1 text-xs font-medium rounded-sm transition-colors ${range === r.value
                                    ? 'bg-white text-slate-900 shadow-sm'
                                    : 'text-slate-500 hover:text-slate-700'
                                }`}
                        >
                            {r.label}
                        </button>
                    ))}
                </div>
            </div>

            <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.1} />
                                <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis
                            dataKey="time"
                            hide={true}
                        />
                        <YAxis
                            domain={[minPrice - padding, maxPrice + padding]}
                            orientation="right"
                            tick={{ fontSize: 12, fill: '#94a3b8' }}
                            tickFormatter={(value) => `$${value.toFixed(0)}`}
                            axisLine={false}
                            tickLine={false}
                        />
                        <Tooltip
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                            formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
                            labelStyle={{ color: '#64748b', marginBottom: '0.25rem' }}
                        />
                        <Legend
                            verticalAlign="top"
                            height={36}
                            iconType="circle"
                            formatter={(value) => <span className="text-xs font-medium text-slate-600">{value}</span>}
                        />
                        <Area
                            type="monotone"
                            dataKey="price"
                            stroke="#0ea5e9"
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#colorPrice)"
                            name="Price"
                        />
                        <Area
                            type="monotone"
                            dataKey={maType === 'SMA' ? "ma50" : "ema50"}
                            stroke="#f59e0b"
                            strokeWidth={2}
                            fill="none"
                            name={`50-Day ${maType}`}
                            connectNulls
                        />
                        <Area
                            type="monotone"
                            dataKey={maType === 'SMA' ? "ma100" : "ema100"}
                            stroke="#8b5cf6"
                            strokeWidth={2}
                            fill="none"
                            name={`100-Day ${maType}`}
                            connectNulls
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
