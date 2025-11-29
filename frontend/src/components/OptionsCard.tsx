import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface OptionsCardProps {
    putCallRatio?: number;
}

export function OptionsCard({ putCallRatio }: OptionsCardProps) {
    if (putCallRatio === undefined || putCallRatio === null) return null;

    // PCR < 0.7 is generally Bullish (more calls)
    // PCR > 1.0 is generally Bearish (more puts)
    let sentiment = "Neutral";
    let color = "text-slate-600";
    let Icon = Minus;

    if (putCallRatio < 0.7) {
        sentiment = "Bullish Flow";
        color = "text-emerald-600";
        Icon = TrendingUp;
    } else if (putCallRatio > 1.0) {
        sentiment = "Bearish Flow";
        color = "text-rose-600";
        Icon = TrendingDown;
    }

    return (
        <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200">
            <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-slate-500">Options Flow</h3>
                <span className="text-xs text-slate-400">Put/Call Ratio</span>
            </div>
            <div className="flex items-center justify-between">
                <span className="text-2xl font-bold text-slate-900">{putCallRatio}</span>
                <div className={`flex items-center gap-1 text-sm font-medium ${color}`}>
                    <Icon className="h-4 w-4" />
                    {sentiment}
                </div>
            </div>
            <div className="w-full bg-slate-100 h-1.5 mt-3 rounded-full overflow-hidden">
                {/* Visual bar: 0.5 to 1.5 range */}
                <div
                    className={`h-full ${putCallRatio < 0.7 ? 'bg-emerald-500' : putCallRatio > 1.0 ? 'bg-rose-500' : 'bg-slate-400'}`}
                    style={{ width: `${Math.min(Math.max((putCallRatio / 2) * 100, 10), 100)}%` }}
                />
            </div>
        </div>
    );
}
