"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import annotations

import threading
import time
from typing import Callable


class PauseableTimer:
    def __init__(self, updatefunc: Callable[[str], None]) -> None:
        self.old_seconds: float = 0.0
        self.reference: float = 0.0
        self.enable: bool = False
        self.updatefunc: Callable[[str], None] = updatefunc

    def incrementer(self) -> None:
        self.updatefunc(self.formatTime(time.time() - self.reference + self.old_seconds))
        if self.enable:
            threading.Timer(0.5, self.incrementer).start()
        else:
            self.old_seconds += time.time() - self.reference

    def start(self) -> None:
        self.reference = time.time()
        self.enable = True
        self.incrementer()

    def stop(self) -> None:
        self.enable = False

    def formatTime(self, seconds: float) -> str:
        return "{0:02d}:{1:02d}".format(int(seconds / 60), int(seconds % 60))
