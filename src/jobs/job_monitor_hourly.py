"""
Recompute leaderboard and (optionally) cache for dashboard.
"""
from src.verify.leaderboard import leaderboard
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    lb = leaderboard(7)
    logger.info("Leaderboard:\
