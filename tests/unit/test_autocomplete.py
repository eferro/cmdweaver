import pytest
from hamcrest import assert_that, has_items, has_length
from doublex import Stub

from cmdweaver import interpreter as interpreter_module
from cmdweaver import basic_types
from cmdweaver.command import Command
from tests.conftest import PlainCompletionsType, CompleteCompletionsType, PartialCompletionsType


class TestAutocomplete:
    @pytest.fixture
    def implementation(self):
        return Stub()

    @pytest.fixture
    def interpreter(self, implementation):
        interp = interpreter_module.Interpreter()
        interp.add_command(Command(['sys', 'reboot'], implementation.reboot))
        interp.add_command(Command(['sys', 'shutdown'], implementation.shutdown))
        interp.add_command(Command(['net', 'show', 'configuration'], implementation.show_net_conf))
        return interp

    class TestWhenAutocompletingEmptyLine:
        def test_completes_with_initial_keywords(self, interpreter):
            assert_that(interpreter.complete(''), has_items('sys ', 'net '))

    class TestWhenAutocompletingKeywords:
        def test_completes_keywords(self, interpreter):
            assert_that(interpreter.complete('sy'), has_items('sys '))
            assert_that(interpreter.complete('sys'), has_items('sys '))
            assert_that(interpreter.complete('sys r'), has_items('reboot'))

        def test_does_not_complete_when_command_matches(self, interpreter):
            assert_that(interpreter.complete('sys reboot'), has_length(0))
            assert_that(interpreter.complete('sys reboot '), has_length(0))

        def test_does_not_complete_unknown_command(self, interpreter):
            assert_that(interpreter.complete('unknown command'), has_length(0))

    class TestWhenAutocompletingTypeWithCompletions:
        def test_completes_with_final_space_if_not_last_token(self, interpreter, implementation):
            interpreter.add_command(Command(
                ['cmd', PlainCompletionsType(['op1', 'op2']), 'last'],
                implementation.irrelevant_cmd
            ))

            assert_that(interpreter.complete('cmd o'), has_items('op1 ', 'op2 '))

        def test_completes_without_final_space_if_last_token(self, interpreter, implementation):
            interpreter.add_command(Command(
                ['cmd', PlainCompletionsType(['op1', 'op2'])],
                implementation.irrelevant_cmd
            ))

            assert_that(interpreter.complete('cmd o'), has_items('op1', 'op2'))

    class TestWhenAutocompletingTypeWithCompleteCompletions:
        def test_completes_with_final_space_if_not_last_token(self, interpreter, implementation):
            interpreter.add_command(Command(
                ['cmd', CompleteCompletionsType(['op1', 'op2']), 'last'],
                implementation.irrelevant_cmd
            ))

            assert_that(interpreter.complete('cmd o'), has_items('op1 ', 'op2 '))

        def test_completes_without_final_space_if_last_token(self, interpreter, implementation):
            interpreter.add_command(Command(
                ['cmd', CompleteCompletionsType(['op1', 'op2'])],
                implementation.irrelevant_cmd
            ))

            assert_that(interpreter.complete('cmd o'), has_items('op1', 'op2'))

    class TestWhenAutocompletingTypeWithPartialCompletions:
        def test_completes_without_final_space_if_not_last_token(self, interpreter, implementation):
            interpreter.add_command(Command(
                ['cmd', PartialCompletionsType(['op1', 'op2']), 'last'],
                implementation.irrelevant_cmd
            ))

            assert_that(interpreter.complete('cmd o'), has_items('op1', 'op2'))

    class TestWhenAutocompletingOptionsType:
        def test_completes_with_all_matching_options(self, interpreter, implementation):
            interpreter.add_command(Command(
                ['cmd', basic_types.OptionsType(['op1', 'op2'])],
                implementation.show_net_conf
            ))

            assert_that(interpreter.complete('cmd o'), has_items('op1', 'op2'))

    class TestWhenAutocompletingStringType:
        def test_no_autocomplete_at_all(self, interpreter, implementation):
            interpreter.add_command(Command(
                ['cmd', basic_types.StringType()],
                implementation.show_net_conf
            ))

            assert_that(interpreter.complete('cmd '), has_length(0))

    class TestFilterAutocomplete:
        def test_autocompletes_with_space_when_starting_filter(self, interpreter):
            assert_that(interpreter.complete('net show configuration |'), has_items(' '))

        def test_autocompletes_all_available_filters(self, interpreter):
            assert_that(interpreter.complete('net show configuration | '), has_items('include'))
            assert_that(interpreter.complete('net show configuration | '), has_items('exclude'))

        def test_autocompletes_include(self, interpreter):
            assert_that(interpreter.complete('net show configuration | inclu'), has_items('include'))

        def test_autocompletes_exclude(self, interpreter):
            assert_that(interpreter.complete('net show configuration | exclu'), has_items('exclude'))

