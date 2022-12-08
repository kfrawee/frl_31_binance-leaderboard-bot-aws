import os

from telegram import Bot, ParseMode
from telegram.error import RetryAfter, TimedOut

TELEGRAM_BOT_API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


class TelegramBot:
    def __init__(self) -> None:
        self.bot_client = Bot(TELEGRAM_BOT_API_KEY)
        self.chat_id = TELEGRAM_CHAT_ID
        self.emojis = {
            "ALERT": "⚠️⚠️",
            "ERROR": "❌❌",
            "SUCCESS": "✅✅",
            "ADD": "🆕✨",
            "UPDATE": "🔃✨",
            "UP": "⬆️📈",
            "DOWN": "⬇️📉",
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
            print(message_)

        if emoji in self.emojis.keys():
            message = f"{self.emojis.get(emoji)}  {message}"

        try:
            self.bot_client.send_message(
                chat_id=self.chat_id, text=f"{message}", parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print(f"Error sending message, '{e.message}'. Retrying in 1 second.")

            # maybe timeout - try to cool down
            from time import sleep

            sleep(1)
            try:
                self.bot_client.send_message(
                    chat_id=self.chat_id, text=f"{message}", parse_mode=ParseMode.HTML
                )
            except Exception as e:  # -_-
                print(f"Error sending message again, '{e.message}'.")

    def send_new_item_added(
        self, item_title: str, item_url: str, item_price: float
    ) -> None:
        """
        Send message with new item added.

        Args:
            item_title (str):  name of the item.
            item_url (str): url of the item.
            item_price (float): price of the item.
        Returns:
            None
        """
        emoji = "ADD"
        message = (
            f"<b>Hey! A new item was added!</b>\n"
            f"<a href='{item_url}'>{item_title}</a> - <b>Price:</b> ${item_price}\n"
        )

        self._send_message(message=message, emoji=emoji)

    def send_new_items_added(self, items_count: int) -> None:
        """
        Send message with new items added.

        Args:
            items_count (int):  number of newly added items.
        Returns:
            None
        """
        emoji = "ADD"
        message = f"<b>Hey! New {items_count} items were added!</b>\n"

        self._send_message(message=message, emoji=emoji, stdout=True)

    def send_new_items_updated(self, items_count: int) -> None:
        """
        Send message with new items updated.

        Args:
            items_count (int):  number of newly updated items.
        Returns:
            None
        """
        emoji = "UPDATE"
        message = f"<b>Hey! New {items_count} items were updated!</b>\n"

        self._send_message(message=message, emoji=emoji, stdout=True)

    def send_price_update(
        self,
        item_title: str,
        item_url: str,
        item_old_price: float,
        item_new_price: float,
        send_all_updates: bool,
    ) -> None:
        """
        Send message if item's price is updated.

        Args:
            item_title (str): name of the item.
            item_url (str): url of the item.
            item_old_price (float): old price of the item.
            item_new_price (float): new price of the item.
            send_all_updates (bool): Either to send all updated prices (increased or decreased) or only the decreased prices.
        Returns:
            None
        """
        if item_old_price == item_new_price:
            return
        elif item_old_price > item_new_price:
            emoji = "DOWN"
        else:
            emoji = "UP"
            if not send_all_updates:
                return

        message = (
            "<b>Hey! An item's price has been updated!</b> \n"
            f"<a href='{item_url}'>{item_title}</a> \n"
            f"<b>Old Price:</b> ${item_old_price} - <b>New Price:</b> ${item_new_price}"
        )

        self._send_message(message=message, emoji=emoji)

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
