"""Shared fixtures and test helpers for cmdweaver tests."""
import pytest
from doublex import Spy

from cmdweaver import interpreter as interpreter_module
from cmdweaver import basic_types
from cmdweaver.command import Command


@pytest.fixture
def interpreter():
    """Create a fresh Interpreter instance."""
    return interpreter_module.Interpreter()


@pytest.fixture
def spy():
    """Create a fresh Spy instance."""
    return Spy()


class PlainCompletionsType(basic_types.BaseType):
    """Test helper type that returns plain completions."""

    def __init__(self, options):
        self.options = options

    def match(self, word, context, partial_line=None):
        return word in self.options

    def partial_match(self, word, context, partial_line=None):
        for option in self.options:
            if option.startswith(word):
                return True
        return False

    def complete(self, token, tokens, context):
        return self.options


class CompleteCompletionsType(PlainCompletionsType):
    """Test helper type that returns complete (finished) completions."""

    def complete(self, token, tokens, context):
        return [(value, True) for value in self.options if value.startswith(tokens[-1])]


class PartialCompletionsType(PlainCompletionsType):
    """Test helper type that returns partial (unfinished) completions."""

    def complete(self, token, tokens, context):
        return [(value, False) for value in self.options if value.startswith(tokens[-1])]

