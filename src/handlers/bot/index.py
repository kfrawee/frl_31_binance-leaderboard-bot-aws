from datetime import datetime
from pybinance.utils.helpers import (
    TelegramBot,
    get_leader_board_rank,
    get_user_details,
    logger,
)


def handler(event, _):
    logger.info(event)
    logger.info(f"Time: {datetime.utcnow()}")
    logger.info("TEST")

    return event
