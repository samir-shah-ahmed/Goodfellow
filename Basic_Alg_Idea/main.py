import argparse
from ingest import yfinance_scrape, yfinance_general_headlines
from classifier import analyze_sentiment

def run_pipeline(mode: str = "general", max_items: int = 200):
    """
    Runs the full ingestion and analysis pipeline.

    mode: "general" to use general headlines, "ticker" to use ticker-specific headlines.
    max_items: max number of headlines (for general) or tickers to process (for ticker mode).
    """
    if mode == "ticker":
        articles = yfinance_scrape(max_tickers=max_items)
    else:
        articles = yfinance_general_headlines(max_headlines=max_items)

    if not articles:
        print("No articles found. Exiting pipeline.")
        return

    print(f"\n--- Starting Analysis Pipeline ({mode}) ---")
    for article in articles:
        # unify headline/title keys from different ingest functions
        text = article.get('headline') or article.get('title')
        if not text:
            continue

        stance, confidence = analyze_sentiment(text)

        print(f"\nAnalyzing: '{text}'")
        if confidence > 0.85:
            print(f"  High Confidence -> Stance: {stance.upper()} ({confidence:.2f})")
            # database.save_processed_article(article, stance, confidence)
        else:
            print(f" Low Confidence -> Flagged for Review. (Stance: {stance.upper()}, Conf: {confidence:.2f})")
            # database.save_for_manual_review(article, stance, confidence)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ingestion -> sentiment pipeline")
    parser.add_argument("--mode", choices=["general", "ticker"], default="general",
                        help="Use 'general' for market headlines or 'ticker' for per-ticker headlines.")
    parser.add_argument("--max", type=int, default=200,
                        help="Maximum items to fetch (headlines or tickers).")
    args = parser.parse_args()

    run_pipeline(mode=args.mode, max_items=args.max)