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
from typing import Optional

from github import Github


class VersionChecker:
    """Handles ROM version checking from GitHub"""

    def __init__(
        self,
        gh_token: Optional[str],
        version_repo: str,
        version_file: str,
        version_template: str,
    ):
        """
        Initialize version checker

        Args:
            gh_token: GitHub token (optional)
            version_repo: Repository in format 'owner/repo'
            version_file: File path in repo
            version_template: Template with placeholders like '{MAJOR}.{MINOR}'
        """
        self.github = Github(gh_token) if gh_token else Github()
        self.version_repo = version_repo
        self.version_file = version_file
        self.version_template = version_template

    def get_version(self) -> Optional[str]:
        """
        Get current ROM version from GitHub repository

        Returns:
            Version string or None if error
        """
        try:
            repo = self.github.get_repo(self.version_repo)
            content = repo.get_contents(self.version_file).decoded_content.decode()

            variables = set(re.findall(r"\{(\w+?)\}", self.version_template))
            values = {}

            for var in variables:
                pattern = rf"{var}\s*:?=\s*(.+)"
                match = re.search(pattern, content)
                if match:
                    values[var] = match.group(1).strip()
                else:
                    print(f"Warning: Variable '{var}' not found in {self.version_file}")
                    values[var] = "UNKNOWN"

            version = self.version_template.format(**values)
            return version

        except Exception as e:
            print(f"Error fetching ROM version: {e}")
            return None
