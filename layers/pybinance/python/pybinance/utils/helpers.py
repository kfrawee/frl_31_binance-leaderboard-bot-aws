""" Helpers utils for the bot"""
import os
from http import HTTPStatus
from typing import Dict

import aws_lambda_powertools
import requests
from requests.exceptions import ConnectionError, ConnectTimeout, HTTPError

from .telegram_bot import TelegramBot


logger = aws_lambda_powertools.Logger(
    service=os.getenv("SERVICE_NAME", ""), level="DEBUG"
)

telegram_bot_client = TelegramBot()

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
}


def get_leader_board_rank() -> Dict:
    """
    Get the top 10 traders, filtered by "periodType: Daily", "statisticsType: PNL".
    Args:
        None
    Returns:
        top_ten (Dict): top 10 traders.
    """

    url = "https://www.binance.com/bapi/futures/v3/public/future/leaderboard/getLeaderboardRank"
    data = {
        "tradeType": "PERPETUAL",
        "statisticsType": "PNL",
        "periodType": "DAILY",
        "isShared": True,
        "isTrader": False,
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        assert response.status_code == HTTPStatus.OK

        print(response.json())

    except (HTTPError, ConnectionError, ConnectTimeout) as e:
        logger.error(f"Error while trying to getLeaderboardRank: '{e}'.")

        return {}

    return


def get_user_details(uid: str) -> Dict:
    """
    Get user details
    """
    # https://www.binance.com/en/futures-activity/leaderboard/user?encryptedUid=F45BBD3F4C148BFCE413B0A343A1BF97
    return


if __name__ == "__main__":
    top_ten_leaderboard = get_leader_board_rank()
