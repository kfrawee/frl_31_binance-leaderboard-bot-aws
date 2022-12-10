import os
from typing import Dict, Generator, List

import aws_lambda_powertools
from telegram import Bot, ParseMode


logger = aws_lambda_powertools.Logger(
    service=os.getenv("SERVICE_NAME", ""), level="DEBUG"
)

TELEGRAM_BOT_API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

chunk_size = 20  # chuck size to split the positions


def split_data(a_list: List, chunk_size: int = chunk_size) -> Generator:
    """
    Split a list of data into chunks of a given size.

    Args:
        a_list (List): List to split.
        chuck_size:  Size of chunks.

    Returns:
        Generator: Generator of chunks.
    """
    for i in range(0, len(a_list), chunk_size):
        yield a_list[i : i + chunk_size]


class TelegramBot:
    def __init__(self) -> None:
        self.bot_client = Bot(TELEGRAM_BOT_API_KEY)
        self.chat_id = TELEGRAM_CHAT_ID
        self.emojis = {
            "ALERT": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✅",
            "LONG": "🟢",
            "SHORT": "🔴",
            "UP": "⬆️",
            "DOWN": "⬇️",
            "+VE": "🟩",
            "-VE": "🟥",
        }
        self.rank_emoji = {
            1: "1️⃣",
            2: "2️⃣",
            3: "3️⃣",
            4: "4️⃣",
            5: "5️⃣",
            6: "6️⃣",
            7: "7️⃣",
            8: "8️⃣",
            9: "9️⃣",
            10: "🔟",
        }

    def _send_message(
        self, message: str, emoji: str = None, stdout: bool = False
    ) -> None:
        """
        Send message to telegram chat.
        Args:
            message (str): message to send.
            emoji (str): prefix emoji to use before message.
            stdout (bool): print/log statements to terminal
        Returns:
            None
        """

        if stdout:
            """Send before adding emoji to stdout and clean HTML tags"""
            import re

            pattern = re.compile(r"<.*?>")
            message_ = pattern.sub("", message)
            # print(message_)
            logger.debug(message_)

        if emoji in self.emojis.keys():
            message = f"{self.emojis.get(emoji)}  {message}"

        try:
            self.bot_client.send_message(
                chat_id=self.chat_id, text=f"{message}", parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.debug(f"Error sending message, '{e.message}'.")

    def send_summary(self, data: Dict) -> None:
        """
        Send summary of the data.

        Args:
            data (Dict): raw data to prepare and send.
        Returns:
            None
        """

        message = (
            "<u><b>📃 Top 10 Traders summary - <i>by Daily PNL</i></b></u>\n"
            f"<i>Updated On: {data.get('datetime')}\n\n</i>"
        )

        users_data = data.get("data")

        for i, user_data in enumerate(users_data):
            profile_url = f"https://www.binance.com/en/futures-activity/leaderboard/user?encryptedUid={user_data.get('encryptedUid')}"
            name = user_data.get("name")

            daily_roi = round((user_data.get("performance").get("Daily_ROI")) * 100, 2)
            if daily_roi > 0:
                daily_roi_str = self.emojis.get("+VE") + " " + str(daily_roi) + "%"
            else:
                daily_roi_str = self.emojis.get("-VE") + " " + str(daily_roi) + "%"

            daily_pnl = user_data.get("performance").get("Daily_PNL")
            if daily_pnl > 0:
                daily_pnl_str = self.emojis.get("+VE") + " $" + str(daily_pnl)
            else:
                daily_pnl_str = self.emojis.get("-VE") + " $" + str(daily_pnl)

            last_trade = user_data.get("performance").get("Last Trade")

            message += (
                f"{self.rank_emoji.get(i + 1)} "
                f"Rank: {user_data.get('rank')}"
                " - "
                f"<a href='{profile_url}'>{name}</a>\n"
                f"Daily ROI: {daily_roi_str}"
                " - "
                f"Daily PNL: {daily_pnl_str}"
                f"\n<i>Last Trade: {last_trade}</i>\n\n"
            )

        self._send_message(message=message)

    def send_details(self, data: Dict) -> None:
        """
        Send details of the data.

        Args:
            data (Dict): raw data to prepare and send.
        Returns:
            None
        """

        updated_on = data.get("datetime")
        users_data = data.get("data")
        for i, user_data in enumerate(users_data):
            profile_url = f"https://www.binance.com/en/futures-activity/leaderboard/user?encryptedUid={user_data.get('encryptedUid')}"
            name = user_data.get("name")

            message = (
                f"<b><u>📈 Trader's Details</u></b>\n"
                f"{self.rank_emoji.get(i+1)} <a href='{profile_url}'>{name}</a>"
                " - "
                f"<i>Updated On: {updated_on}\n\n</i>"
                "<u>Positions:</u>\n"
                f"<i>Binance last update: {user_data.get('positions').get('Last Update')}</i>\n\n"
            )

            user_positions = user_data.get("positions").get("Positions")

            # we can not send all details at once, split list into chunks
            if len(user_positions) > chunk_size:
                part_i = 0
                for partial_positions in split_data(user_positions):
                    message = (
                        f"<b><u>📈 Trader's Details</u></b>\n"
                        f"{self.rank_emoji.get(i+1)} <a href='{profile_url}'>{name}</a>"
                        " - "
                        f"<i>Updated On: {updated_on}\n\n</i>"
                        "<u>Positions:</u>\n"
                        f"<i>Binance last update: {user_data.get('positions').get('Last Update')}</i>\n\n"
                    )
                    message += f"<i>Too many positions to send, sending positions in {chunk_size}s</i>"
                    part_i += 1
                    message += f"<i> - <b>Part {part_i}</b>:</i>\n\n"

                    for position_data in partial_positions:
                        symbol = position_data.get("Symbol")
                        type_ = position_data.get("type")
                        leverage = position_data.get("leverage")
                        amount = position_data.get("amount", 100)
                        entry_price = round(position_data.get("entryPrice"), 3)
                        market_price = round(position_data.get("marketPrice"), 3)

                        pnl = round(position_data.get("PNL"), 2)
                        if pnl > 0:
                            pnl_str = self.emojis.get("+VE") + " " + str(pnl)
                        else:
                            pnl_str = self.emojis.get("-VE") + " " + str(pnl)

                        poe = round(position_data.get("POE") * 100, 2)
                        if poe > 0:
                            poe_str = self.emojis.get("+VE") + " " + str(poe) + "%"
                        else:
                            poe_str = self.emojis.get("-VE") + " " + str(poe) + "%"
                        datetime_ = position_data.get("datetime")

                        message += f"🪙 Symbol: {symbol}"
                        message += f" - {self.emojis.get(type_.upper())} {type_}"
                        message += f" - Leverage: {leverage}x\n"
                        message += f"💰 Amount: {amount}\n"
                        message += f"Entry Price: {entry_price} | Market Price: {market_price}\n"
                        message += f"PNL: {pnl_str} | POE: {poe_str}\n"
                        message += f"<i>Datetime: {datetime_}</i>\n\n"

                    self._send_message(message)

            else:
                for position_data in user_positions:
                    symbol = position_data.get("Symbol")
                    type_ = position_data.get("type")
                    leverage = position_data.get("leverage")
                    amount = position_data.get("amount", 100)
                    entry_price = round(position_data.get("entryPrice"), 3)
                    market_price = round(position_data.get("marketPrice"), 3)

                    pnl = round(position_data.get("PNL"), 2)
                    if pnl > 0:
                        pnl_str = self.emojis.get("+VE") + " " + str(pnl)
                    else:
                        pnl_str = self.emojis.get("-VE") + " " + str(pnl)

                    poe = round(position_data.get("POE") * 100, 2)
                    if poe > 0:
                        poe_str = self.emojis.get("+VE") + " " + str(poe) + "%"
                    else:
                        poe_str = self.emojis.get("-VE") + " " + str(poe) + "%"
                    datetime_ = position_data.get("datetime")

                    message += f"🪙 Symbol: {symbol}"
                    message += f" - {self.emojis.get(type_.upper())} {type_}"
                    message += f" - Leverage: {leverage}x\n"
                    message += f"💰 Amount: {amount}\n"
                    message += (
                        f"Entry Price: {entry_price} | Market Price: {market_price}\n"
                    )
                    message += f"PNL: {pnl_str} | POE: {poe_str}\n"
                    message += f"<i>Datetime: {datetime_}</i>\n\n"

                self._send_message(message)

    def send_alert(self, message: str) -> None:
        """
        Send an alert message.

        Args:
            message (str): message to send.
        Returns:
            None
        """
        emoji = "ALERT"
        self._send_message(message=message, emoji=emoji, stdout=True)

    def send_error(self, message: str) -> None:
        """
        Send an error message.

        Args:
            message (str): message to send.
        Returns:
            None
        """
        emoji = "ERROR"
        self._send_message(message=message, emoji=emoji, stdout=True)

    def send_success(self, message: str) -> None:
        """
        Send an success message.

        Args:
            message (str): message to send.
        Returns:
            None
        """
        emoji = "SUCCESS"
        self._send_message(message=message, emoji=emoji, stdout=True)
