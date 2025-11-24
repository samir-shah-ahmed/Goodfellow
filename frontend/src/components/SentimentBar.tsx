import { cn } from "@/lib/utils";

interface SentimentBarProps {
    bullish: number;
    bearish: number;
    neutral: number;
    className?: string;
}

export function SentimentBar({ bullish, bearish, neutral, className }: SentimentBarProps) {
    const total = bullish + bearish + neutral;
    if (total === 0) return null;

    const bullPct = (bullish / total) * 100;
    const bearPct = (bearish / total) * 100;
    const neutPct = (neutral / total) * 100;

    return (
        <div className={cn("flex h-4 w-full overflow-hidden rounded-full", className)}>
            {bullish > 0 && (
                <div
                    style={{ width: `${bullPct}%` }}
                    className="bg-emerald-500 transition-all duration-500"
                    title={`Bullish: ${bullish} (${bullPct.toFixed(1)}%)`}
                />
            )}
            {neutral > 0 && (
                <div
                    style={{ width: `${neutPct}%` }}
                    className="bg-gray-400 transition-all duration-500"
                    title={`Neutral: ${neutral} (${neutPct.toFixed(1)}%)`}
                />
            )}
            {bearish > 0 && (
                <div
                    style={{ width: `${bearPct}%` }}
                    className="bg-rose-500 transition-all duration-500"
                    title={`Bearish: ${bearish} (${bearPct.toFixed(1)}%)`}
                />
            )}
        </div>
    );
}
