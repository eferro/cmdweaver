from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cmdweaver import exceptions
from cmdweaver import parser as parser_module

if TYPE_CHECKING:
    from cmdweaver.command import Command


class Context:
    def __init__(self, context_name: str, prompt: str | None = None) -> None:
        self.context_name = context_name
        self.prompt: str = prompt if prompt else self.context_name
        self.data: dict[str, Any] = {}

    def is_default(self) -> bool:
        return False

    def has_name(self, context_name: str) -> bool:
        return self.context_name == context_name

    def __str__(self) -> str:
        return f"Context:{self.context_name}"


class DefaultContext(Context):
    def __init__(self, prompt: str | None = None) -> None:
        super().__init__("Default", prompt=prompt)

    def is_default(self) -> bool:
        return True


class Interpreter:
    def __init__(
        self,
        parser: parser_module.Parser | None = None,
        prompt: str = "",
    ) -> None:
        self._commands: list[Command] = []
        self.parser = parser if parser is not None else parser_module.Parser()
        self.context: list[Context] = [DefaultContext(prompt)]

    def add_command(self, command: Command) -> None:
        self._commands.append(command)

    def push_context(self, context_name: str, prompt: str | None = None) -> None:
        self.context.append(Context(context_name, prompt))

    def pop_context(self) -> None:
        if len(self.context) == 1:
            raise exceptions.NotContextDefinedError()
        self.context.pop()

    def exit(self) -> None:
        raise exceptions.EndOfProgram()

    def _matching_command(self, tokens: list[str], line_text: str) -> Command:
        matching_commands = self._select_matching_commands(tokens)
        if len(matching_commands) == 1:
            return matching_commands[0]

        if len(matching_commands) > 1:
            raise exceptions.AmbiguousCommandError(matching_commands)
        raise exceptions.NoMatchingCommandFoundError(line_text)

    def eval_multiple(self, lines: list[str]) -> list[Any]:
        results: list[Any] = []
        for line in lines:
            results.append(self.eval(line))
        return results

    def parse(self, line_text: str) -> str | None:
        _, result = self._parse(line_text)
        return result.cmd_id if result else None

    def eval(self, line_text: str) -> Any:
        tokens, matching_command = self._parse(line_text)
        if not matching_command:
            return None

        return self._execute_command(
            matching_command, matching_command.normalize_tokens(tokens, self.actual_context())
        )

    def _parse(self, line_text: str) -> tuple[list[str], Command | None]:
        line_text = line_text.strip()
        if not line_text:
            return [], None

        tokens = self.parser.parse(line_text)
        return tokens, self._matching_command(tokens, line_text)

    def _execute_command(self, command: Command, tokens: list[str]) -> Any:
        arguments = command.matching_parameters(tokens)
        try:
            cmd_id = command.cmd_id
            if cmd_id is None:
                return command.execute(*arguments, tokens=tokens, interpreter=self)
            else:
                return command.execute(*arguments, tokens=tokens, interpreter=self, cmd_id=cmd_id)
        except KeyboardInterrupt:
            return None

    def _select_matching_commands(self, tokens: list[str]) -> list[Command]:
        return [command for command in self._commands if command.match(tokens, self.actual_context())]

    def actual_context(self) -> Context:
        return self.context[-1]

    def active_commands(self) -> list[Command]:
        return [command for command in self._commands if command.context_match(self.actual_context())]

    def _partial_match(self, line_text: str) -> list[Command]:
        tokens = self.parser.parse(line_text)
        return [command for command in self.active_commands() if command.partial_match(tokens, self.actual_context())]

    def help(self, line_text: str) -> dict[Command, str | None]:
        return {command: command.help for command in self._partial_match(line_text)}

    def all_commands_help(self) -> dict[Command, str | None]:
        return {command: command.help for command in self._commands}

    def complete(self, line_to_complete: str) -> set[str]:
        completions: set[str] = set()
        tokens = self.parser.parse(line_to_complete)

        for command in self._partial_match(line_to_complete):
            completions.update(command.complete(tokens, self.actual_context()))
        return completions

    @property
    def prompt(self) -> str:
        return self.actual_context().prompt

    @prompt.setter
    def prompt(self, value: str) -> None:
        self.actual_context().prompt = value
