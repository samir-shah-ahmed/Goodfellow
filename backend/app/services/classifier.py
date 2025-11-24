import requests
import os
from typing import Tuple

# Use Hugging Face Inference API
API_URL = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
# In a real app, use an env var: os.environ.get("HF_API_KEY")
# For this demo, we'll use the public free tier which doesn't strictly require a key but is rate limited.
HEADERS = {"Authorization": f"Bearer {os.environ.get('HF_API_KEY', '')}"}

def analyze_sentiment(text: str) -> Tuple[str, float]:
    """
    Analyzes the sentiment of a given financial text using Hugging Face API.

    Args:
        text: The financial news article or headline to analyze.

    Returns:
        A tuple containing the predicted sentiment ('positive', 'negative', 'neutral')
        and the confidence score (a float between 0 and 1).
    """
    if not text or not isinstance(text, str):
        return ("invalid_input", 0.0)

    try:
        payload = {"inputs": text}
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=5)
        
        # Check if model is loading
        if response.status_code == 503:
             # Fallback if model is cold/loading
             print("Model is loading, returning neutral fallback")
             return ("neutral", 0.5)

        response.raise_for_status()
        data = response.json()

        # API returns a list of lists of dicts: [[{'label': 'positive', 'score': 0.9}, ...]]
        # or sometimes just a list of dicts depending on the model pipeline.
        # FinBERT usually returns: [[{'label': 'positive', 'score': 0.95}, {'label': 'negative', 'score': 0.02}, ...]]
        
        if isinstance(data, list) and len(data) > 0:
            scores = data[0] # Get the first prediction set
            if isinstance(scores, list):
                # Find the label with the highest score
                best_score = max(scores, key=lambda x: x['score'])
                return (best_score['label'], best_score['score'])
                
        return ("neutral", 0.0)

    except Exception as e:
        print(f"Sentiment analysis failed: {e}")
        # Fail gracefully to neutral
        return ("neutral", 0.0)
