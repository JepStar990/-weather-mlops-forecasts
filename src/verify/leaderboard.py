"""
Leaderboard: best source per variable & horizon over recent window.
"""
import pandas as pd
from datetime import datetime, timedelta, timezone
from src.utils.db_utils import fetch_df
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def leaderboard(days: int = 7) -> pd.DataFrame:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    sql = """
    SELECT source, variable, horizon_hours, avg(mae) AS mae, avg(rmse) AS rmse, avg(mape) AS mape, sum(n) AS n
    FROM errors
    WHERE valid_time >= :since
    GROUP BY source, variable, horizon_hours
    """
    df = fetch_df(sql, {"since": since})
    if df.empty:
        return df
    # rank per variable,horizon by RMSE then MAE
    df["rank"] = df.groupby(["variable","horizon_hours"])["rmse"].rank(method="first")
    best = df.sort_values(["variable","horizon_hours","rank"]).groupby(["variable","horizon_hours"]).head(1)
    return best[["variable","h
