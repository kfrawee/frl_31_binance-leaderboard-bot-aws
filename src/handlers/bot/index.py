import os
import asyncio
from datetime import datetime
from operator import itemgetter
from typing import Dict, List

import aws_lambda_powertools
import nest_asyncio

from pybinance.utils.helpers import (
    generate_user_data,
    get_encrypted_uids,
    get_leader_board_rank,
    get_trader_performance,
    get_trader_positions,
)
from pybinance.utils.telegram_bot import TelegramBot


logger = aws_lambda_powertools.Logger(
    service=os.getenv("SERVICE_NAME", ""), level="DEBUG"
)
nest_asyncio.apply()

users_data = []
Telegram_bot_client = TelegramBot()


def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)

    return wrapped


@background
def parallel_f(i: int, trader_rank_data: Dict, uids: List):
    user_rank = i + 1
    logger.info(f"#Processing user {str(user_rank).zfill(2)} uid: {uids[i]}")

    performance_data = get_trader_performance(uids[i])
    positions_data = get_trader_positions(uids[i])
    user_data = generate_user_data(
        user_rank, trader_rank_data, performance_data, positions_data
    )

    users_data.append(user_data)


def handler(event, _):
    start_datetime = datetime.utcnow()

    rank_raw_data = get_leader_board_rank()
    uids = get_encrypted_uids(rank_raw_data)

    loop = asyncio.get_event_loop()
    looper = asyncio.gather(
        *[
            parallel_f(i, trader_rank_data, uids)
            for i, trader_rank_data in enumerate(rank_raw_data)
        ]
    )
    loop.run_until_complete(looper)

    # sort the list by rank
    sorted_users_data = sorted(users_data, key=itemgetter("rank"))

    results = {"data": sorted_users_data, "datetime": str(start_datetime)}

    logger.debug(
        f"Elapsed time #before_telegram: {(datetime.utcnow() - start_datetime).total_seconds()}"
    )

    # Report to telegram
    # 1. summary report
    Telegram_bot_client.send_summary(results)
    # 2. detailed report for each user
    Telegram_bot_client.send_details(results)

    logger.debug(
        f"Elapsed time #total: {(datetime.utcnow() - start_datetime).total_seconds()}"
    )
    return event
