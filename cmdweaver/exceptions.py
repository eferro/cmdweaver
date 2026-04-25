from __future__ import annotations

from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class ArgumentError:
    index: int
    name: str | None
    value: str
    slot_str: str
    valid_options: list[str] | None = field(default=None)


class InvalidArgumentError(EvalError):
    def __init__(self, command: Command, argument_errors: list[ArgumentError]) -> None:
        self.command = command
        self.argument_errors = argument_errors
        super().__init__(command, argument_errors)

    def __str__(self) -> str:
        details = ", ".join(
            f"{err.name or f'arg[{err.index}]'}={err.value!r}" for err in self.argument_errors
        )
        return f"InvalidArgumentError(command={self.command}, errors=[{details}])"


class NotContextDefinedError(Exception):
    pass


class EndOfProgram(Exception):
    pass
