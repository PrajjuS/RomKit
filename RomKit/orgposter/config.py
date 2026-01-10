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

from typing import Any, Dict, List, Optional

from NoobStuffs.libenvconfig import getConfig
from NoobStuffs.libyamlconfig import YAMLConfig


class OrgPosterConfig:
    """Configuration loader for OrgPoster"""

    def __init__(self, config_path: str = "romkit.yaml"):
        """
        Load configuration from YAML file

        Args:
            config_path: Path to YAML configuration file
        """
        self.yaml = YAMLConfig(config_path)
        self.getConfig = getConfig
        self._load()

    def _load(self):
        """Load and validate all configuration"""
        self.bot_token: str = self.getConfig("BOT_TOKEN") or self.yaml.getConfig(
            "bot_token",
            is_required=True,
        )
        self.gh_token: Optional[str] = self.getConfig(
            "GH_TOKEN",
        ) or self.yaml.getConfig("gh_token")
        self.chat_ids: List[str] = self.getConfig(
            "CHAT_IDS",
            return_type=list,
        ) or self.yaml.getConfig("chat_ids", return_type=list, is_required=True)
        self.priv_chat_id: Optional[str] = self.getConfig(
            "PRIV_CHAT_ID",
        ) or self.yaml.getConfig("priv_chat_id")

        self.bot_username: str = self.yaml.getConfig("bot_username", is_required=True)
        self.rom_name: str = self.yaml.getConfig("rom_name", is_required=True)
        self.json_directories: Dict[str, str] = self.yaml.getConfig(
            "json_directories",
            is_required=True,
            return_type=dict,
        )
        self.device_json_structure: Dict[str, Any] = self.yaml.getConfig(
            "device_json_structure",
            is_required=True,
            return_type=dict,
        )
        self.id_field: str = self.yaml.getConfig("id_field", is_required=True)
        self.message_template: str = self.yaml.getConfig(
            "message_template",
            is_required=True,
        )
        self.file_ids_path: str = self.yaml.getConfig("file_ids_path", is_required=True)
        self.banner_path: str = self.yaml.getConfig("banner_path", is_required=True)

        self.version_repo: str = self.yaml.getConfig("version_repo", is_required=True)
        self.version_file: str = self.yaml.getConfig("version_file", is_required=True)
        self.version_template: str = self.yaml.getConfig(
            "version_template",
            is_required=True,
        )
        self.version_field: str = self.yaml.getConfig("version_field", is_required=True)

        self.device_name_field: str = self.yaml.getConfig(
            "device_name_field",
            is_required=True,
        )
        self.maintainer_field: str = self.yaml.getConfig(
            "maintainer_field",
            is_required=True,
        )

        self.website_url: Optional[str] = self.yaml.getConfig("website_url")
        self.donation_list: List[Dict[str, str]] = self.yaml.getConfig(
            "donation_list",
            return_type=list,
        )
