from hamcrest import is_
from doublex import assert_that

from cmdweaver.command import Command


class TestCommand:
    def test_allows_assigning_a_command_id(self):
        command = Command(['k1', 'k2'], cmd_id='cmd_id1')

        assert_that(command.cmd_id, is_('cmd_id1'))

