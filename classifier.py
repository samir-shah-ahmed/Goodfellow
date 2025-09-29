# Import the necessary components from the transformers library
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Define the model we want to use. "ProsusAI/finbert" is a popular, well-trained choice.
MODEL_NAME = "ProsusAI/finbert"

print("Loading model and tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
print("Model and tokenizer loaded.")

def analyze_sentiment(text: str) -> tuple[str, float]:
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
    # The tokenizer prepares the text for the model.
    # `padding=True` and `truncation=True` handle texts of different lengths.
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors='pt', max_length=512)

    # 2. Get model predictions (logits)
    # We disable gradient calculation for inference, which speeds things up.
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    # 3. Convert logits to probabilities
    # A "softmax" function converts the raw model output (logits) into probabilities for each class.
    probabilities = torch.nn.functional.softmax(logits, dim=-1)

    # 4. Get the winning label and its score
    # `torch.argmax` finds the index of the highest probability.
    predicted_class_id = torch.argmax(probabilities).item()
    confidence_score = probabilities[0][predicted_class_id].item()

    # The model's labels are ['positive', 'negative', 'neutral']. We map the index to the label.
    # You might see this called `model.config.id2label` in more advanced use cases.
    labels = ['positive', 'negative', 'neutral']
    predicted_label = labels[predicted_class_id]

    return (predicted_label, confidence_score)

# --- Example Usage ---
if __name__ == "__main__":
    # Let's test it with a few examples
    bullish_headline = "The new normal: Wall Street says high stock valuations may be here to stay."
    bearish_headline = "Fears Britain may be edging closer to a recession have been stoked by new figures showing a drop in job openings, as well as a rise in business pessimism and public concern about the economy."
    neutral_headline = "The FED Chair Jerome Powell has announced a rate increase of 50bps."
    tricky_headline = "Despite rising costs, the company managed to meet earnings expectations."

    stance, confidence = analyze_sentiment(bullish_headline)
    print(f"Text: '{bullish_headline}'")
    print(f"Stance: {stance.upper()}, Confidence: {confidence:.4f}\n") # Expected: POSITIVE

    stance, confidence = analyze_sentiment(bearish_headline)
    print(f"Text: '{bearish_headline}'")
    print(f"Stance: {stance.upper()}, Confidence: {confidence:.4f}\n") # Expected: NEGATIVE
    
    stance, confidence = analyze_sentiment(neutral_headline)
    print(f"Text: '{neutral_headline}'")
    print(f"Stance: {stance.upper()}, Confidence: {confidence:.4f}\n") # Expected: NEUTRAL