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

import re
from datetime import datetime
from typing import Any, Dict, List, Tuple

from jinja2 import Environment


def extract_data(data: Dict[str, Any], structure: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract data from JSON based on structure

    Args:
        data: JSON data
        structure: Structure definition

    Returns:
        Flattened dictionary with extracted data
    """
    items = {}

    for key, value in structure.items():
        if key in data:
            if isinstance(value, dict):
                items.update(extract_data(data[key], value))
            elif isinstance(value, list):
                if isinstance(data[key], list):
                    for item in data[key]:
                        items.update(extract_data(item, value[0]))
                else:
                    items[key] = data[key]
            else:
                items[key] = data[key]

    return items


def filter_dateformat(timestamp, format_string="%Y-%m-%d %H:%M UTC"):
    """Format timestamp to datetime string"""
    try:
        return datetime.fromtimestamp(int(timestamp)).strftime(format_string)
    except (ValueError, TypeError):
        return str(timestamp)


def filter_filesizeformat(bytes_size):
    """Format bytes to human readable size"""
    try:
        size = float(bytes_size)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    except (ValueError, TypeError):
        return str(bytes_size)


class MessageProcessor:
    """Handles message template processing with Jinja2 and buttons"""

    def __init__(self, message_template: str):
        """
        Initialize message processor

        Args:
            message_template: Message template with {placeholder} and [[Button | URL]] syntax
        """
        self.message_template = message_template

        self.env = Environment(
            variable_start_string="{",
            variable_end_string="}",
            autoescape=False,
        )

        self.env.filters["dateformat"] = filter_dateformat
        self.env.filters["filesizeformat"] = filter_filesizeformat

    def extract_message_content(self, message: str) -> str:
        """
        Remove button syntax from message

        Args:
            message: Message with [[Button | URL]] syntax

        Returns:
            Message without button syntax
        """
        button_pattern = r"\[\[.*? \| .*?\]\]"
        return re.sub(button_pattern, "", message).strip()

    def extract_buttons(self, message: str) -> List[List[Dict[str, str]]]:
        """
        Extract buttons from message template

        Args:
            message: Message with [[Button | URL]] syntax

        Returns:
            List of button rows, each containing list of buttons with text and url
        """
        button_pattern = r"\[\[(.*?) \| (.*?)\]\]"
        buttons = []
        message_lines = message.splitlines()

        for line in message_lines:
            line_buttons = re.findall(button_pattern, line)
            if line_buttons:
                buttons.append(
                    [{"text": btn[0], "url": btn[1]} for btn in line_buttons],
                )

        return buttons

    def process_message(
        self,
        data: Dict[str, str],
    ) -> Tuple[str, List[List[Dict[str, str]]]]:
        """
        Process message template with data

        Args:
            data: Data dictionary with values for placeholders

        Returns:
            Tuple of (processed_message, button_list)
        """
        # Render template with Jinja2
        try:
            template = self.env.from_string(self.message_template)
            message = template.render(data)
        except Exception as e:
            print(f"Error rendering template: {e}")
            message = self.message_template

        # Extract buttons and clean message
        buttons = self.extract_buttons(message)
        message_content = self.extract_message_content(message)

        return message_content, buttons
