import re

# Minimal alias map; expand over time
ALIAS = {
    "AAPL": ["Apple", "iPhone maker", "Apple Inc."],
    "MSFT": ["Microsoft", "MSFT", "Windows maker"],
    "NVDA": ["Nvidia", "NVDA", "chipmaker Nvidia"],
}

def link_tickers(title: str, text: str, tickers: list[str]) -> list[tuple[str, float]]:
    hits = []
    blob = f"{title} {text}"
    for t in tickers:
        score = 0.0
        # direct ticker match
        if re.search(rf"\b{re.escape(t)}\b", blob, flags=re.I):
            score += 1.0
        # alias matches
        for alias in ALIAS.get(t, []):
            if re.search(rf"\b{re.escape(alias)}\b", blob, flags=re.I):
                score += 0.5
        if score > 0:
            hits.append((t, min(score, 1.5)))
    return hits