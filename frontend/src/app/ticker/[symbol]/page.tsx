import { getTickerBrief } from "@/lib/api";
import { SentimentBar } from "@/components/SentimentBar";
import { NewsCard } from "@/components/NewsCard";
import { SafetyBadge } from "@/components/SafetyBadge";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { VolumeCard } from "@/components/VolumeCard";
import { OptionsCard } from "@/components/OptionsCard";
import { SentimentBreakdown } from "@/components/SentimentBreakdown";
import { InsiderCard } from "@/components/InsiderCard";
import { PriceChart } from "@/components/PriceChart";

interface PageProps {
    params: {
        symbol: string;
    };
}

export default async function TickerPage({ params }: PageProps) {
    const { symbol } = await params;
    let brief;

    try {
        brief = await getTickerBrief(symbol);
    } catch (error) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-slate-50">
                <h1 className="text-2xl font-bold text-slate-800 mb-4">Error loading data for {symbol}</h1>
                <p className="text-slate-600 mb-6">Make sure the backend is running and the ticker is valid.</p>
                <Link href="/" className="text-blue-600 hover:underline flex items-center gap-2">
                    <ArrowLeft className="h-4 w-4" /> Back to Home
                </Link>
            </div>
        );
    }

    const bullishArticles = brief.articles.filter(a => a.sentiment.stance === 'positive');
    const bearishArticles = brief.articles.filter(a => a.sentiment.stance === 'negative');
    const neutralArticles = brief.articles.filter(a => a.sentiment.stance === 'neutral');

    return (
        <div className="min-h-screen bg-slate-50 pb-12">
            {/* Header */}
            <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link href="/" className="text-slate-400 hover:text-slate-600 transition-colors">
                            <ArrowLeft className="h-5 w-5" />
                        </Link>
                        <h1 className="text-2xl font-bold text-slate-900">{brief.symbol}</h1>
                        {brief.price && (
                            <div className="flex items-baseline gap-2">
                                <span className="text-xl font-semibold text-slate-900">${brief.price.toFixed(2)}</span>
                                <span className={`text-sm font-medium ${brief.change_percent && brief.change_percent >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                                    {brief.change_percent && brief.change_percent > 0 ? '+' : ''}
                                    {(brief.change_percent ? brief.change_percent * 100 : 0).toFixed(2)}%
                                </span>
                            </div>
                        )}
                        <SafetyBadge score={brief.safety_score} />
                    </div>
                    <div className="w-1/3 max-w-md hidden md:block">
                        <SentimentBar
                            bullish={brief.bullish_count}
                            bearish={brief.bearish_count}
                            neutral={brief.neutral_count}
                        />
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Mobile Sentiment Bar */}
                <div className="md:hidden mb-8">
                    <SentimentBar
                        bullish={brief.bullish_count}
                        bearish={brief.bearish_count}
                        neutral={brief.neutral_count}
                    />
                </div>

                {/* Advanced Metrics Row */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div className="md:col-span-2">
                        <PriceChart symbol={brief.symbol} />
                    </div>
                    <div className="space-y-6">
                        <VolumeCard
                            volume={brief.volume}
                            averageVolume={brief.average_volume}
                            exchange={brief.exchange}
                        />
                        <OptionsCard putCallRatio={brief.put_call_ratio} />
                    </div>
                </div>

                {/* Sentiment & Insider Row */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <SentimentBreakdown
                        retailSentiment={brief.retail_sentiment}
                        insiderSentiment={brief.insider_sentiment}
                        institutionalHolders={brief.institutional_holders}
                    />
                    <div className="md:col-span-2">
                        <InsiderCard
                            corporateInsiders={brief.corporate_insiders}
                            politicianTrades={brief.politician_trades}
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Bullish Column */}
                    <section className="space-y-4">
                        <div className="flex items-center justify-between border-b-2 border-emerald-500 pb-2">
                            <h2 className="text-lg font-bold text-slate-800">Bullish</h2>
                            <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-2 py-1 rounded-full">
                                {brief.bullish_count}
                            </span>
                        </div>
                        <div className="space-y-3">
                            {bullishArticles.map((article, i) => (
                                <NewsCard
                                    key={i}
                                    headline={article.headline}
                                    source={article.source}
                                    link={article.link}
                                    stance={article.sentiment.stance}
                                    confidence={article.sentiment.confidence}
                                />
                            ))}
                            {bullishArticles.length === 0 && (
                                <p className="text-slate-400 text-sm italic">No bullish news found.</p>
                            )}
                        </div>
                    </section>

                    {/* Neutral / Overlap Column */}
                    <section className="space-y-4">
                        <div className="flex items-center justify-between border-b-2 border-slate-300 pb-2">
                            <h2 className="text-lg font-bold text-slate-800">Neutral / Overlap</h2>
                            <span className="bg-slate-100 text-slate-800 text-xs font-bold px-2 py-1 rounded-full">
                                {brief.neutral_count}
                            </span>
                        </div>
                        <div className="space-y-3">
                            {neutralArticles.map((article, i) => (
                                <NewsCard
                                    key={i}
                                    headline={article.headline}
                                    source={article.source}
                                    link={article.link}
                                    stance={article.sentiment.stance}
                                    confidence={article.sentiment.confidence}
                                />
                            ))}
                            {neutralArticles.length === 0 && (
                                <p className="text-slate-400 text-sm italic">No neutral news found.</p>
                            )}
                        </div>
                    </section>

                    {/* Bearish Column */}
                    <section className="space-y-4">
                        <div className="flex items-center justify-between border-b-2 border-rose-500 pb-2">
                            <h2 className="text-lg font-bold text-slate-800">Bearish</h2>
                            <span className="bg-rose-100 text-rose-800 text-xs font-bold px-2 py-1 rounded-full">
                                {brief.bearish_count}
                            </span>
                        </div>
                        <div className="space-y-3">
                            {bearishArticles.map((article, i) => (
                                <NewsCard
                                    key={i}
                                    headline={article.headline}
                                    source={article.source}
                                    link={article.link}
                                    stance={article.sentiment.stance}
                                    confidence={article.sentiment.confidence}
                                />
                            ))}
                            {bearishArticles.length === 0 && (
                                <p className="text-slate-400 text-sm italic">No bearish news found.</p>
                            )}
                        </div>
                    </section>
                </div>
            </main>
        </div>
    );
}
