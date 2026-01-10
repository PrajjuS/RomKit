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

import datetime
from pathlib import Path
from typing import Any, Dict, List

from NoobStuffs.libtelegraph import TelegraphHelper

from ..utils import MessageProcessor, TelegramPoster, VersionChecker
from .config import OrgPosterConfig
from .id_tracker import IDTracker
from .json_reader import JSONReader
from .placeholders import PlaceholderProcessor


class OrgPoster:
    """
    Automated ROM posting for organization repositories
    Handles multi-device OTA repos with JSON tracking
    """

    def __init__(self, config_path: str = "romkit.yaml"):
        """
        Initialize OrgPoster with config file

        Args:
            config_path: Path to YAML configuration file
        """
        self.config = OrgPosterConfig(config_path)

        placeholder_processor = PlaceholderProcessor(self.config)

        self.telegram = TelegramPoster(self.config.bot_token)

        self.message_processor = MessageProcessor(self.config.message_template)

        self.json_reader = JSONReader(
            self.config.json_directories,
            self.config.device_json_structure,
            placeholder_processor,
        )

        self.id_tracker = IDTracker(
            self.config.file_ids_path,
            self.json_reader,
            self.config.id_field,
            self.config.device_json_structure,
        )

        self.version_checker = None
        if all(
            [
                self.config.version_repo,
                self.config.version_file,
                self.config.version_template,
            ],
        ):
            self.version_checker = VersionChecker(
                self.config.gh_token,
                self.config.version_repo,
                self.config.version_file,
                self.config.version_template,
            )

        self.telegraph = None
        if self.config.priv_chat_id:
            self.telegraph = TelegraphHelper(
                author_name=f"{self.config.rom_name} Bot",
                author_url=f"https://t.me/{self.config.bot_username}",
                domain="graph.org",
            )

    def post_update(self, device_info: Dict[str, Any]):
        """
        Post update to Telegram channels

        Args:
            device_info: Device information dictionary
        """
        message, buttons = self.message_processor.process_message(device_info)

        self.telegram.post(
            self.config.chat_ids,
            message,
            buttons,
            self.config.banner_path,
        )

    def generate_commit_message(self, updated_devices: List[Dict[str, Any]]) -> str:
        """
        Generate commit message for updated files

        Args:
            updated_devices: List of updated device info

        Returns:
            Commit message string
        """
        message = f"{self.config.rom_name}: Update new IDs and push OTA [BOT]\n\n"
        message += "Data for following device(s) were changed:\n"

        for device in updated_devices:
            device_name = device.get(self.config.device_name_field, "Unknown")
            message += f"- {device_name} ({device['bot_codename']})\n"

        return message

    def post_status_message(self):
        """Post monthly update status to private chat"""
        if not self.config.priv_chat_id or not self.version_checker:
            return

        try:
            current_version = self.version_checker.get_version()
            if not current_version:
                print("Unable to fetch current ROM version")
                return

            all_devices = self.json_reader.get_all_devices()

            updated = []
            not_updated = []

            version_field = self.config.version_field or "version"

            for device in all_devices:
                device_version = device.get(version_field)
                if device_version == current_version:
                    updated.append(device)
                else:
                    not_updated.append(device)

            msg = f"<b>{self.config.rom_name} Update Status</b><br><br>"
            msg += f"<b>The following devices have been updated to the version</b> <code>{current_version}</code> <b>in the current month:</b> "

            if len(updated) == 0:
                msg += f"<code>None</code>"
            else:
                for i, device in enumerate(updated, 1):
                    device_name = device.get(self.config.device_name_field, "Unknown")
                    maintainer = device.get(self.config.maintainer_field, "Unknown")
                    msg += f"<br><b>{i}.</b> <code>{device_name} ({device['bot_codename']})</code> <b>-</b> <a href='https://t.me/{maintainer}'>{maintainer}</a>"

            msg += "<br><br>"
            msg += f"<b>The following devices have not been updated to the version</b> <code>{current_version}</code> <b>in the current month:</b> "

            if len(not_updated) == 0:
                msg += f"<code>None</code>"
            else:
                for i, device in enumerate(not_updated, 1):
                    device_name = device.get(self.config.device_name_field, "Unknown")
                    maintainer = device.get(self.config.maintainer_field, "Unknown")
                    msg += f"<br><b>{i}.</b> <code>{device_name} ({device['bot_codename']})</code> <b>-</b> <a href='https://t.me/{maintainer}'>{maintainer}</a>"

            msg += "<br><br>"
            msg += f"<b>Total Official Devices:</b> <code>{len(all_devices)}</code><br>"
            msg += (
                f"<b>Updated during current month:</b> <code>{len(updated)}</code><br>"
            )
            msg += f"<b>Not Updated during current month:</b> <code>{len(not_updated)}</code><br><br>"
            msg += f"<b>Information as on:</b> <code>{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')} (UTC)</code>"

            telegraph_url = self.telegraph.create_page(
                title=f"{self.config.rom_name} Device Update Status",
                content=msg,
            )

            text = f"*{self.config.rom_name} Devices (v{current_version}) Update Status*\n\n"
            text += f"*Total Official Devices:* `{len(all_devices)}`\n"
            text += f"*Updated during current month:* `{len(updated)}`\n"
            text += f"*Not Updated during current month:* `{len(not_updated)}`\n"
            text += f"*Information as on:* `{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')} (UTC)`"

            self.telegram.post_status(
                self.config.priv_chat_id,
                text,
                telegraph_url["url"],
            )

        except Exception as e:
            print(f"Error posting status message: {e}")

    def run(self):
        """
        Main execution method - checks for updates and posts to Telegram
        """
        print(f"RomKit OrgPoster - Checking for {self.config.rom_name} updates...\n")

        changed_ids = self.id_tracker.get_changed_ids()

        if not changed_ids:
            print("No updates found. Nothing to do.")
            self.post_status_message()
            return

        print(f"Found {len(changed_ids)} update(s):\n")

        updated_devices = []
        successfully_posted_ids = []

        for id in changed_ids:
            device_info = self.json_reader.get_device_info(self.config.id_field, id)

            if not device_info:
                print(f"Warning: Could not find device info for ID: {id}")
                continue

            device_name = device_info.get(
                self.config.device_name_field,
                device_info.get("bot_codename", "Unknown"),
            )
            print(f"Posting update for {device_name} ({device_info['bot_codename']})")

            try:
                self.post_update(device_info)
                updated_devices.append(device_info)
                successfully_posted_ids.append(id)
                print(f"Successfully posted {device_info['bot_codename']}\n")
            except Exception as e:
                print(f"Error posting {device_info['bot_codename']}: {e}\n")

        if successfully_posted_ids:
            current_ids = self.id_tracker.get_old_ids()
            current_ids.extend(successfully_posted_ids)
            self.id_tracker.save_ids(current_ids)

        if updated_devices:
            commit_msg = self.generate_commit_message(updated_devices)
            Path("commit_mesg.txt").write_text(commit_msg)
            print(f"Commit message saved to commit_mesg.txt")

        print(f"Updated {len(updated_devices)} device(s) successfully!")

        self.post_status_message()
