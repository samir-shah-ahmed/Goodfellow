const API_BASE_URL = "http://localhost:8000/api/v1";

export interface TickerBrief {
    symbol: string;
    bullish_count: number;
    bearish_count: number;
    neutral_count: number;
    articles: Article[];
    safety_score: number;
    price?: number;
    change_percent?: number;
    volume?: number;
    average_volume?: number;
    exchange?: string;
    put_call_ratio?: number;
    institutional_holders?: string[];
    insider_sentiment?: string;
    retail_sentiment?: string;
    corporate_insiders?: InsiderTransaction[];
    politician_trades?: PoliticianTrade[];
}

export interface InsiderTransaction {
    holder: string;
    shares: string;
    position: string;
    date: string;
    transaction_text: string;
}

export interface PoliticianTrade {
    politician: string;
    party: string;
    date: string;
    type: string;
    amount: string;
    ticker: string;
}

export interface PricePoint {
    time: string;
    price: number;
    ma50?: number;
    ma100?: number;
    ema50?: number;
    ema100?: number;
}

export async function getTickerHistory(symbol: string, period: string = "1mo"): Promise<PricePoint[]> {
    const res = await fetch(`${API_BASE_URL}/ticker/${symbol}/history?period=${period}`);
    if (!res.ok) {
        throw new Error(`Failed to fetch history for ${symbol}`);
    }
    return res.json();
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
