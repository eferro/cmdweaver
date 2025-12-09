import pytest
from doublex import ANY_ARG, Spy, assert_that, called, is_, never, when

from cmdweaver import basic_types, exceptions
from cmdweaver import interpreter as interpreter_module
from cmdweaver.command import Command


class TestInterpreterContext:
    @pytest.fixture
    def always_present(self):
        return Spy()

    @pytest.fixture
    def main_commands(self):
        return Spy()

    @pytest.fixture
    def context_commands(self):
        return Spy()

    @pytest.fixture
    def interpreter(self, always_present, main_commands, context_commands):
        interp = interpreter_module.Interpreter(prompt="irrelevant_prompt")
        interp.add_command(Command(["exit"], main_commands.exit))
        interp.add_command(Command(["always_present"], always_present.always_present, always=True))
        interp.add_command(Command(["cmd1"], context_commands.cmd1, context_name="context1"))
        interp.add_command(Command(["cmd2"], context_commands.cmd2, context_name="context1"))
        interp.add_command(Command(["exit"], context_commands.exit, context_name="context1"))
        return interp

    class TestWhenNotInRequiredContext:
        def test_does_not_execute_main_command(self, interpreter, main_commands):
            interpreter.push_context("context1")

            # In context1 there's an 'exit' command, so it doesn't raise
            # but it should NOT execute the main_commands.exit
            interpreter.eval("exit")

            assert_that(main_commands.exit, never(called()))

        def test_executes_always_present_commands(self, interpreter, always_present):
            interpreter.push_context("context1")

            interpreter.eval("always_present")

            assert_that(always_present.always_present, called().with_args(ANY_ARG))

    class TestWhenNotInAnyContext:
        def test_does_not_execute_command_from_other_context(self, interpreter, context_commands):
            with pytest.raises(exceptions.NoMatchingCommandFoundError):
                interpreter.eval("cmd1")

            with pytest.raises(exceptions.NoMatchingCommandFoundError):
                interpreter.eval("cmd2")

            assert_that(context_commands.cmd1, never(called()))
            assert_that(context_commands.cmd2, never(called()))

        def test_executes_commands_in_default_context(self, interpreter, main_commands):
            interpreter.eval("exit")

            assert_that(main_commands.exit, called().with_args(ANY_ARG))

        def test_raises_error_when_popping_context_at_top_level(self, interpreter):
            with pytest.raises(exceptions.NotContextDefinedError):
                interpreter.pop_context()

    class TestWhenInsideContext:
        def test_executes_commands_from_the_context(self, interpreter, context_commands):
            interpreter.push_context("context1")

            interpreter.eval("cmd1")
            interpreter.eval("cmd2")

            assert_that(context_commands.cmd1, called().with_args(ANY_ARG))
            assert_that(context_commands.cmd2, called().with_args(ANY_ARG))
            assert_that(interpreter.actual_context().has_name("context1"), is_(True))

        def test_executes_context_commands_not_outside_commands(self, interpreter, context_commands):
            interpreter.push_context("context1")

            interpreter.eval("exit")

            assert_that(context_commands.exit, called().with_args(ANY_ARG))

        def test_attaches_info_to_actual_context(self, interpreter):
            interpreter.push_context("context1")

            context_data = interpreter.actual_context().data
            context_data["key1"] = "data1"
            context_data["key2"] = "data2"

            assert_that(interpreter.actual_context().data, is_({"key1": "data1", "key2": "data2"}))

        def test_allows_stacking_another_context(self, interpreter):
            interpreter.push_context("context1")
            interpreter.push_context("context2")

            assert_that(interpreter.actual_context().context_name, is_("context2"))

            interpreter.pop_context()

            assert_that(interpreter.actual_context().context_name, is_("context1"))

        def test_default_prompt_is_interpreter_initial_prompt(self, interpreter):
            assert_that(interpreter.prompt, is_("irrelevant_prompt"))

        def test_default_context_prompt_is_context_name(self, interpreter):
            interpreter.push_context("context1")

            assert_that(interpreter.prompt, is_("context1"))

    class TestWhenPushingContextWithPrompt:
        def test_assigns_prompt_to_context(self, interpreter):
            interpreter.push_context("context1", prompt="prompt1")

            assert_that(interpreter.prompt, is_("prompt1"))


class TestTypesCanUseContext:
    @pytest.fixture
    def type_spy(self):
        return Spy(basic_types.BaseType)

    @pytest.fixture
    def command_spy(self):
        return Spy()

    @pytest.fixture
    def interpreter(self, type_spy, command_spy):
        interp = interpreter_module.Interpreter(prompt="irrelevant_prompt")
        interp.add_command(Command([type_spy], command_spy.command, context_name="context1"))
        interp.push_context("context1", prompt="prompt1")
        when(type_spy).complete(ANY_ARG).returns([])
        when(type_spy).partial_match(ANY_ARG).returns(True)
        return interp

    @pytest.fixture
    def actual_context(self, interpreter):
        return interpreter.actual_context()

    class TestWhenAutocompletingCommand:
        def test_passes_context_to_the_type(self, interpreter, type_spy, actual_context):
            when(type_spy).match(ANY_ARG).returns(False)

            interpreter.complete("test")

            assert_that(type_spy.partial_match, called().with_args("test", actual_context, partial_line=["test"]))
            assert_that(type_spy.complete, called().with_args("test", ["test"], actual_context))

    class TestWhenExecutingCommand:
        def test_passes_context_to_type_to_verify_match(self, interpreter, type_spy, actual_context):
            when(type_spy).match(ANY_ARG).returns(True)

            interpreter.eval("test")

            assert_that(type_spy.match, called().with_args("test", actual_context, partial_line=["test"]))
