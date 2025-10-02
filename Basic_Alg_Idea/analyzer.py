import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

#FinBERT 
finBert="ProsusAI/finbert"
print("Loading FinBERT")
finBert_tokenizer=AutoTokenizer.from_pretrained(finBert)
finbert_model=AutoModelForSequenceClassification.from_pretrained(finBert)
print("FinBERT loaded")

#GoEmotions
Emotions="SameLowe/roberta-base-go_emotions"
print("Loading GoEmotions")
Emotions_tokenizer=AutoTokenizer.from_pretrained(Emotions)
Emotions_model=AutoModelForSequenceClassification.from_pretrained(Emotions)
print("GoEmotions loaded")

def analyze_sentiment(text: str) -> dict:
    #init stance w/FinBERT
    with torch.no_grad():
        logits=finbert_model(**finBert_tokenizer(text,padding=True,truncation=True,return_tensors='pt',max_length=512)).logits
        probabilities=torch.nn.functional.softmax(logits,dim=-1)
        stance_id=torch.nn.argmax(probabilities).item()
        confidence=probabilities[0][stance_id].item()
        labels=finbert_model.config.id2label[stance_id]
        if labels=='positive':
            stance='bullish'
        elif labels=='negative':
            stance='bearish'
        else:
            stance='neutral'
    #init emotions w/GoEmotions
    emotion_inputs=Emotions_tokenizer(text,padding=True,truncation=True,return_tensors='pt',max_length=512)
    with torch.no_grad():
        logits=Emotions_model(**emotion_inputs).logits
        probabilities=torch.nn.functional.softmax(logits,dim=-1)
        emotion_id=torch.nn.argmax(probabilities).item()
        emotion_score=probabilities[0][emotion_id].item()
        emotion_label=Emotions_model.config.id2label[emotion_id]
        result={
            "text":text,
            "stance": labels,
            "stance_confidence": round(confidence,3),
            "emotion": emotion_label,
            "emotion_confidence": round(emotion_score,3)
        }
        return result
#test
if __name__ == "__main__":
    bullish_headline = "The new normal: Wall Street says high stock valuations may be here to stay."
    bearish_headline = "Fears Britain may be edging closer to a recession have been stoked by new figures showing a drop in job openings, as well as a rise in business pessimism and public concern about the economy."
    neutral_headline = "The FED Chair Jerome Powell has announced a rate increase of 50bps."
    tricky_headline = "Despite rising costs, the company managed to meet earnings expectations."
    print(analyze_sentiment(bullish_headline))
    print(analyze_sentiment(bearish_headline))
    print(analyze_sentiment(neutral_headline))
    print(analyze_sentiment(tricky_headline))
    print(analyze_sentiment("The stock market is unpredictable."))
    print(analyze_sentiment("The economy is stable but faces challenges ahead."))
    print(analyze_sentiment("The company's profits soared despite the economic downturn.")) 
    
