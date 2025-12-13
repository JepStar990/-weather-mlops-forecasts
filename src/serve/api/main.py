from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from src.utils.db_utils import fetch_df
from src.verify.leaderboard import leaderboard

app = FastAPI(title="Weather Forecast API", version="0.1.0")

class PredictRequest(BaseModel):
    lat: float
    lon: float
    variables: list[str]
    horizons: list[int]

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/sources")
def sources():
    sql = """
    SELECT source, variable, horizon_hours, avg(rmse) AS rmse, avg(mae) AS mae, avg(mape) AS mape
    FROM errors
    WHERE valid_time >= now() - interval '7 days'
    GROUP BY source, variable, horizon_hours
    """
    df = fetch_df(sql)
    return {"data": df.to_dict(orient="records")}

@app.get("/metrics")
def metrics():
    lb = leaderboard(7)
    return {"leaderboard": lb.to_dict(orient="records")}

@app.post("/predict")
def predict(req: PredictRequest):
    # Serve our latest 'our_model' forecasts already in DB.
    sql = """
    SELECT lat, lon, variable, horizon_hours, valid_time, value, unit
    FROM forecasts
    WHERE source='our_model' AND lat=:lat AND lon=:lon
      AND variable = ANY(:variables) AND horizon_hours = ANY(:horizons)
      AND valid_time >= now() AT TIME ZONE 'utc' - interval '6 hours'
       """
    df = fetch_df(sql, {"lat": req.lat, "lon": req.lon, "variables": req.variables, "horizons": req.horizons})
    if df.empty:
        raise HTTPException(status_code=404, detail="No predictions available yet for requested parameters")
