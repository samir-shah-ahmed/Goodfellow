from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Tuple

# Define the model we want to use. "ProsusAI/finbert" is a popular, well-trained choice.
MODEL_NAME = "ProsusAI/finbert"

print("Loading model and tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
print("Model and tokenizer loaded.")

def analyze_sentiment(text: str) -> Tuple[str, float]:
    """
    Analyzes the sentiment of a given financial text.

    Args:
        text: The financial news article or headline to analyze.

    Returns:
        A tuple containing the predicted sentiment ('positive', 'negative', 'neutral')
        and the confidence score (a float between 0 and 1).
    """
    if not text or not isinstance(text, str):
        return ("invalid_input", 0.0)

    # 1. Tokenize the input text
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors='pt', max_length=512)

    # 2. Get model predictions (logits)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    # 3. Convert logits to probabilities
    probabilities = torch.nn.functional.softmax(logits, dim=-1)

    # 4. Get the winning label and its score
    predicted_class_id = torch.argmax(probabilities).item()
    confidence_score = probabilities[0][predicted_class_id].item()

    labels = ['positive', 'negative', 'neutral']
    predicted_label = labels[predicted_class_id]

    return (predicted_label, confidence_score)
