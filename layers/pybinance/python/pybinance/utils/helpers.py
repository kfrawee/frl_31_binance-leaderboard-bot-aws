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
        top_ten_data = response_json.get("data")[:10]
        
    except (HTTPError, ConnectionError, ConnectTimeout) as e:
        error_msg = f"Error while trying to getLeaderboardRank: {e}."
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

    return top_ten_data

def get_uids(data: List) -> List:
    """
    Return a list of encryptedUids (uids) from data.

    Args:
        data (List): List of traders data.
    
    Returns:
        uids (List): List of traders ids.
    """
    ids = []
    for user_data in data:
        ids.append(user_data.get("encryptedUid"))
    
    return ids

def get_trader_performance(id:str) ->Dict: 
    """
    Get trader performance data using encryptedUid (uid).

    Args:
        uid (str): Trader encryptedUid (id).
    
    Returns:
        performance_data (Dict): Trader performance data.
    """
    return {}

def get_trader_positions(id:str)-> List:
    """
    Get trader positions data using encryptedUid (uid).

    Args:
        uid (str): Trader encryptedUid (id).
    
    Returns:
        positions_data (Dict): List of trader positions data.
    """
    return []

def generate_user_data(id: str, performance_data: Dict, position_data: List)-> Dict:
    """
    Generate full trader data; performance and positions encryptedUid (uid).

    Args:
        uid (str): Trader encryptedUid (id).
        performance_data (Dict): Trader performance data.
        positions_data (Dict): List of trader positions data.
    
    Returns:
        user_data (Dict): Trader's data.
    """
    return

if __name__ == "__main__":
    top_ten_leaderboard = get_leader_board_rank()
