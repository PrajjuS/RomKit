#
# Copyright (c) 2026 PrajjuS <theprajjus@gmail.com>.
#
# This file is part of RomKit
# (see http://github.com/PrajjuS/RomKit).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from pathlib import Path
from time import sleep
from typing import Dict, List, Optional

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


class TelegramPoster:
    """Handles Telegram posting operations"""

    def __init__(self, bot_token: str):
        """
        Initialize Telegram poster

        Args:
            bot_token: Telegram bot token
        """
        self.bot = telebot.TeleBot(bot_token, parse_mode="MARKDOWN")

    def create_keyboard(
        self,
        buttons: List[List[Dict[str, str]]],
    ) -> InlineKeyboardMarkup:
        """
        Create inline keyboard from button list

        Args:
            buttons: List of button rows

        Returns:
            InlineKeyboardMarkup object
        """
        keyboard = InlineKeyboardMarkup()

        for button_row in buttons:
            keyboard_row = []
            for button in button_row:
                keyboard_row.append(
                    InlineKeyboardButton(text=button["text"], url=button["url"]),
                )
            keyboard.add(*keyboard_row)

        return keyboard

    def post(
        self,
        chat_ids: List[str],
        message: str,
        buttons: List[List[Dict[str, str]]] = None,
        banner_path: Optional[str] = None,
        delay: int = 5,
    ):
        """
        Post message to Telegram channels

        Args:
            chat_ids: List of chat IDs to post to
            message: Message text
            buttons: Optional button list
            banner_path: Optional banner image path
            delay: Delay between posts in seconds (default: 5)
        """
        keyboard = self.create_keyboard(buttons) if buttons else None

        for chat_id in chat_ids:
            try:
                if banner_path and Path(banner_path).exists():
                    with open(banner_path, "rb") as photo:
                        self.bot.send_photo(
                            chat_id=chat_id,
                            photo=photo,
                            caption=message,
                            reply_markup=keyboard,
                        )
                else:
                    self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        reply_markup=keyboard,
                        disable_web_page_preview=True,
                    )

                print(f"Posted to {chat_id}")
                sleep(delay)
            except Exception as e:
                raise RuntimeError(f"Error posting to {chat_id}: {e}")

    def post_status(
        self,
        chat_id: str,
        message: str,
        button_url: Optional[str] = None,
        button_text: str = "More Info",
    ):
        """
        Post status message to private chat

        Args:
            chat_id: Chat ID to post to
            message: Status message
            button_url: Optional button URL
            button_text: Button text (default: "More Info")
        """
        try:
            keyboard = None
            if button_url:
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton(text=button_text, url=button_url))

            self.bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )

            print(f"Posted status to {chat_id}")
        except Exception as e:
            print(f"Error posting status to {chat_id}: {e}")
