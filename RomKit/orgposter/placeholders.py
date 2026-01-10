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

from typing import Any, Callable, Dict

PLACEHOLDERS: Dict[str, Callable] = {
    "bot_codename": lambda data, filename, buildtype: filename,
    "bot_filename": lambda data, filename, buildtype: data.get("filename", filename),
    "bot_buildtype": lambda data, filename, buildtype: buildtype,
}


class PlaceholderProcessor:
    """Handles placeholder processing for device data"""

    def __init__(self, config):
        """
        Initialize placeholder processor

        Args:
            config: OrgPosterConfig instance
        """
        self.config = config

    def process(
        self,
        data: Dict[str, Any],
        json_filename: str,
        buildtype: str,
    ) -> Dict[str, Any]:
        """
        Add placeholders to device data

        Args:
            data: Device data dictionary
            json_filename: JSON filename without .json
            buildtype: Build type from directory

        Returns:
            Device data with placeholders added
        """
        for name, func in PLACEHOLDERS.items():
            try:
                data[name] = func(data, json_filename, buildtype)
            except Exception as e:
                print(f"Error processing placeholder '{name}': {e}")
                data[name] = ""

        if self.config.website_url:
            data["website_url"] = self.config.website_url

        if self.config.donation_list:
            data.update(self.config.donation_list)

        return data
