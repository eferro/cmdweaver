import pytest
from doublex import Spy, called, never
from hamcrest import assert_that

from cmdweaver import filters


class TestFilters:
    @pytest.fixture
    def output_stream(self):
        return Spy()

    @pytest.fixture
    def include_filter(self, output_stream):
        return filters.IncludeFilter("regex", output_stream)

    @pytest.fixture
    def exclude_filter(self, output_stream):
        return filters.ExcludeFilter("regex", output_stream)

    class TestWhenLineIncludesRegex:
        def test_include_filter_outputs_the_line(self, include_filter, output_stream):
            include_filter.write("line including regex \n")

            assert_that(output_stream.write, called().with_args("line including regex \n"))

        def test_exclude_filter_does_not_output_the_line(self, exclude_filter, output_stream):
            exclude_filter.write("line including regex \n")

            assert_that(output_stream.write, never(called().with_args("line including regex \n")))

    class TestWhenLineDoesNotIncludeRegex:
        def test_include_filter_does_not_output_the_line(self, include_filter, output_stream):
            include_filter.write("line \n")

            assert_that(output_stream.write, never(called().with_args("line including regex \n")))

        def test_exclude_filter_outputs_the_line(self, exclude_filter, output_stream):
            exclude_filter.write("line \n")

            assert_that(output_stream.write, called().with_args("line \n"))

    class TestWhenWritingChunksOfData:
        def test_include_filter_processes_data_line_by_line(self, include_filter, output_stream):
            include_filter.write("begin ")
            include_filter.write("regex ")
            include_filter.write("end\n")

            assert_that(output_stream.write, called().with_args("begin regex end\n"))

        def test_exclude_filter_processes_data_line_by_line(self, exclude_filter, output_stream):
            exclude_filter.write("begin ")
            exclude_filter.write("end\n")

            assert_that(output_stream.write, called().with_args("begin end\n"))
