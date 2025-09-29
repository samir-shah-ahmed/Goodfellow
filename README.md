# Balanced Alpha 📈

**Trade with full vision.**

Balanced Alpha is an algorithm + AI hybrid platform designed to give investors **balanced, bias-aware insights** on the stock market.  
Instead of drowning in one-sided hype, Balanced Alpha surfaces **Bullish**, **Bearish**, and **Shared Facts/Overlap** perspectives for each ticker—along with a transparent **Safety-of-Hold** risk signal.

---

## 🚀 Vision
Current algorithms reward outrage, hype, and echo chambers.  
Balanced Alpha flips the script: we optimize for **clarity, trust, and full-vision decision making**.

- **Balanced Feeds** → Stance diversity (Bull | Bear | Overlap).  
- **Bias Tags** → Fundamentals, Technicals, Macro, Geopolitics, ESG, etc.  
- **Safety-of-Hold (SoH)** → Transparent, calibrated risk color bands.  
- **Ethics Filters** → Focus on companies aligned with user-defined values.  
- **Sandbox Simulator** → Replay scenarios & stress test portfolios.

---

## 🧠 Core Idea
- **90% Algorithm:** Efficient stance & bias classifiers, risk models, feed optimization.  
- **10% AI:** Used selectively (LLM arbitration) when classifiers are uncertain or text is noisy.  
- **Explainability First:** Every label & risk score shows *why* it was produced.

---

## 📂 Repo Structure
- **Coming Soon!**

---

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI, Postgres, Redis, Prefect/Celery, Docker  
- **NLP:** sentence-transformers, FinBERT, LightGBM/XGBoost, selective LLM (OpenAI/Claude)  
- **Frontend:** Next.js, React, Tailwind, Vercel  
- **Infra:** Railway/Render/Fly.io, S3/GCS for raw text storage  
- **Monitoring:** MLflow, Weights & Biases, Grafana  

---

## 📊 Data Flow
1. **Ingest & Normalize** → RSS/APIs, company PR, SEC filings.  
2. **Ticker/Event Linking** → symbol dictionary + embeddings.  
3. **Fast Classifiers** → stance, bias tags, claim templates.  
4. **Confidence Router** → if low-confidence → route to LLM arbitration.  
5. **Balanced Feed Builder** → maximize stance diversity + overlap facts.  
6. **Safety-of-Hold Model** → risk bands (Green/Yellow/Red) + factor breakdown.  
7. **Delivery** → Web app, API, alerts, daily digest email.  

---

## 🔑 Features (MVP)
- **Ticker Briefs**: Bull | Bear | Overlap feed with bias chips.  
- **Watchlists & Alerts**: Follow tickers, receive balanced briefs daily.  
- **Safety-of-Hold**: Simple calibrated risk band for each ticker.  
- **Why am I seeing this?**: Transparent explanations with evidence spans.  

---

## 💡 Longer-Term Features
- **Ethics Filters** (user-defined ESG/values).  
- **Sandbox Trading Simulator** (historical replay + scenario shocks).  
- **Enterprise Dashboard** (compliance exports, polarization analytics).  
- **Data/API Licensing** (Polarization Index, Stance Dispersion metrics).  

---

## 🗓️ Development Roadmap
**Week 1–2**
- Repo scaffold, ingestion pipeline, ticker linking.
- Draft annotation guide; label 1k doc→ticker pairs.

**Week 3–4**
- Baseline classifiers + confidence router.
- Add selective LLM arbitration + caching.
- MVP “Ticker Brief” UI + daily digest for alpha users.

**Week 5–6**
- Balanced Feed selector.
- Safety-of-Hold v0 (basic calibrated model).
- Per-card explainability + source diversity meter.

**Week 7–8**
- Watchlists, alerts, pro/free pricing gates.
- Ethics filter v1 (rules-based).
- Soft launch to waitlist.

---

## ⚖️ Compliance & Trust
- Prominent disclaimer: **Educational only, not investment advice.**  
- Model cards + calibration charts.  
- Monthly bias audit report (source mix, stance balance).  

---

## 📬 Getting Started (Dev)
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.api:app --reload

# Frontend
cd frontend
npm install
npm run dev
