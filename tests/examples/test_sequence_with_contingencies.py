# Copyright 2021 Andreas Steck (steck.andi@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from io import StringIO

import re

from unittest.mock import patch
from carebt.abstractLogger import LogLevel

from carebt.behaviorTreeRunner import BehaviorTreeRunner
from carebt.examples.sequence_with_contingencies import AddTwoNumbersAction
from carebt.examples.sequence_with_contingencies import Sequence
from carebt.examples.sequence_with_contingencies import ContingencySequence
from carebt.nodeStatus import NodeStatus


class TestSequenceWithContingencies:

    @patch('sys.stdout', new_callable=StringIO)
    def test_AddTwoNumbersAction_ok(self, mock_print):
        bt_runner = BehaviorTreeRunner()
        bt_runner.run(AddTwoNumbersAction, '1 2 => ?x')
        regex = re.compile(r'AddTwoNumbersAction: calculating: 1 \+ 2 = 3\n')
        assert bool(re.match(regex, mock_print.getvalue()))
        assert bt_runner.get_status() == NodeStatus.SUCCESS
        assert bt_runner.get_contingency_message() == ''

    @patch('sys.stdout', new_callable=StringIO)
    def test_AddTwoNumbersAction_one_missing(self, mock_print):
        bt_runner = BehaviorTreeRunner()
        bt_runner.run(AddTwoNumbersAction, '1 => ?x')
        regex = re.compile(r'')
        assert bool(re.match(regex, mock_print.getvalue()))
        assert bt_runner.get_status() == NodeStatus.FAILURE
        assert bt_runner.get_contingency_message() == 'ONE_PARAM_MISSING'

    @patch('sys.stdout', new_callable=StringIO)
    def test_AddTwoNumbersAction_both_missing(self, mock_print):
        bt_runner = BehaviorTreeRunner()
        bt_runner.run(AddTwoNumbersAction, '=> ?x')
        regex = re.compile(r'')
        assert bool(re.match(regex, mock_print.getvalue()))
        assert bt_runner.get_status() == NodeStatus.FAILURE
        assert bt_runner.get_contingency_message() == 'BOTH_PARAMS_MISSING'

    @patch('sys.stdout', new_callable=StringIO)
    def test_AddTwoNumbersAction_to_large(self, mock_print):
        bt_runner = BehaviorTreeRunner()
        bt_runner.run(AddTwoNumbersAction, '6 8 => ?x')
        regex = re.compile(r'')
        assert bool(re.match(regex, mock_print.getvalue()))
        assert bt_runner.get_status() == NodeStatus.FAILURE
        assert bt_runner.get_contingency_message() == 'RESULT_TOO_LARGE'

########################################################################

    @patch('sys.stdout', new_callable=StringIO)
    def test_Sequence_ok(self, mock_print):
        bt_runner = BehaviorTreeRunner()
        bt_runner.run(Sequence, '1 2')
        regex = re.compile(r'AddTwoNumbersAction: calculating: [0-9]+ \+ [0-9]+ = [0-9]+\n'
                           + r'PrintNumberAction: number = [0-9]+\n')
        assert bool(re.match(regex, mock_print.getvalue()))
        assert bt_runner.get_status() == NodeStatus.SUCCESS
        assert bt_runner.get_contingency_message() == ''

    @patch('sys.stdout', new_callable=StringIO)
    def test_Sequence_one_missing(self, mock_print):
        bt_runner = BehaviorTreeRunner()
        bt_runner.run(Sequence, '1')
        regex = re.compile('')
        assert bool(re.match(regex, mock_print.getvalue()))
        assert bt_runner.get_status() == NodeStatus.FAILURE
        assert bt_runner.get_contingency_message() == 'ONE_PARAM_MISSING'

    @patch('sys.stdout', new_callable=StringIO)
    def test_Sequence_both_missing(self, mock_print):
        bt_runner = BehaviorTreeRunner()
        bt_runner.run(Sequence, '')
        regex = re.compile('')
        assert bool(re.match(regex, mock_print.getvalue()))
        assert bt_runner.get_status() == NodeStatus.FAILURE
        assert bt_runner.get_contingency_message() == 'BOTH_PARAMS_MISSING'

    @patch('sys.stdout', new_callable=StringIO)
    def test_Sequence_to_large(self, mock_print):
        bt_runner = BehaviorTreeRunner()
        bt_runner.run(Sequence, '11 22')
        regex = re.compile('')
        assert bool(re.match(regex, mock_print.getvalue()))
        assert bt_runner.get_status() == NodeStatus.FAILURE
        assert bt_runner.get_contingency_message() == 'RESULT_TOO_LARGE'

########################################################################

    @patch('sys.stdout', new_callable=StringIO)
    def test_ContingencySequence1_ok(self, mock_print):
        bt_runner = BehaviorTreeRunner()
        bt_runner.run(ContingencySequence, '1 2')
        regex = re.compile(r'AddTwoNumbersAction: calculating: [0-9]+ \+ [0-9]+ = [0-9]+\n'
                           + r'PrintNumberAction: number = [0-9]+\n')
        assert bool(re.match(regex, mock_print.getvalue()))
        assert bt_runner.get_status() == NodeStatus.SUCCESS
        assert bt_runner.get_contingency_message() == ''

    @patch('sys.stdout', new_callable=StringIO)
    def test_ContingencySequence1_one_missing(self, mock_print):
        bt_runner = BehaviorTreeRunner()
        bt_runner.get_logger().set_log_level(LogLevel.OFF)
        bt_runner.run(ContingencySequence, '1')
        regex = re.compile(r'fix_missing_input: set \?c = 0\n'
                           + r'PrintNumberAction: number = 0\n')
        assert bool(re.match(regex, mock_print.getvalue()))
        assert bt_runner.get_status() == NodeStatus.SUCCESS
        assert bt_runner.get_contingency_message() == ''

    @patch('sys.stdout', new_callable=StringIO)
    def test_ContingencySequence1_both_missing(self, mock_print):
        bt_runner = BehaviorTreeRunner()
        bt_runner.get_logger().set_log_level(LogLevel.OFF)
        bt_runner.run(ContingencySequence, '')
        regex = re.compile(r'fix_missing_input: set \?c = 0\n'
                           + r'PrintNumberAction: number = 0\n')
        assert bool(re.match(regex, mock_print.getvalue()))
        assert bt_runner.get_status() == NodeStatus.SUCCESS
        assert bt_runner.get_contingency_message() == ''

    @patch('sys.stdout', new_callable=StringIO)
    def test_ContingencySequence1_to_large(self, mock_print):
        bt_runner = BehaviorTreeRunner()
        bt_runner.get_logger().set_log_level(LogLevel.OFF)
        bt_runner.run(ContingencySequence, '6 9')
        regex = re.compile(r'AddTwoNumbersAction: calculating: 6 \+ 9 = 15\n'
                           + r'fix_large_result\n'
                           + r'CreateRandomNumberAction: number = [0-9]+\n'
                           + r'PrintNumberAction: number = [0-9]+\n')
        assert bool(re.match(regex, mock_print.getvalue()))
        assert bt_runner.get_status() == NodeStatus.SUCCESS
        assert bt_runner.get_contingency_message() == ''
