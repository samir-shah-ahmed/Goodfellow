from readability import Document as ReadabilityDoc
from bs4 import BeautifulSoup

def clean_html(html: str) -> str:
    try:
        doc = ReadabilityDoc(html)
        content_html = doc.summary()
    except Exception:
        content_html = html
    soup = BeautifulSoup(content_html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return text