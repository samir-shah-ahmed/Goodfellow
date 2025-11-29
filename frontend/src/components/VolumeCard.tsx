import { BarChart3, ArrowUp, ArrowDown } from "lucide-react";

interface VolumeCardProps {
    volume?: number;
    averageVolume?: number;
    exchange?: string;
}

export function VolumeCard({ volume, averageVolume, exchange }: VolumeCardProps) {
    if (!volume || !averageVolume) return null;

    const isHighVolume = volume > averageVolume;
    const percentDiff = Math.round(((volume - averageVolume) / averageVolume) * 100);

    return (
        <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200">
            <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-slate-500 flex items-center gap-2">
                    <BarChart3 className="h-4 w-4" /> Volume
                </h3>
                <span className="text-xs font-mono text-slate-400">{exchange}</span>
            </div>
            <div className="flex items-end gap-2">
                <span className="text-2xl font-bold text-slate-900">
                    {(volume / 1000000).toFixed(1)}M
                </span>
                <div className={`flex items-center text-sm mb-1 ${isHighVolume ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {isHighVolume ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                    {Math.abs(percentDiff)}% vs Avg
                </div>
            </div>
            <p className="text-xs text-slate-400 mt-1">
                Avg: {(averageVolume / 1000000).toFixed(1)}M
            </p>
        </div>
    );
}
