import pytest
from doublex import ANY_ARG, Spy, Stub, assert_that, called, when
from hamcrest import contains_string, has_items, has_length, is_, is_not, none

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

            def test_raises_invalid_argument_when_option_value_is_unknown(self, interpreter):
                with pytest.raises(exceptions.InvalidArgumentError) as exc_info:
                    interpreter.eval("cmd_with_ops invalid_op")

                error = exc_info.value
                assert_that(error.argument_errors, has_length(1))
                argument_error = error.argument_errors[0]
                assert_that(argument_error.index, is_(1))
                assert_that(argument_error.value, is_("invalid_op"))
                assert_that(argument_error.valid_options, is_(["op1", "op2"]))

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

            def test_raises_invalid_argument_when_value_does_not_match_regex(self, interpreter):
                with pytest.raises(exceptions.InvalidArgumentError) as exc_info:
                    interpreter.eval("cmd_with_regex not_matching_parameter")

                error = exc_info.value
                assert_that(error.argument_errors, has_length(1))
                argument_error = error.argument_errors[0]
                assert_that(argument_error.index, is_(1))
                assert_that(argument_error.value, is_("not_matching_parameter"))
                assert_that(argument_error.valid_options, is_(none()))

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

    class TestInvalidArgument:
        def test_reports_invalid_option_in_named_slot(self, cmds_implementation):
            interp = interpreter_module.Interpreter()
            env_slot = basic_types.OptionsType(["prod", "staging"], name="env")
            interp.add_command(Command(["aws", "key", "reset", env_slot], cmds_implementation.cmd))

            with pytest.raises(exceptions.InvalidArgumentError) as exc_info:
                interp.eval("aws key reset banana")

            error = exc_info.value
            assert_that(error.command.keywords, is_(["aws", "key", "reset", env_slot]))
            assert_that(error.argument_errors, has_length(1))
            argument_error = error.argument_errors[0]
            assert_that(argument_error.index, is_(3))
            assert_that(argument_error.name, is_("env"))
            assert_that(argument_error.value, is_("banana"))
            assert_that(argument_error.slot_str, is_("<env>"))
            assert_that(argument_error.valid_options, is_(["prod", "staging"]))

        def test_reports_only_failing_slots_when_multiple_typed_args(self, cmds_implementation):
            interp = interpreter_module.Interpreter()
            interp.add_command(
                Command(
                    [
                        "deploy",
                        basic_types.OptionsType(["prod", "staging"], name="env"),
                        basic_types.IntegerType(min=0, max=100, name="version"),
                    ],
                    cmds_implementation.cmd,
                )
            )

            with pytest.raises(exceptions.InvalidArgumentError) as exc_info:
                interp.eval("deploy prod NaN")

            error = exc_info.value
            assert_that(error.argument_errors, has_length(1))
            assert_that(error.argument_errors[0].index, is_(2))
            assert_that(error.argument_errors[0].name, is_("version"))
            assert_that(error.argument_errors[0].value, is_("NaN"))
            assert_that(error.argument_errors[0].valid_options, is_(none()))

        def test_genuinely_unknown_keyword_still_raises_no_match(self, cmds_implementation):
            interp = interpreter_module.Interpreter()
            interp.add_command(Command(["aws", "key", "reset"], cmds_implementation.cmd))

            with pytest.raises(exceptions.NoMatchingCommandFoundError):
                interp.eval("totally unknown command here")

        def test_invalid_option_does_not_promote_other_keyword_paths(self, cmds_implementation):
            interp = interpreter_module.Interpreter()
            interp.add_command(
                Command(
                    ["aws", "key", "reset", basic_types.OptionsType(["prod", "staging"], name="env")],
                    cmds_implementation.cmd_reset,
                )
            )
            interp.add_command(Command(["aws", "key", "rotate"], cmds_implementation.cmd_rotate))

            with pytest.raises(exceptions.InvalidArgumentError) as exc_info:
                interp.eval("aws key reset banana")

            assert_that(exc_info.value.command.command_function, is_(cmds_implementation.cmd_reset))

        def test_reports_argument_error_without_name_when_slot_is_unnamed(self, cmds_implementation):
            interp = interpreter_module.Interpreter()
            interp.add_command(Command(["pick", basic_types.OptionsType(["a", "b"])], cmds_implementation.cmd))

            with pytest.raises(exceptions.InvalidArgumentError) as exc_info:
                interp.eval("pick z")

            argument_error = exc_info.value.argument_errors[0]
            assert_that(argument_error.name, is_(none()))
            assert_that(argument_error.slot_str, is_("<a|b>"))
            assert_that(argument_error.valid_options, is_(["a", "b"]))

        def test_raises_ambiguous_when_multiple_commands_share_structural_shape(self, cmds_implementation):
            interp = interpreter_module.Interpreter()
            interp.add_command(Command(["pick", basic_types.OptionsType(["a", "b"])], cmds_implementation.cmd_one))
            interp.add_command(Command(["pick", basic_types.OptionsType(["c", "d"])], cmds_implementation.cmd_two))

            with pytest.raises(exceptions.AmbiguousCommandError) as exc_info:
                interp.eval("pick z")

            assert_that(exc_info.value.matching_commands, has_length(2))

        def test_str_includes_named_slot_value(self, cmds_implementation):
            interp = interpreter_module.Interpreter()
            interp.add_command(
                Command(
                    ["aws", "key", "reset", basic_types.OptionsType(["prod", "staging"], name="env")],
                    cmds_implementation.cmd,
                )
            )

            with pytest.raises(exceptions.InvalidArgumentError) as exc_info:
                interp.eval("aws key reset banana")

            assert_that(str(exc_info.value), contains_string("env='banana'"))

        def test_str_falls_back_to_arg_index_when_slot_unnamed(self, cmds_implementation):
            interp = interpreter_module.Interpreter()
            interp.add_command(Command(["pick", basic_types.OptionsType(["a", "b"])], cmds_implementation.cmd))

            with pytest.raises(exceptions.InvalidArgumentError) as exc_info:
                interp.eval("pick z")

            assert_that(str(exc_info.value), contains_string("arg[1]='z'"))

    class TestStructuralMatch:
        def test_returns_false_when_keyword_position_differs(self, cmds_implementation):
            command = Command(
                ["aws", "key", "reset", basic_types.OptionsType(["prod"], name="env")],
                cmds_implementation.cmd,
            )
            context = interpreter_module.DefaultContext()

            assert_that(command.structural_match(["aws", "key", "rotate", "prod"], context), is_(False))

        def test_returns_false_when_tokens_are_shorter_than_keywords(self, cmds_implementation):
            command = Command(
                ["aws", "key", "reset", basic_types.OptionsType(["prod"], name="env")],
                cmds_implementation.cmd,
            )
            context = interpreter_module.DefaultContext()

            assert_that(command.structural_match(["aws", "key", "reset"], context), is_(False))

        def test_returns_false_when_tokens_are_longer_than_keywords(self, cmds_implementation):
            command = Command(
                ["aws", "key", "reset", basic_types.OptionsType(["prod"], name="env")],
                cmds_implementation.cmd,
            )
            context = interpreter_module.DefaultContext()

            assert_that(command.structural_match(["aws", "key", "reset", "prod", "extra"], context), is_(False))

        def test_returns_true_for_matching_keywords_even_with_invalid_typed_value(
            self, cmds_implementation
        ):
            command = Command(
                ["aws", "key", "reset", basic_types.OptionsType(["prod"], name="env")],
                cmds_implementation.cmd,
            )
            context = interpreter_module.DefaultContext()

            assert_that(command.structural_match(["aws", "key", "reset", "banana"], context), is_(True))

        def test_returns_false_when_command_is_scoped_to_a_different_context(self, cmds_implementation):
            command = Command(
                ["scoped", basic_types.OptionsType(["a", "b"], name="opt")],
                cmds_implementation.cmd,
                context_name="config",
            )
            default_context = interpreter_module.DefaultContext()

            assert_that(command.structural_match(["scoped", "a"], default_context), is_(False))

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
