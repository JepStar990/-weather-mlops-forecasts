# src/jobs/job_monitor_hourly.py

from src.utils.logging_utils import get_logger
from src.verify.leaderboard import leaderboard

logger = get_logger(__name__)

def main() -> None:
    # Show leaderboard for the last 7 days
    lb = leaderboard(7)

    if lb is None or lb.empty:
        logger.info("No leaderboard data available for the last 7 days.")
        return

    # Pretty print as a table in logs without breaking strings
    logger.info("Leaderboard (last 7 days):\n%s", lb.to_string(index=False))

if __name__ == "__main__":
    main()
