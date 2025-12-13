import json
import os
from sqlalchemy import text
from src.config import CFG
from src.utils.db_utils import db_conn

# Optional helper table to store configured locations
CREATE = """
CREATE TABLE IF NOT EXISTS locations (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  lat DOUBLE PRECISION NOT NULL,
  lon DOUBLE PRECISION NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
"""

INSERT = "INSERT INTO locations (name, lat, lon) VALUES (:name,:lat,:lon)"

def main():
    with db_conn() as conn:
        conn.execute(text(CREATE))
        for loc in CFG.TARGET_LOCATIONS:
            conn.execute(text(INSERT), {"name": loc["name            conn.execute(text(INSERT), {"name": loc["name"], "lat": loc["lat"], "lon": loc["lon"]})
    print("Seeded locations")

if __name__ == "__main__":
