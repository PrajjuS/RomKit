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

from github import Github

from ..utils import extract_data
from .json_reader import JSONReader
from .placeholders import PlaceholderProcessor


class DeviceInfoReader:
    """
    Orchestrates multiple data sources for device information.
    Merges data from OTA JSON files with optional device info sources.
    """

    def __init__(
        self,
        device_info_sources: Optional[List[Dict[str, Any]]],
        gh_token: Optional[str],
        json_reader: "JSONReader",
        placeholder_processor: "PlaceholderProcessor",
    ):
        """
        Initialize device info reader

        Args:
            device_info_sources: List of source configurations (optional)
            gh_token: GitHub token for API access (optional)
            json_reader: JSONReader instance for OTA files
            placeholder_processor: PlaceholderProcessor instance
        """
        self.json_reader = json_reader
        self.placeholder_processor = placeholder_processor
        self.gh_token = gh_token
        self.device_info_sources = device_info_sources or []
        self.sources_cache: Dict[str, Dict[str, Any]] = {}

        if self.device_info_sources:
            self._load_all_sources()

    def _load_all_sources(self):
        """
        Load all device info sources once and cache them.
        Called during initialization to avoid repeated network calls.
        """
        for source in self.device_info_sources:
            source_name = source.get("name")
            if not source_name:
                print("Warning: Source missing 'name' field, skipping")
                continue

            try:
                if source["type"] == "github":
                    data = self._load_github_source(source)
                elif source["type"] == "local":
                    data = self._load_local_source(source)
                else:
                    print(
                        f"Warning: Unknown source type '{source['type']}' for {source_name}",
                    )
                    continue

                structure = source["structure"]

                if (
                    isinstance(data, list)
                    and isinstance(structure, list)
                    and len(structure) > 0
                ):
                    extracted_data = []
                    for item in data:
                        extracted_item = extract_data(item, structure[0])
                        extracted_data.append(extracted_item)
                else:
                    extracted_data = extract_data(data, structure)

                if not isinstance(extracted_data, list):
                    extracted_data = [extracted_data] if extracted_data else []

                self.sources_cache[source_name] = {
                    "data": extracted_data,
                    "config": source,
                }
                print(f"Loaded {len(extracted_data)} items from source '{source_name}'")

            except Exception as e:
                print(f"Error loading source '{source_name}': {e}")

    def _load_github_source(self, source: Dict[str, Any]) -> Any:
        """
        Load data from GitHub repository

        Args:
            source: Source configuration dict

        Returns:
            Parsed JSON data from GitHub file
        """
        github = Github(self.gh_token) if self.gh_token else Github()
        repo = github.get_repo(source["repo"])
        content = repo.get_contents(source["file"]).decoded_content.decode()
        return json.loads(content)

    def _load_local_source(self, source: Dict[str, Any]) -> Any:
        """
        Load data from local file

        Args:
            source: Source configuration dict

        Returns:
            Parsed JSON data from local file
        """
        file_path = Path(source["file"])
        with open(file_path) as f:
            return json.load(f)

    def _lookup_in_source(
        self,
        source_name: str,
        lookup_field: str,
        lookup_value: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Fast in-memory lookup in cached source data

        Args:
            source_name: Name of the source to search
            lookup_field: Field name to match on
            lookup_value: Value to search for

        Returns:
            Matched item dict or None if not found
        """
        if source_name not in self.sources_cache:
            return None

        cached_source = self.sources_cache[source_name]
        data = cached_source["data"]

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get(lookup_field) == lookup_value:
                    return item
        elif isinstance(data, dict):
            if data.get(lookup_field) == lookup_value:
                return data

        return None

    def _merge_sources_into_device(self, ota_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge source data into OTA device data with prefixes

        Args:
            ota_data: Device data from OTA JSON

        Returns:
            Dictionary with merged device information including prefixed source fields
        """
        current_data = ota_data.copy()

        for source_name, cached_source in self.sources_cache.items():
            config = cached_source["config"]
            lookup_field = config.get("lookup_field")

            if not lookup_field:
                continue

            if config.get("match_from"):
                lookup_value = current_data.get(config["match_from"])
            else:
                lookup_value = ota_data.get(lookup_field)

            if lookup_value:
                match = self._lookup_in_source(source_name, lookup_field, lookup_value)
                if match:
                    prefixed_match = {f"{source_name}_{k}": v for k, v in match.items()}
                    current_data.update(prefixed_match)

        return current_data

    def get_device_info(self, id_field: str, id_value: str) -> Optional[Dict[str, Any]]:
        """
        Get device information by ID with merged source data

        Args:
            id_field: Name of the ID field
            id_value: ID value to search for

        Returns:
            Dictionary with merged device information or None
        """
        ota_data = self.json_reader.get_device_info(id_field, id_value)
        if not ota_data:
            return None

        if not self.device_info_sources:
            return ota_data

        return self._merge_sources_into_device(ota_data)

    def get_all_devices(self) -> List[Dict[str, Any]]:
        """
        Get all devices with merged source data

        Returns:
            List of device info dictionaries with merged data
        """
        all_devices = []

        ota_devices = self.json_reader.get_all_devices()

        if not self.device_info_sources:
            return ota_devices

        for ota_device in ota_devices:
            merged_device = self._merge_sources_into_device(ota_device)
            all_devices.append(merged_device)

        return all_devices

    def get_all_json_files(self) -> List[Dict[str, str]]:
        """
        Get all JSON files from configured directories.
        Delegates to internal JSONReader.

        Returns:
            List of dicts with type, dir, and file info
        """
        return self.json_reader.get_all_json_files()
