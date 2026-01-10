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

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils import extract_data
from .placeholders import PlaceholderProcessor


class JSONReader:
    """Handles JSON file discovery and device information extraction"""

    def __init__(
        self,
        json_directories: Dict[str, str],
        device_json_structure: Dict,
        placeholder_processor: "PlaceholderProcessor",
    ):
        """
        Initialize JSON reader

        Args:
            json_directories: Dict mapping build type to directory path
            device_json_structure: JSON structure definition for parsing
            placeholder_processor: PlaceholderProcessor instance
        """
        self.json_directories = json_directories
        self.device_json_structure = device_json_structure
        self.placeholder_processor = placeholder_processor

    def get_all_json_files(self) -> List[Dict[str, str]]:
        """
        Get all JSON files from configured directories

        Returns:
            List of dicts with type, dir, and file info
        """
        files = []

        for build_type, directory in self.json_directories.items():
            dir_path = Path(directory)
            if dir_path.exists():
                for json_file in dir_path.glob("*.json"):
                    files.append(
                        {
                            "type": build_type,
                            "dir": str(dir_path),
                            "file": json_file.name,
                        },
                    )

        return files

    def get_device_info(self, id_field: str, id_value: str) -> Optional[Dict[str, Any]]:
        """
        Get device information by ID

        Args:
            id_field: Name of the ID field
            id_value: ID value to search for

        Returns:
            Dictionary with device information including bot placeholders
        """
        for file_info in self.get_all_json_files():
            json_path = Path(file_info["dir"]) / file_info["file"]
            try:
                with open(json_path) as f:
                    data = json.load(f)
                    extracted = extract_data(data, self.device_json_structure)

                    if extracted.get(id_field) == id_value:
                        codename = file_info["file"].replace(".json", "")
                        extracted = self.placeholder_processor.process(
                            extracted,
                            codename,
                            file_info["type"],
                        )
                        return extracted
            except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
                print(f"Error reading {json_path}: {e}")

        return None

    def get_all_devices(self) -> List[Dict[str, Any]]:
        """
        Get information for all devices

        Returns:
            List of device info dictionaries
        """
        devices = []

        for file_info in self.get_all_json_files():
            json_path = Path(file_info["dir"]) / file_info["file"]
            try:
                with open(json_path) as f:
                    data = json.load(f)
                    extracted = extract_data(data, self.device_json_structure)

                    codename = file_info["file"].replace(".json", "")
                    extracted = self.placeholder_processor.process(
                        extracted,
                        codename,
                        file_info["type"],
                    )

                    devices.append(extracted)
            except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
                print(f"Error reading {json_path}: {e}")
                continue

        return devices
