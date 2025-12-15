"""
Build feature matrix for our model:
- Vendor forecasts for same valid_time (one column per vendor per variable)
- Lagged observations (1h, 3h, 6h) per variable
- Calendar features (hour of day, day of week)
"""
import pandas as pd
from src.utils.db_utils import fetch_df
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def get_vendor_matrix(variable: str, horizon: int) -> pd.DataFrame:
    sql = """
    SELECT lat, lon, valid_time, source, value
    FROM forecasts
    WHERE variable = :variable
      AND source IN ('open_meteo','met_no','openweather','visual_crossing','weather_gov')
    """
    df = fetch_df(sql, {"variable": variable})
    if df.empty:
        return df
    return df.pivot_table(
        index=["lat","lon","valid_time"], columns="source", values="value",).reset_index()

# def get_vendor_matrix(variable: str, horizon: int) -> pd.DataFrame:
#     sql = """
#     SELECT lat, lon, valid_time, source, value
#     FROM forecasts
#     WHERE variable = :variable
#       AND ABS(horizon_hours - :h) <= 1
#       AND source IN ('open_meteo','met_no','openweather','visual_crossing','weather_gov')
#     """
#     df = fetch_df(sql, {"variable": variable, "h": horizon})
#     if df.empty:
#         return df
#     return df.pivot_table(
#         index=["lat", "lon", "valid_time"],
#         columns="source",
#         values="value",
#     ).reset_index()

def get_obs_lags(variable: str, lags=(1,3,6)) -> pd.DataFrame:
    sql = """
    SELECT lat, lon, obs_time, value
    FROM observations
    WHERE variable = :variable
    """
    df = fetch_df(sql, {"variable": variable}).rename(columns={"obs_time":"valid_time"})
    if df.empty: return df
    out = df.copy()
    out = out.sort_values(["lat","lon","valid_time"])
    frames = [out]
    for l in lags:
        lagged = out.copy()
        lagged["valid_time"] = lagged["valid_time"] + pd.to_timedelta(l, unit="h")
        lagged = lagged.rename(columns={"value": f"obs_lag_{l}h"})
        frames.append(lagged[["lat","lon","valid_time",f"obs_lag_{l}h"]])
    base = frames[0][["lat","lon","valid_time"]].drop_duplicates()
    for fr in frames[1:]:
        base = base.merge(fr, on=["lat","lon","valid_time"], how="left")
    return base

def calendar_features(df_index: pd.DataFrame) -> pd.DataFrame:
    df = df_index.copy()
    df["hour"] = pd.to_datetime(df["valid_time"]).dt.hour
    df["dow"] = pd.to_datetime(df["valid_time"]).dt.dayofweek
    return df

def build_features(variable: str, horizon: int) -> pd.DataFrame:
    vend = get_vendor_matrix(variable, horizon)
    if vend.empty: return vend
    lags = get_obs_lags(variable)
    X = vend.merge(lags, on=["lat","lon","valid_time"], how="left")
    cal = calendar_features(X[["valid_time"]].drop_duplicates()).rename(columns={"valid_time":"valid_time"})
    X = X.merge(cal, on="valid_time", how="left")
    # attach target from observations (aligned to valid_time)
    ysql = """
    SELECT lat, lon, obs_time as valid_time, value as y
    FROM observations
    WHERE variable = :variable
    """
    ydf = fetch_df(ysql, {"variable": variable})

    if ydf.empty:
        return pd.DataFrame()

    # Create a copy of X with valid_time +/- 1h to catch slight misalignments
    X0 = X.copy()
    Xm1 = X.copy(); Xm1["valid_time"] = Xm1["valid_time"] - pd.to_timedelta(1, unit="h")
    Xp1 = X.copy(); Xp1["valid_time"] = Xp1["valid_time"] + pd.to_timedelta(1, unit="h")

    def join_y(Xcand: pd.DataFrame) -> pd.DataFrame:
        return Xcand.merge(
            ydf.rename(columns={"obs_time": "valid_time"}),
            on=["lat", "lon", "valid_time"],
            how="left",
        )

    Xy = join_y(X0)
    # fill missing y from the +/-1h candidates
    Xy_m1 = join_y(Xm1).rename(columns={"y": "y_m1"})
    Xy_p1 = join_y(Xp1).rename(columns={"y": "y_p1"})

    Xy = Xy.merge(Xy_m1[["lat", "lon", "valid_time", "y_m1"]], on=["lat", "lon", "valid_time"], how="left")
    Xy = Xy.merge(Xy_p1[["lat", "lon", "valid_time", "y_p1"]], on=["lat", "lon", "valid_time"], how="left")

    # Prefer exact match; fallback to -1h, then +1h
    Xy["y"] = Xy["y"].fillna(Xy["y_m1"]).fillna(Xy["y_p1"])
    Xy = Xy.drop(columns=["y_m1", "y_p1"])
    return Xy
