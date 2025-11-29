import random
from typing import Dict

def get_retail_sentiment(symbol: str) -> str:
    """
    Get retail sentiment from social media (Reddit/X).
    Currently mocked for demo purposes.
    """
    # In a real implementation, this would scrape r/wallstreetbets or use Twitter API.
    # For the demo, we'll return a random sentiment weighted slightly by the symbol.
    
    sentiments = ["Bullish", "Bearish", "Neutral"]
    
    # Mock logic: Tech stocks slightly more bullish
    if symbol in ['NVDA', 'TSLA', 'AAPL', 'AMD']:
        weights = [0.6, 0.2, 0.2]
    else:
        weights = [0.33, 0.33, 0.34]
        
    return random.choices(sentiments, weights=weights, k=1)[0]
