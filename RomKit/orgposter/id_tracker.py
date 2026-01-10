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
from typing import Dict, List

from ..utils import extract_data
from .json_reader import JSONReader


class IDTracker:
    """Handles ID tracking for change detection"""

    def __init__(
        self,
        file_ids_path: str,
        json_reader: JSONReader,
        id_field: str,
        device_json_structure: Dict,
    ):
        """
        Initialize ID tracker

        Args:
            file_ids_path: Path to file storing tracked IDs
            json_reader: JSONReader instance for file discovery
            id_field: Name of the ID field in JSON
            device_json_structure: JSON structure definition
        """
        self.file_ids_path = file_ids_path
        self.json_reader = json_reader
        self.id_field = id_field
        self.device_json_structure = device_json_structure

    def get_new_ids(self) -> List[str]:
        """
        Get IDs of all current JSON files

        Returns:
            List of IDs based on id_field config
        """
        file_ids = []

        for file_info in self.json_reader.get_all_json_files():
            json_path = Path(file_info["dir"]) / file_info["file"]
            try:
                with open(json_path) as f:
                    data = json.load(f)
                    extracted = extract_data(data, self.device_json_structure)
                    file_id = extracted.get(self.id_field)
                    if file_id:
                        file_ids.append(file_id)
            except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
                print(f"Error reading {json_path}: {e}")

        return file_ids

    def get_old_ids(self) -> List[str]:
        """
        Get previously tracked IDs

        Returns:
            List of IDs
        """
        id_file = Path(self.file_ids_path)

        if not id_file.exists():
            return []

        with open(id_file) as f:
            return [line.strip() for line in f.readlines()]

    def save_ids(self, ids: List[str]):
        """
        Save current IDs to tracking file

        Args:
            ids: List of IDs to save
        """
        id_file = Path(self.file_ids_path)
        id_file.parent.mkdir(parents=True, exist_ok=True)

        with open(id_file, "w") as f:
            for id in ids:
                f.write(f"{id}\n")

    def get_changed_ids(self) -> List[str]:
        """
        Get list of IDs that have changed since last run

        Returns:
            List of new/changed IDs
        """
        old_ids = self.get_old_ids()
        new_ids = self.get_new_ids()

        changed = list(set(new_ids) - set(old_ids))
        return changed
