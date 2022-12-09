""" Helpers utils for the bot"""
import os
import traceback
from http import HTTPStatus
from typing import Optional, Dict, List

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


def get_leader_board_rank() -> Optional[List[Dict]]:
    """
    Get the top 10 traders data, filtered by "periodType: Daily", "statisticsType: PNL".

    Args:
        None

    Returns:
        top_ten (List): List of top 10 traders data.
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

        response_json = response.json()
        data = response_json.get("data")

    except (HTTPError, ConnectionError, ConnectTimeout) as e:
        error_msg = f"Error while trying to connect to Binance API: {e}"
        logger.error(error_msg)
        telegram_bot_client.send_error(error_msg)
        return

    except AssertionError:
        error_msg = f"Binance responded with statusCode: {response.status_code}"
        logger.error(error_msg)
        telegram_bot_client.send_error(error_msg)
        return

    except Exception as e:
        error_msg = f"Unexpected error: {e}. Traceback: {traceback.format_exc()}"
        logger.error(error_msg)
        telegram_bot_client.send_error(error_msg)
        return

    return data[:10]  # only top 10


def get_encrypted_uids(data: List) -> List:
    """
    Return a list of encryptedUids (uids) from data.

    Args:
        data (List): List of traders data.

    Returns:
        encryptedUids (List): List of traders ids.
    """
    return [user_data.get("encryptedUid") for user_data in data]


def get_trader_performance(encryptedUid: str) -> Dict:
    """
    Get trader performance data using encryptedUid.

    Args:
        encryptedUid (str): Trader encryptedUid (id).

    Returns:
        performance_data (Dict): Trader performance data.
    """
    url = "https://www.binance.com/bapi/futures/v3/public/future/leaderboard/getLeaderboardRank"
    request_body = {
        "encryptedUid": encryptedUid,
        "tradeType": "PERPETUAL",
    }

    try:
        response = requests.post(url, json=request_body, headers=headers)
        assert response.status_code == HTTPStatus.OK

        response_json = response.json()
        date = response_json.get("data")

    except (HTTPError, ConnectionError, ConnectTimeout) as e:
        error_msg = f"Error while trying to connect to Binance API: {e}"
        logger.error(error_msg)
        telegram_bot_client.send_error(error_msg)
        return

    except AssertionError:
        error_msg = f"Binance responded with statusCode: {response.status_code}"
        logger.error(error_msg)
        telegram_bot_client.send_error(error_msg)
        return

    except Exception as e:
        error_msg = f"Unexpected error: {e}. Traceback: {traceback.format_exc()}"
        logger.error(error_msg)
        telegram_bot_client.send_error(error_msg)
        return
    return date


def get_trader_positions(encryptedUid: str) -> Dict:
    """
    Get trader positions data using encryptedUid (uid).

    Args:
        encryptedUid (str): Trader encryptedUid (id).

    Returns:
        positions_data (Dict): Trader positions data.
    """
    url = "https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getOtherPosition"
    request_body = {
        "encryptedUid": encryptedUid,
        "tradeType": "PERPETUAL",
    }

    try:
        response = requests.post(url, json=request_body, headers=headers)
        assert response.status_code == HTTPStatus.OK

        response_json = response.json()
        date = response_json.get("data")

    except (HTTPError, ConnectionError, ConnectTimeout) as e:
        error_msg = f"Error while trying to connect to Binance API: {e}"
        logger.error(error_msg)
        telegram_bot_client.send_error(error_msg)
        return

    except AssertionError:
        error_msg = f"Binance responded with statusCode: {response.status_code}"
        logger.error(error_msg)
        telegram_bot_client.send_error(error_msg)
        return

    except Exception as e:
        error_msg = f"Unexpected error: {e}. Traceback: {traceback.format_exc()}"
        logger.error(error_msg)
        telegram_bot_client.send_error(error_msg)
        return
    return date


def generate_user_data(rank_data: Dict, performance_data: Dict, position_data: Dict) -> Dict:
    """
    Generate full trader data; rank, performance and positions data.

    Args:
        rank_data (str): Trader rank data.
        performance_data (Dict): Trader performance data.
        positions_data (Dict): List of trader positions data.

    Returns:
        user_data (Dict): Trader's data.
    """
    # amount +ve short
    # amount -ve long

    return


if __name__ == "__main__":
    top_ten_leaderboard = get_leader_board_rank()
