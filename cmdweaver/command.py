from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeAlias

if TYPE_CHECKING:
    from cmdweaver.basic_types import BaseType
    from cmdweaver.interpreter import Context

    KeywordDefinition: TypeAlias = str | BaseType


class KeywordType:
    def __init__(self, name: str) -> None:
        self.name = name

    def complete(self, token: str, tokens: list[str], context: Context) -> list[tuple[str, bool]]:
        if self.name.startswith(token):
            return [(self.name, True)]
        return []

    def match(self, word: str, context: Context, partial_line: list[str] | None = None) -> bool:
        return word == self.name

    def partial_match(self, word: str, context: Context, partial_line: list[str] | None = None) -> bool:
        return bool(self.name.startswith(word))

    def __str__(self) -> str:
        return f"{self.name}"


class Command:
    def __init__(
        self,
        keywords: list[KeywordDefinition],
        command_function: Callable[..., Any] | None = None,
        help: str | None = None,
        context_name: str | None = None,
        always: bool = False,
        cmd_id: str | None = None,
    ) -> None:
        self.definitions: list[KeywordType | BaseType] = []
        for definition in keywords:
            if isinstance(definition, str):
                self.definitions.append(KeywordType(definition))
            else:
                self.definitions.append(definition)

        self.keywords = keywords
        self.command_function = command_function
        self.help = help
        self.context_name = context_name
        self.always = always
        self.cmd_id = cmd_id

    def __lt__(self, other: Command) -> bool:
        return self.__str__().__lt__(other.__str__())

    def __str__(self) -> str:
        return " ".join(str(token_definition) for token_definition in self.keywords)

    def __repr__(self) -> str:
        return str(self)

    def normalize_tokens(self, tokens: list[str], context: Context) -> list[str]:
        result: list[str] = []
        for index, word in enumerate(tokens):
            definition_for_that_index = self.keywords[index]
            if self._is_keyword(definition_for_that_index):
                result.append(definition_for_that_index)  # type: ignore[arg-type]
            else:
                result.append(self._expand_parameter(self.definitions[index], word, tokens, context))
        return result

    def _match_word(self, index: int, word: str, context: Context, partial_line: list[str]) -> bool:
        definition = self.definitions[index]
        if isinstance(definition, KeywordType):
            return definition.partial_match(word, context, partial_line=partial_line)
        else:
            word = self._expand_parameter(self.definitions[index], word, partial_line, context)
            return self.definitions[index].match(word, context, partial_line=partial_line)

    def _expand_parameter(
        self, definition: KeywordType | BaseType, word: str, tokens: list[str], context: Context
    ) -> str:
        completions = definition.complete(word, tokens, context)
        if len(completions) == 1:
            return completions[0][0]
        return word

    def _partial_match(self, index: int, word: str, context: Context, partial_line: list[str]) -> bool:
        return self.definitions[index].partial_match(word, context, partial_line=partial_line)

    def partial_match(self, tokens: list[str], context: Context) -> bool:
        if len(tokens) > len(self.keywords):
            return False

        for index, word in enumerate(tokens):
            if index == len(tokens) - 1:
                if not self._partial_match(index, word, context, partial_line=tokens):
                    return False
            else:
                if not self._match_word(index, word, context, partial_line=tokens):
                    return False

        return True

    def context_match(self, context: Context) -> bool:
        if self.always:
            return True

        if self.context_name and context.is_default():
            return False

        if not self.context_name and context.is_default():
            return True

        if self.context_name is None:
            return False

        return context.has_name(self.context_name)

    def match(self, tokens: list[str], context: Context) -> bool:
        if not self.context_match(context):
            return False
        if len(tokens) != len(self.keywords):
            return False
        return all(self._match_word(index, word, context, partial_line=tokens) for index, word in enumerate(tokens))

    def perfect_match(self, tokens: list[str], context: Context) -> bool:
        if not self.match(tokens, context):
            return False
        return self.normalize_tokens(tokens, context) == tokens

    def matching_parameters(self, tokens: list[str]) -> list[str]:
        parameters: list[str] = []
        for index, token in enumerate(tokens):
            if not isinstance(self.keywords[index], str):
                parameters.append(token)
        return parameters

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        if self.command_function:
            return self.command_function(*args, **kwargs)
        return None

    def complete(self, tokens: list[str], context: Context) -> list[str]:
        definition, token = self._select_token_to_complete(tokens)
        return self.completions(definition, token, tokens, context)

    def completions(self, definition: KeywordDefinition, token: str, tokens: list[str], context: Context) -> list[str]:
        if self._is_keyword(definition):
            raw_completions: list[Any] = self._complete_keyword(definition, token, tokens, context)  # type: ignore[arg-type]
        else:
            raw_completions = definition.complete(token, tokens, context)  # type: ignore[union-attr]

        completions: list[str] = []
        for completion in raw_completions:
            if isinstance(completion, tuple):
                completions.append(completion[0] + (" " if completion[1] else ""))
            else:
                completions.append(completion.strip() + " ")

        return [completion.strip() if self._is_last_token(tokens) else completion for completion in completions]

    def _complete_keyword(self, definition: str, token: str, tokens: list[str], context: Context) -> list[str]:
        if definition == token:
            if not self.match(tokens, context):
                return [token]
        elif definition.startswith(token):
            return [definition]

        return []

    def _is_last_token(self, tokens: list[str]) -> bool:
        return len(tokens) == len(self.keywords)

    def _select_token_to_complete(self, tokens: list[str]) -> tuple[KeywordDefinition, str]:
        if not tokens:
            return (self.keywords[0], "")
        else:
            return (self.keywords[len(tokens) - 1], tokens[-1])

    def _is_keyword(self, definition: KeywordDefinition) -> bool:
        return isinstance(definition, str)
