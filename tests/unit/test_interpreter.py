import pytest
from doublex import ANY_ARG, Spy, Stub, assert_that, called, when
from hamcrest import has_items, has_length, is_, is_not, none

from cmdweaver import basic_types, exceptions
from cmdweaver import interpreter as interpreter_module
from cmdweaver.command import Command


class TestInterpreter:
    @pytest.fixture
    def cmds_implementation(self):
        return Spy()

    @pytest.fixture
    def interpreter(self, cmds_implementation):
        interp = interpreter_module.Interpreter()
        interp.add_command(Command(["cmd", "key"], cmds_implementation.cmd, cmd_id="id1"))
        interp.add_command(
            Command(
                ["cmd_with_parameters", basic_types.StringType(), basic_types.StringType()],
                cmds_implementation.cmd_with_parameters,
                cmd_id="id2",
            )
        )
        interp.add_command(
            Command(
                ["cmd_with_ops", basic_types.OptionsType(["op1", "op2"])],
                cmds_implementation.cmd_with_ops,
                cmd_id="id3",
            )
        )
        interp.add_command(
            Command(
                ["cmd_with_regex", basic_types.RegexType("^start.*")], cmds_implementation.cmd_with_regex, cmd_id="id4"
            )
        )
        return interp

    class TestCommandExecution:
        class TestWhenEvaluatingMultipleLines:
            def test_executes_each_line_command(self, interpreter, cmds_implementation):
                lines = ["cmd key", "cmd_with_parameters s1 s2"]

                interpreter.eval_multiple(lines)

                assert_that(
                    cmds_implementation.cmd,
                    called().with_args(tokens=["cmd", "key"], interpreter=interpreter, cmd_id="id1"),
                )
                assert_that(
                    cmds_implementation.cmd_with_parameters,
                    called().with_args(
                        "s1", "s2", tokens=["cmd_with_parameters", "s1", "s2"], interpreter=interpreter, cmd_id="id2"
                    ),
                )

            def test_returns_result_for_each_line(self, interpreter, cmds_implementation):
                when(cmds_implementation).cmd(ANY_ARG).returns("a_result")
                lines = ["cmd key", "cmd_with_parameters s1 s2"]

                result = interpreter.eval_multiple(lines)

                assert_that(result, has_items("a_result", None))

        class TestWhenEvaluatingEmptyLine:
            def test_returns_none(self, interpreter):
                assert_that(interpreter.eval(""), none())

        class TestWhenAllKeywordsMatch:
            def test_executes_command(self, interpreter, cmds_implementation):
                interpreter.eval("cmd key")

                assert_that(
                    cmds_implementation.cmd,
                    called().with_args(tokens=["cmd", "key"], interpreter=interpreter, cmd_id="id1"),
                )

        class TestCtrlCWhenRunningCommand:
            def test_stops_the_command(self, interpreter, cmds_implementation):
                def an_interrupted_cmd(*args, **kwargs):
                    cmds_implementation.cmd1()
                    raise KeyboardInterrupt()
                    cmds_implementation.cmd2()

                interpreter.add_command(Command(["cmd", "ctrl+c"], an_interrupted_cmd))

                interpreter.eval("cmd ctrl+c")

                assert_that(cmds_implementation.cmd1, called())
                assert_that(cmds_implementation.cmd2, is_not(called()))

        class TestWhenLineDoesNotMatchAnyCommand:
            def test_raises_exception(self, interpreter):
                with pytest.raises(exceptions.NoMatchingCommandFoundError):
                    interpreter.eval("unknown command")

        class TestWhenTwoCommandsMatch:
            def test_raises_ambiguous_command_exception_with_commands_info(self, interpreter):
                cmd1 = Command(["duplicate_cmd"], Stub().cmd1)
                interpreter.add_command(cmd1)
                cmd2 = Command(["duplicate_cmd"], Stub().cmd2)
                interpreter.add_command(cmd2)

                with pytest.raises(exceptions.AmbiguousCommandError) as exc_info:
                    interpreter.eval("duplicate_cmd")

                assert_that(exc_info.value.matching_commands, has_length(2))
                assert_that(exc_info.value.matching_commands, has_items(cmd1, cmd2))

        class TestWhenKeywordsAreAbbreviated:
            def test_does_not_execute_with_abbreviated_keywords(self, interpreter):
                with pytest.raises(exceptions.NoMatchingCommandFoundError):
                    interpreter.eval("cm ke")

        class TestStringParameters:
            def test_executes_command_passing_parameters(self, interpreter, cmds_implementation):
                interpreter.eval("cmd_with_parameters param1 param2")

                assert_that(
                    cmds_implementation.cmd_with_parameters,
                    called().with_args(
                        "param1",
                        "param2",
                        tokens=["cmd_with_parameters", "param1", "param2"],
                        interpreter=interpreter,
                        cmd_id="id2",
                    ),
                )

            def test_quoted_parameters_can_contain_spaces(self, interpreter, cmds_implementation):
                interpreter.eval('cmd_with_parameters param1 "param with spaces"')

                assert_that(
                    cmds_implementation.cmd_with_parameters,
                    called().with_args(
                        "param1",
                        "param with spaces",
                        tokens=["cmd_with_parameters", "param1", "param with spaces"],
                        interpreter=interpreter,
                        cmd_id="id2",
                    ),
                )

        class TestOptionsParameters:
            def test_executes_command_with_valid_option(self, interpreter, cmds_implementation):
                interpreter.eval("cmd_with_ops op1")

                assert_that(
                    cmds_implementation.cmd_with_ops,
                    called().with_args("op1", tokens=["cmd_with_ops", "op1"], interpreter=interpreter, cmd_id="id3"),
                )

            def test_does_not_execute_with_invalid_option(self, interpreter):
                with pytest.raises(exceptions.NoMatchingCommandFoundError):
                    interpreter.eval("cmd_with_ops invalid_op")

        class TestRegexParameter:
            def test_executes_command_when_parameter_matches_regex(self, interpreter, cmds_implementation):
                interpreter.eval("cmd_with_regex start_whatever")

                assert_that(
                    cmds_implementation.cmd_with_regex,
                    called().with_args(
                        "start_whatever",
                        tokens=["cmd_with_regex", "start_whatever"],
                        interpreter=interpreter,
                        cmd_id="id4",
                    ),
                )

            def test_does_not_execute_when_parameter_does_not_match_regex(self, interpreter):
                with pytest.raises(exceptions.NoMatchingCommandFoundError):
                    interpreter.eval("cmd_with_regex not_matching_parameter")

    class TestCommandExecutionWithAutoexpansion:
        def test_expands_parameter_to_unique_autocompletion(self, interpreter, cmds_implementation):
            interpreter.add_command(
                Command(["cmd1", basic_types.OptionsType(["firstOp", "secondOp"])], cmds_implementation.cmd1)
            )

            interpreter.eval("cmd1 first")

            assert_that(
                cmds_implementation.cmd1,
                called().with_args("firstOp", tokens=["cmd1", "firstOp"], interpreter=interpreter),
            )

        def test_expands_all_parameters_with_unique_autocompletions(self, interpreter, cmds_implementation):
            interpreter.add_command(
                Command(
                    [
                        "cmd1",
                        basic_types.OptionsType(["firstOp", "secondOp"]),
                        basic_types.OptionsType(["firstOp", "secondOp"]),
                    ],
                    cmds_implementation.cmd1,
                )
            )

            interpreter.eval("cmd1 first second")

            assert_that(
                cmds_implementation.cmd1,
                called().with_args(
                    "firstOp", "secondOp", tokens=["cmd1", "firstOp", "secondOp"], interpreter=interpreter
                ),
            )

    class TestPromptManagement:
        def test_has_default_prompt(self, interpreter):
            assert_that(interpreter.prompt, is_("Default"))

        def test_allows_changing_prompt(self, interpreter):
            interpreter.prompt = "prompt1"

            assert_that(interpreter.prompt, is_("prompt1"))

        def test_maintains_prompts_of_previous_contexts(self, interpreter):
            interpreter.prompt = "default"

            assert_that(interpreter.prompt, is_("default"))

            interpreter.push_context("context1", "prompt_context1")
            assert_that(interpreter.prompt, is_("prompt_context1"))

            interpreter.push_context("context2", "prompt_context2")
            assert_that(interpreter.prompt, is_("prompt_context2"))

            interpreter.pop_context()
            assert_that(interpreter.prompt, is_("prompt_context1"))

            interpreter.pop_context()
            assert_that(interpreter.prompt, is_("default"))


class TestInterpreterParseMode:
    @pytest.fixture
    def interpreter(self):
        interp = interpreter_module.Interpreter()
        interp.add_command(Command(["cmd", "key1"], Spy().irrelevant_func, cmd_id="id1"))
        interp.add_command(Command(["cmd", "key2"], Spy().irrelevant_func, cmd_id="id2"))
        return interp

    def test_parses_a_line(self, interpreter):
        result1 = interpreter.parse("cmd key1")
        result2 = interpreter.parse("cmd key2")

        assert_that(result1, is_("id1"))
        assert_that(result2, is_("id2"))

    def test_parses_a_line_with_spaces(self, interpreter):
        result = interpreter.parse(" cmd key1 ")

        assert_that(result, is_("id1"))

    def test_returns_none_for_empty_line(self, interpreter):
        result = interpreter.parse("")

        assert_that(result, is_(None))

    def test_raises_exception_when_no_match(self, interpreter):
        with pytest.raises(exceptions.NoMatchingCommandFoundError):
            interpreter.eval("unknown command")
