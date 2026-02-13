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

import logging
import os

FULL_MODULE_PATH = os.getenv("ROMKIT_FULL_MODULE_PATH", "false").lower() == "true"


class RomKitFormatter(logging.Formatter):
    """Custom formatter to show: [LEVEL] - RomKit - Module: message"""

    def format(self, record):
        parts = record.name.split(".")
        if len(parts) >= 2 and parts[0] == "RomKit":
            if FULL_MODULE_PATH:
                record.module_name = ".".join(parts[1:])
            else:
                record.module_name = parts[1]
        else:
            record.module_name = record.name

        return super().format(record)


handler = logging.StreamHandler()
handler.setFormatter(
    RomKitFormatter("[%(levelname)s] - RomKit - %(module_name)s: %(message)s"),
)

logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)

logging.getLogger("TelegraphHelper").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("github").setLevel(logging.ERROR)
