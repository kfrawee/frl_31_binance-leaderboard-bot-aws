""" Helpers utils for the bot"""
import os
import traceback
from datetime import datetime
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


def extract_datetime(timestamp: int) -> str:
    """
    Extract datetime from timestamp.

    Args:
        timestamp (int): Timestamp.

    Returns:
        datetime (str): Datetime.
    """
    if not timestamp:
        return "Not available"
    if len(str(timestamp)) > 10:
        timestamp = timestamp // 1000  # remove ms

    return str(datetime.fromtimestamp(timestamp))


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
    url = "https://www.binance.com/bapi/futures/v2/public/future/leaderboard/getOtherPerformance"
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


def clean_performance_data(performance_data: Dict) -> Dict:
    """
    Clean performance data.

    Args:
        performance_data (Dict): Trader performance data.

    Returns:
        cleaned_performance_data (Dict): Cleaned trader performance data.
    """

    cleaned_performance_data = {
        "Last Trade": extract_datetime(performance_data.get("lastTradeTime")),
    }

    for data in performance_data.get("performanceRetList"):
        if data.get("periodType") == "DAILY":
            if data.get("statisticsType") == "ROI":
                cleaned_performance_data.update(
                    Daily_ROI=round(data.get("value"), 6),
                )
            elif data.get("statisticsType") == "PNL":
                cleaned_performance_data.update(
                    Daily_PNL=round(data.get("value"), 2),
                )

        elif data.get("periodType") == "WEEKLY":
            if data.get("statisticsType") == "ROI":
                cleaned_performance_data.update(
                    Weekly_ROI=round(data.get("value"), 6),
                )
            elif data.get("statisticsType") == "PNL":
                cleaned_performance_data.update(
                    Weekly_PNL=round(data.get("value"), 2),
                )

        elif data.get("periodType") == "MONTHLY":
            if data.get("statisticsType") == "ROI":
                cleaned_performance_data.update(
                    Monthly_ROI=round(data.get("value"), 6),
                )
            elif data.get("statisticsType") == "PNL":
                cleaned_performance_data.update(
                    Monthly_PNL=round(data.get("value"), 2),
                )

        elif data.get("periodType") == "ALL":
            if data.get("statisticsType") == "ROI":
                cleaned_performance_data.update(
                    All_ROI=round(data.get("value"), 6),
                )
            elif data.get("statisticsType") == "PNL":
                cleaned_performance_data.update(
                    All_PNL=round(data.get("value"), 2),
                )

    return cleaned_performance_data


def clean_positions_data(positions_data: Dict) -> Dict:
    """
    Clean positions data.

    Args:
        positions_data (Dict): Trader positions data.

    Returns:
        cleaned_positions_data (Dict): Cleaned trader positions data.
    """
    cleaned_positions_data = {
        "Last Update": extract_datetime(positions_data.get("updateTimeStamp")),
    }

    cleaned_positions_data.update(
        Positions=[
            {
                "Symbol": data.get("symbol"),
                "leverage": data.get("leverage"),
                "type": "Long" if data.get("amount") > 0 else "Short",
                "amount": data.get("amount"),
                "entryPrice": data.get("entryPrice"),
                "marketPrice": data.get("markPrice"),
                "PNL": data.get("pnl"),
                "POE": data.get("roe"),
                "datetime": extract_datetime(data.get("updateTimeStamp")),
            }
            for data in positions_data.get("otherPositionRetList")
        ]
    )

    return cleaned_positions_data


def generate_user_data(
    trader_rank: int, rank_data: Dict, performance_data: Dict, position_data: Dict
) -> Dict:
    """
    Generate full trader data; rank, performance and positions data.

    Args:
        trader_rank (int): Trader rank from 1 to 10.
        rank_data (str): Trader raw rank data.
        performance_data (Dict): Trader raw performance data.
        positions_data (Dict): List of trader raw positions data.

    Returns:
        user_data (Dict): Trader's data.
    """

    return {
        "rank": trader_rank,
        "name": rank_data.get("nickName"),
        "encryptedUid": rank_data.get("encryptedUid"),
        "performance": clean_performance_data(performance_data),
        "positions": clean_positions_data(position_data),
    }
