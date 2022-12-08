from datetime import datetime
from pybinance.utils.helpers import (
    logger,
    get_leader_board_rank,
    get_user_details,
)
from pybinance.utils.telegram_bot import TelegramBot


def handler(event, _):
    logger.info(event)
    logger.info(f"Time: {datetime.utcnow()}")
    logger.info("TEST")

    return event
