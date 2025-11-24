const API_BASE_URL = "http://localhost:8000/api/v1";

export interface TickerBrief {
    symbol: string;
    bullish_count: number;
    bearish_count: number;
    neutral_count: number;
    articles: Article[];
    safety_score: number;
}

export interface Article {
    headline: string;
    source?: string;
    link?: string;
    ticker?: string;
    published_at?: string;
    sentiment: {
        stance: string;
        confidence: number;
    };
}

export async function getTickerBrief(symbol: string): Promise<TickerBrief> {
    const res = await fetch(`${API_BASE_URL}/ticker/${symbol}`);
    if (!res.ok) {
        throw new Error("Failed to fetch ticker brief");
    }
    return res.json();
}

export async function getTrendingTickers(): Promise<string[]> {
    const res = await fetch(`${API_BASE_URL}/trending`);
    if (!res.ok) {
        throw new Error("Failed to fetch trending tickers");
    }
    return res.json();
}
