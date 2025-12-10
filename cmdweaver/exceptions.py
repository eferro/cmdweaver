from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cmdweaver.command import Command


class EvalError(Exception):
    pass


class NoMatchingCommandFoundError(EvalError):
    pass


class AmbiguousCommandError(EvalError):
    def __init__(self, matching_commands: list[Command]) -> None:
        self.matching_commands = matching_commands
        super().__init__(matching_commands)


class NotContextDefinedError(Exception):
    pass


class EndOfProgram(Exception):
    pass
