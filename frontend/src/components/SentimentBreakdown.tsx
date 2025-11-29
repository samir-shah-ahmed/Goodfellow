import { Users, Building2, Briefcase } from "lucide-react";

interface SentimentBreakdownProps {
    retailSentiment?: string;
    insiderSentiment?: string;
    institutionalHolders?: string[];
}

export function SentimentBreakdown({ retailSentiment, insiderSentiment, institutionalHolders }: SentimentBreakdownProps) {
    return (
        <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200 space-y-4">
            <h3 className="text-sm font-semibold text-slate-500 mb-2">Market Sentiment</h3>

            {/* Retail */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-slate-700">
                    <Users className="h-4 w-4 text-blue-500" />
                    <span className="text-sm font-medium">Retail (Social)</span>
                </div>
                <span className={`text-sm font-bold ${retailSentiment === 'Bullish' ? 'text-emerald-600' :
                        retailSentiment === 'Bearish' ? 'text-rose-600' : 'text-slate-500'
                    }`}>
                    {retailSentiment || 'N/A'}
                </span>
            </div>

            {/* Insider */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-slate-700">
                    <Briefcase className="h-4 w-4 text-purple-500" />
                    <span className="text-sm font-medium">Insiders</span>
                </div>
                <span className="text-sm font-bold text-slate-500">
                    {insiderSentiment || 'N/A'}
                </span>
            </div>

            {/* Institutional */}
            <div className="pt-2 border-t border-slate-100">
                <div className="flex items-center gap-2 text-slate-700 mb-2">
                    <Building2 className="h-4 w-4 text-slate-500" />
                    <span className="text-sm font-medium">Top Institutions</span>
                </div>
                <ul className="text-xs text-slate-500 space-y-1 pl-6">
                    {institutionalHolders && institutionalHolders.length > 0 ? (
                        institutionalHolders.map((holder, i) => (
                            <li key={i} className="truncate">• {holder}</li>
                        ))
                    ) : (
                        <li>No data available</li>
                    )}
                </ul>
            </div>
        </div>
    );
}
