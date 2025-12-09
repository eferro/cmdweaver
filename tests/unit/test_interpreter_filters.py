import pytest
from doublex import Spy, Stub, assert_that, called

from cmdweaver import exceptions
from cmdweaver import interpreter as interpreter_module
from cmdweaver.command import Command


class TestInterpreterFilters:
    @pytest.fixture
    def filter_factory(self):
        return Spy()

    @pytest.fixture
    def output_stream(self):
        return Stub()

    @pytest.fixture
    def cmds_implementation(self):
        return Spy()

    @pytest.fixture
    def interpreter(self, filter_factory, output_stream, cmds_implementation):
        interp = interpreter_module.Interpreter(filter_factory=filter_factory, output_stream=output_stream)
        interp.add_command(Command(["cmd", "key"], cmds_implementation.cmd))
        return interp

    class TestMalformedLine:
        def test_raises_syntax_error_when_two_filters(self, interpreter):
            with pytest.raises(exceptions.SyntaxError):
                interpreter.eval("cmd key | include regexp | exclude regexp")

        def test_raises_syntax_error_when_incomplete_filter(self, interpreter):
            with pytest.raises(exceptions.SyntaxError):
                interpreter.eval("cmd key | include")

        def test_raises_syntax_error_when_unknown_filter(self, interpreter):
            with pytest.raises(exceptions.SyntaxError):
                interpreter.eval("cmd key | unknown_filter regexp")

    class TestCommandExecution:
        def test_executes_command_connected_to_include_filter(
            self, interpreter, cmds_implementation, filter_factory, output_stream
        ):
            interpreter.eval("cmd key | include regexp")

            assert_that(cmds_implementation.cmd, called().with_args(tokens=["cmd", "key"], interpreter=interpreter))
            assert_that(filter_factory.create_include_filter, called().with_args("regexp", output_stream))

        def test_executes_command_with_abbreviated_include_keyword(
            self, interpreter, cmds_implementation, filter_factory, output_stream
        ):
            interpreter.eval("cmd key | inc regexp")

            assert_that(cmds_implementation.cmd, called().with_args(tokens=["cmd", "key"], interpreter=interpreter))
            assert_that(filter_factory.create_include_filter, called().with_args("regexp", output_stream))

        def test_executes_command_connected_to_exclude_filter(
            self, interpreter, cmds_implementation, filter_factory, output_stream
        ):
            interpreter.eval("cmd key | exclude regexp")

            assert_that(cmds_implementation.cmd, called().with_args(tokens=["cmd", "key"], interpreter=interpreter))
            assert_that(filter_factory.create_exclude_filter, called().with_args("regexp", output_stream))

        def test_executes_command_with_abbreviated_exclude_keyword(
            self, interpreter, cmds_implementation, filter_factory, output_stream
        ):
            interpreter.eval("cmd key | exc regexp")

            assert_that(cmds_implementation.cmd, called().with_args(tokens=["cmd", "key"], interpreter=interpreter))
            assert_that(filter_factory.create_exclude_filter, called().with_args("regexp", output_stream))
