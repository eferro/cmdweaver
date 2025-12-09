from __future__ import annotations

import re
import sys
from typing import TextIO


class ByLineBaseFilter:
    def __init__(self) -> None:
        self.output = ""

    def write(self, data: str) -> None:
        self.output += data
        k = self.output.rfind("\n")
        if k != -1:
            data_to_flush = self.output[:k]
            for line in data_to_flush.splitlines():
                self.process_line(line)
            self.output = self.output[k + 1 :]

    def flush(self) -> None:
        pass

    def process_line(self, line: str) -> None:
        pass


class IncludeFilter(ByLineBaseFilter):
    def __init__(self, regex: str, stdout: TextIO) -> None:
        self.regex = re.compile(regex)
        self.stdout = stdout
        super().__init__()

    def process_line(self, line: str) -> None:
        if self.regex.search(line):
            self.stdout.write(line + "\n")


class ExcludeFilter(ByLineBaseFilter):
    def __init__(self, regex: str, stdout: TextIO) -> None:
        self.regex = re.compile(regex)
        self.stdout = stdout
        super().__init__()

    def process_line(self, line: str) -> None:
        if not self.regex.search(line):
            self.stdout.write(line + "\n")


class RedirectStdout:
    """Create a context manager for redirecting sys.stdout
    to another file.
    """

    def __init__(self, new_target: ByLineBaseFilter) -> None:
        self.new_target = new_target
        self.old_target: TextIO | None = None

    def __enter__(self) -> RedirectStdout:
        self.old_target = sys.stdout
        sys.stdout = self.new_target
        return self

    def __exit__(
        self, exctype: type[BaseException] | None, excinst: BaseException | None, exctb: object
    ) -> None:
        sys.stdout = self.old_target


class FilterFactory:
    def create_include_filter(self, reg_ex: str, output: TextIO) -> IncludeFilter:
        return IncludeFilter(reg_ex, output)

    def create_exclude_filter(self, reg_ex: str, output: TextIO) -> ExcludeFilter:
        return ExcludeFilter(reg_ex, output)
