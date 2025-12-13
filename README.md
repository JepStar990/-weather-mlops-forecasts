# Weather MLOps: Multi-API Forecast Verification + Ensemble (Zero Budget)

An end‑to‑end, production‑grade (free‑tier) MLOps system to ingest hourly weather forecasts from multiple providers, ingest observed weather, measure forecast error per source/horizon/variable, train and promote our own ensemble model, and serve predictions via FastAPI with a Gradio verification dashboard.

All pipelines run on **free tiers**:
- **Data**: Open‑Meteo (no key), MET Norway Locationforecast (User‑Agent), weather.gov (US NWS), OpenWeather One Call 3.0 (first 1,000 calls/day free), Visual Crossing (≈1,000 records/day free), Meteostat Python library (observations).
- **Warehouse**: Neon Serverless Postgres (free).
- **Experiment Tracking**: DagsHub MLflow-compatible (free for public).
- **Serving**: Deta Space (FastAPI), Hugging Face Spaces (Gradio).
- **Orchestration**: GitHub Actions (UTC; off‑hour cron to avoid congestion).

> **South Africa first**: Includes multiple SA locations out-of-the-box (Johannesburg, Cape Town, Durban, Pretoria, Gqeberha, Bloemfontein, Polokwane, Mbombela, East London). Add more anytime via `TARGET_LOCATIONS`.

---

## Overview
