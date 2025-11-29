import { User, Landmark, TrendingUp, TrendingDown } from "lucide-react";
import { InsiderTransaction, PoliticianTrade } from "@/lib/api";

interface InsiderCardProps {
    corporateInsiders?: InsiderTransaction[];
    politicianTrades?: PoliticianTrade[];
}

export function InsiderCard({ corporateInsiders, politicianTrades }: InsiderCardProps) {
    const hasCorp = corporateInsiders && corporateInsiders.length > 0;
    const hasPol = politicianTrades && politicianTrades.length > 0;

    if (!hasCorp && !hasPol) return null;

    return (
        <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200 space-y-6">
            {/* Politician Trades */}
            {hasPol && (
                <div>
                    <div className="flex items-center gap-2 mb-3">
                        <Landmark className="h-4 w-4 text-purple-600" />
                        <h3 className="text-sm font-semibold text-slate-700">Politician Trading</h3>
                    </div>
                    <div className="space-y-3">
                        {politicianTrades!.map((trade, i) => (
                            <div key={i} className="flex items-start justify-between text-sm border-l-2 pl-3 border-purple-200">
                                <div>
                                    <div className="font-medium text-slate-900">
                                        {trade.politician} <span className="text-xs text-slate-400">({trade.party})</span>
                                    </div>
                                    <div className="text-xs text-slate-500">{trade.date}</div>
                                </div>
                                <div className="text-right">
                                    <div className={`font-bold ${trade.type === 'Purchase' ? 'text-emerald-600' : 'text-rose-600'}`}>
                                        {trade.type}
                                    </div>
                                    <div className="text-xs text-slate-500">{trade.amount}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {hasPol && hasCorp && <div className="border-t border-slate-100" />}

            {/* Corporate Insiders */}
            {hasCorp && (
                <div>
                    <div className="flex items-center gap-2 mb-3">
                        <User className="h-4 w-4 text-blue-600" />
                        <h3 className="text-sm font-semibold text-slate-700">Corporate Insiders</h3>
                    </div>
                    <div className="space-y-3">
                        {corporateInsiders!.map((trade, i) => (
                            <div key={i} className="flex items-start justify-between text-sm">
                                <div>
                                    <div className="font-medium text-slate-900 truncate max-w-[150px]" title={trade.holder}>
                                        {trade.holder}
                                    </div>
                                    <div className="text-xs text-slate-500">{trade.date}</div>
                                </div>
                                <div className="text-right">
                                    <div className="font-mono text-slate-700">{trade.shares} shares</div>
                                    <div className="text-xs text-slate-400">{trade.transaction_text}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
