import pytest
from hamcrest import has_length, contains_string, has_items, string_contains_in_order, contains
from doublex import assert_that, is_, Spy, Stub, when

from cmdweaver import basic_types


class TestOrType:
    @pytest.fixture
    def type1(self):
        return Spy(basic_types.BaseType)

    @pytest.fixture
    def type2(self):
        return Spy(basic_types.BaseType)

    @pytest.fixture
    def type3(self):
        return Spy(basic_types.BaseType)

    @pytest.fixture
    def context(self):
        return 'irrelevant_context'

    @pytest.fixture
    def or_type(self, type1, type2, type3):
        return basic_types.OrType(type1, type2, type3)

    def test_autocompletes_with_all_types_autocompletions(self, or_type, type1, type2, type3, context):
        when(type1).complete('token', ['token'], context).returns(['irrelevant_res1'])
        when(type2).complete('token', ['token'], context).returns(['irrelevant_res2'])
        when(type3).complete('token', ['token'], context).returns(['irrelevant_res3'])

        result = or_type.complete('token', ['token'], context)

        assert_that(result, contains('irrelevant_res1', 'irrelevant_res2', 'irrelevant_res3'))

    def test_matches_if_any_type_matches(self, or_type, type1, type2, type3, context):
        when(type1).match('token', context, partial_line=['token']).returns(False)
        when(type2).match('token', context, partial_line=['token']).returns(True)
        when(type3).match('token', context, partial_line=['token']).returns(False)

        result = or_type.match('token', context, partial_line=['token'])

        assert_that(result, is_(True))

    def test_does_not_match_when_none_matches(self, or_type, type1, type2, type3, context):
        when(type1).match('token', context, partial_line=['token']).returns(False)
        when(type2).match('token', context, partial_line=['token']).returns(False)
        when(type3).match('token', context, partial_line=['token']).returns(False)

        result = or_type.match('token', context, partial_line=['token'])

        assert_that(result, is_(False))

    def test_partial_matches_if_any_type_matches(self, or_type, type1, type2, type3, context):
        when(type1).partial_match('token', context, partial_line=['token']).returns(False)
        when(type2).partial_match('token', context, partial_line=['token']).returns(True)
        when(type3).partial_match('token', context, partial_line=['token']).returns(False)

        result = or_type.partial_match('token', context, partial_line=['token'])

        assert_that(result, is_(True))

    def test_does_not_partial_match_when_none_matches(self, or_type, type1, type2, type3, context):
        when(type1).partial_match('token', context, partial_line=['token']).returns(False)
        when(type2).partial_match('token', context, partial_line=['token']).returns(False)
        when(type3).partial_match('token', context, partial_line=['token']).returns(False)

        result = or_type.partial_match('token', context, partial_line=['token'])

        assert_that(result, is_(False))

    class TestRepresentation:
        def test_contains_name_when_provided(self, type1, type2, type3):
            or_type = basic_types.OrType(type1, type2, type3, name='name')

            assert_that(str(or_type), contains_string('name'))


class TestBasicTypes:
    @pytest.fixture
    def bool_type(self):
        return basic_types.BoolType(name='Bool')

    @pytest.fixture
    def options_type(self):
        return basic_types.OptionsType(['op1', 'op2'])

    @pytest.fixture
    def string_type(self):
        return basic_types.StringType(name='String')

    @pytest.fixture
    def regex_type(self):
        return basic_types.RegexType('op[1-3]', name='ops1-3')

    @pytest.fixture
    def integer_type(self):
        return basic_types.IntegerType(min=5, max=10)

    @pytest.fixture
    def context(self):
        return 'irrelevant_context'

    class TestBoolType:
        def test_autocompletes_with_options(self, bool_type, context):
            assert_that(bool_type.complete('', [''], context), has_items(('true', True), ('false', True)))

        def test_matches_true_or_false(self, bool_type, context):
            assert_that(bool_type.match('true', context), is_(True))
            assert_that(bool_type.match('false', context), is_(True))

        def test_does_not_match_other_words(self, bool_type, context):
            assert_that(bool_type.match('whatever', context), is_(False))

        def test_partial_matches_true_or_false(self, string_type, context):
            assert_that(string_type.partial_match('tr', context), is_(True))
            assert_that(string_type.partial_match('fa', context), is_(True))

        class TestRepresentation:
            def test_has_default_representation(self):
                assert_that(str(basic_types.BoolType()), string_contains_in_order('true', 'false'))

            def test_has_name_as_representation_when_provided(self):
                assert_that(str(basic_types.BoolType(name='name')), contains_string('name'))

    class TestOptionsType:
        def test_autocompletes_with_options(self, options_type, context):
            assert_that(options_type.complete('', [''], context), has_items(('op1', True), ('op2', True)))

        def test_matches_valid_options(self, options_type, context):
            assert_that(options_type.match('op1', context), is_(True))

        def test_does_not_match_invalid_options(self, options_type, context):
            assert_that(options_type.match('invalid_option', context), is_(False))

        def test_partial_matches_words_starting_like_valid_options(self, options_type, context):
            assert_that(options_type.partial_match('o', context), is_(True))

        def test_does_not_partial_match_invalid_starts(self, options_type, context):
            assert_that(options_type.partial_match('inv', context), is_(False))

        class TestRepresentation:
            def test_includes_options_in_representation(self, options_type):
                assert_that(str(options_type), string_contains_in_order('op1', 'op2'))

            def test_includes_name_when_provided(self):
                options_type = basic_types.OptionsType(['op1', 'op2'], name='name')
                assert_that(str(options_type), contains_string('name'))

    class TestDynamicOptionsType:
        @pytest.fixture
        def options_stub(self):
            stub = Stub()
            when(stub).get_options().returns(['op1', 'op2'])
            return stub

        @pytest.fixture
        def dynamic_options_type(self, options_stub):
            return basic_types.DynamicOptionsType(options_stub.get_options)

        def test_autocompletes_with_dynamic_options(self, dynamic_options_type, context):
            assert_that(dynamic_options_type.complete('', [''], context), has_items(('op1', True), ('op2', True)))

        def test_matches_valid_options(self, dynamic_options_type, context):
            assert_that(dynamic_options_type.match('op1', context), is_(True))

        def test_does_not_match_invalid_options(self, dynamic_options_type, context):
            assert_that(dynamic_options_type.match('invalid_option', context), is_(False))

        def test_partial_matches_words_starting_like_valid_options(self, dynamic_options_type, context):
            assert_that(dynamic_options_type.partial_match('o', context), is_(True))

        def test_does_not_partial_match_invalid_starts(self, dynamic_options_type, context):
            assert_that(dynamic_options_type.partial_match('inv', context), is_(False))

        class TestRepresentation:
            def test_includes_options_in_representation(self, dynamic_options_type):
                assert_that(str(dynamic_options_type), string_contains_in_order('op1', 'op2'))

            def test_includes_name_when_provided(self):
                dynamic_options_type = basic_types.DynamicOptionsType(Stub().get_options, name='name')
                assert_that(str(dynamic_options_type), contains_string('name'))

    class TestStringType:
        def test_has_no_autocompletion(self, string_type, context):
            assert_that(string_type.complete('', [''], context), has_length(0))

        def test_does_not_match_empty_value(self, string_type, context):
            assert_that(string_type.match('', context), is_(False))

        def test_matches_any_non_empty_value(self, string_type, context):
            assert_that(string_type.match('whatever', context), is_(True))
            assert_that(string_type.match('1', context), is_(True))

        def test_does_not_partial_match_empty_value(self, string_type, context):
            assert_that(string_type.partial_match('', context), is_(False))

        def test_partial_matches_any_non_empty_value(self, string_type, context):
            assert_that(string_type.partial_match('whatever', context), is_(True))
            assert_that(string_type.partial_match('1', context), is_(True))

        class TestRepresentation:
            def test_has_default_representation(self):
                assert_that(str(basic_types.StringType()), contains_string('StringType'))

            def test_has_name_as_representation_when_provided(self):
                assert_that(str(basic_types.StringType(name='name')), contains_string('name'))

    class TestIntegerType:
        def test_has_no_autocompletion(self, integer_type, context):
            assert_that(integer_type.complete('', [''], context), has_length(0))

        def test_does_not_match_strings(self, integer_type, context):
            assert_that(integer_type.match('whatever', context), is_(False))

        class TestWhenMinLimitDefined:
            def test_matches_numbers_greater_than_limit(self, integer_type, context):
                assert_that(integer_type.match('5', context), is_(False))
                assert_that(integer_type.match('6', context), is_(True))

            def test_partial_matches_numbers_greater_than_limit(self, integer_type, context):
                assert_that(integer_type.partial_match('5', context), is_(False))
                assert_that(integer_type.partial_match('6', context), is_(True))

        class TestWhenMaxLimitDefined:
            def test_matches_numbers_lesser_than_limit(self, integer_type, context):
                assert_that(integer_type.match('10', context), is_(False))
                assert_that(integer_type.match('6', context), is_(True))

            def test_partial_matches_numbers_lesser_than_limit(self, context):
                integer_type = basic_types.IntegerType(max=10)
                assert_that(integer_type.partial_match('10', context), is_(False))
                assert_that(integer_type.partial_match('6', context), is_(True))

        class TestRepresentation:
            def test_has_default_representation(self):
                assert_that(str(basic_types.IntegerType()), contains_string('IntegerType'))

            def test_has_name_as_representation_when_provided(self):
                assert_that(str(basic_types.IntegerType(name='name')), contains_string('name'))

    class TestRegexType:
        def test_has_no_autocompletion(self, regex_type, context):
            assert_that(regex_type.complete('', [''], context), has_length(0))

        def test_matches_when_regexp_matches(self, regex_type, context):
            assert_that(regex_type.match('op1', context), is_(True))
            assert_that(regex_type.match('op2', context), is_(True))
            assert_that(regex_type.match('op3', context), is_(True))
            assert_that(regex_type.match('op4', context), is_(False))

        def test_partial_matches_when_regexp_matches(self, regex_type, context):
            assert_that(regex_type.partial_match('op1', context), is_(True))
            assert_that(regex_type.partial_match('op2', context), is_(True))
            assert_that(regex_type.partial_match('op3', context), is_(True))
            assert_that(regex_type.partial_match('op4', context), is_(False))

        def test_propagates_context_and_partial_line_to_match(self, context):
            class TestRegexType(basic_types.RegexType):
                def __init__(self):
                    super().__init__('op[1-3]')
                    self.recorded = None

                def match(self, word, context, partial_line=None):
                    self.recorded = (word, context, partial_line)
                    return True

            regex_type = TestRegexType()

            result = regex_type.partial_match('op1', context, partial_line=['op'])

            assert_that(result, is_(True))
            assert_that(regex_type.recorded, is_(('op1', context, ['op'])))

        class TestRepresentation:
            def test_has_default_representation(self):
                assert_that(str(basic_types.RegexType('regEx')), contains_string('RegexType'))

            def test_has_name_as_representation_when_provided(self):
                assert_that(str(basic_types.RegexType('regEx', name='name')), contains_string('name'))

