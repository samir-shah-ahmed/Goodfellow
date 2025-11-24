import { SearchForm } from "@/components/SearchForm";
import { getTrendingTickers } from "@/lib/api";
import Link from "next/link";

export default async function Home() {
    // In a real app, we'd handle errors here.
    // For MVP, we'll try to fetch, or default to empty if backend is down.
    let trending: string[] = [];
    try {
        trending = await getTrendingTickers();
    } catch (e) {
        console.error("Failed to fetch trending:", e);
        // Fallback if backend is not running during build/dev
        trending = ["AAPL", "TSLA", "NVDA", "MSFT", "AMD"];
    }

    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-6 bg-slate-50">
            <div className="w-full max-w-3xl text-center space-y-8">
                <div className="space-y-4">
                    <h1 className="text-5xl font-extrabold tracking-tight text-slate-900">
                        Balanced <span className="text-blue-600">Alpha</span>
                    </h1>
                    <p className="text-xl text-slate-600 max-w-2xl mx-auto">
                        Trade with full vision. See the Bullish, Bearish, and Neutral perspectives for every stock.
                    </p>
                </div>

                <div className="flex justify-center w-full">
                    <SearchForm />
                </div>

                <div className="pt-8">
                    <p className="text-sm font-medium text-slate-500 mb-4 uppercase tracking-wider">Trending Now</p>
                    <div className="flex flex-wrap justify-center gap-3">
                        {trending.map((ticker) => (
                            <Link
                                key={ticker}
                                href={`/ticker/${ticker}`}
                                className="px-4 py-2 bg-white rounded-lg border border-slate-200 text-slate-700 font-medium hover:border-blue-300 hover:shadow-md transition-all"
                            >
                                {ticker}
                            </Link>
                        ))}
                    </div>
                </div>
            </div>
        </main>
    );
}
