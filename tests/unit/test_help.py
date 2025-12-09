import pytest
from doublex import Spy
from hamcrest import assert_that, contains_string, has_entries, has_entry, is_not

from cmdweaver import basic_types
from cmdweaver import interpreter as interpreter_module
from cmdweaver.command import Command


class TestHelp:
    @pytest.fixture
    def command_implementation(self):
        return Spy()

    @pytest.fixture
    def cmd1(self, command_implementation):
        return Command(["cmd", "key1"], command_implementation.cmd1, help="help_cmd1", always=True)

    @pytest.fixture
    def cmd2(self, command_implementation):
        return Command(["cmd", "normal"], command_implementation.cmd1, help="help_normal")

    @pytest.fixture
    def cmd_no_help(self, command_implementation):
        return Command(["description", basic_types.StringType()], command_implementation.description)

    @pytest.fixture
    def cmd_context(self, command_implementation):
        return Command(
            ["cmd", "key2"], command_implementation.netmask, context_name="irrelevant_context", help="help_cmd_context"
        )

    @pytest.fixture
    def interpreter(self, cmd1, cmd2, cmd_no_help, cmd_context):
        interp = interpreter_module.Interpreter()
        interp.add_command(cmd1)
        interp.add_command(cmd2)
        interp.add_command(cmd_no_help)
        interp.add_command(cmd_context)
        return interp

    class TestWhenAskingForHelpWithEmptyLine:
        class TestWhenNotInContext:
            def test_returns_help_for_all_active_commands_not_requiring_context(
                self, interpreter, cmd1, cmd2, cmd_no_help, cmd_context
            ):
                result = interpreter.help("")

                assert_that(
                    result,
                    has_entries(
                        cmd1, contains_string("help_cmd1"), cmd2, contains_string("help_normal"), cmd_no_help, None
                    ),
                )
                assert_that(result, is_not(has_entries(cmd_context, contains_string("help_cmd_context"))))

        class TestWhenInsideContext:
            def test_returns_help_for_commands_from_actual_context(self, interpreter, cmd_context):
                interpreter.push_context("irrelevant_context")

                result = interpreter.help("")

                assert_that(result, has_entry(cmd_context, contains_string("help_cmd_context")))

            def test_returns_help_for_always_active_commands(self, interpreter, cmd1):
                interpreter.push_context("irrelevant_context")

                result = interpreter.help("")

                assert_that(result, has_entries(cmd1, contains_string("help_cmd1")))

            def test_does_not_return_help_for_normal_commands(self, interpreter, cmd2, cmd_no_help):
                interpreter.push_context("irrelevant_context")

                result = interpreter.help("")

                assert_that(result, is_not(has_entries(cmd2, contains_string("help_normal"))))
                assert_that(result, is_not(has_entries(cmd_no_help, None)))

    class TestWhenAskingForHelpWithPartialCommand:
        def test_returns_help_for_partial_matching_commands(self, interpreter, cmd1, cmd2, cmd_no_help, cmd_context):
            result = interpreter.help("cmd ")

            assert_that(result, has_entries(cmd1, contains_string("help_cmd1"), cmd2, contains_string("help_normal")))
            assert_that(result, is_not(has_entries(cmd_no_help, None)))
            assert_that(result, is_not(has_entries(cmd_context, contains_string("help_cmd_context"))))

    class TestWhenAskingForHelpForAllCommands:
        def test_returns_help_for_all_commands_even_requiring_context(
            self, interpreter, cmd1, cmd2, cmd_no_help, cmd_context
        ):
            result = interpreter.all_commands_help()

            assert_that(
                result,
                has_entries(
                    cmd1,
                    contains_string("help_cmd1"),
                    cmd2,
                    contains_string("help_normal"),
                    cmd_no_help,
                    None,
                    cmd_context,
                    contains_string("help_cmd_context"),
                ),
            )
