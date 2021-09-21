from tests.global_mock import mock
from tests.helloActions import SayHelloAction

from unittest.mock import call

from carebt.actionNode import ActionNode
from carebt.behaviorTree import BehaviorTree
from carebt.nodeStatus import NodeStatus
from carebt.parallelNode import ParallelNode

########################################################################


class TickCountingAction(ActionNode):

    def __init__(self, bt):
        super().__init__(bt, '=> ?count')
        self._count = 0
        mock('__init__ {}'.format(self.__class__.__name__))

    def on_tick(self) -> None:
        self._count += 1
        mock('TickCountingAction - count: {}'.format(self._count))
        self.set_status(NodeStatus.RUNNING)

    def __del__(self):
        mock('__del__ {}'.format(self.__class__.__name__))

########################################################################


class EachThirdCountAction(ActionNode):

    def __init__(self, bt):
        super().__init__(bt, '?count')
        self._count = 0
        self._each_third_count = 0
        mock('__init__ {}'.format(self.__class__.__name__))

    def on_tick(self) -> None:
        self.set_status(NodeStatus.RUNNING)
        if(self._count % 3 == 0):
            self._each_third_count += 1
            mock('EachThirdCountAction - do action')
        if(self._each_third_count >= 3):
            mock('EachThirdCountAction - finished')
            self.set_status(NodeStatus.SUCCESS)

    def __del__(self):
        mock('__del__ {}'.format(self.__class__.__name__))

########################################################################


class SimpleParallel(ParallelNode):

    def __init__(self, bt):
        super().__init__(bt, 2, '?name')
        self.add_child(SayHelloAction, '"Alice"')
        self.add_child(SayHelloAction, '?name')
        mock('__init__ {}'.format(self.__class__.__name__))

        self.attach_rule_handler(SayHelloAction,
                                 [NodeStatus.FAILURE],
                                 'CHUCK_IS_NOT_ALLOWED',
                                 self.handle_name_is_chuck)

    def handle_name_is_chuck(self) -> None:
        mock('handle_name_is_chuck')
        print('Oh Chuck, lets stop!')
        self.abort()
        self.set_message('WRONG_NAME')

    def on_abort(self) -> None:
        mock('on_abort {}'.format(self.__class__.__name__))

    def __del__(self):
        mock('__del__ {}'.format(self.__class__.__name__))

########################################################################


class TickCountingParallel(ParallelNode):

    def __init__(self, bt):
        super().__init__(bt, 1)
        self.add_child(TickCountingAction, '=> ?cnt')
        self.add_child(EachThirdCountAction, '?cnt')
        mock('__init__ {}'.format(self.__class__.__name__))

    def __del__(self):
        mock('__del__ {}'.format(self.__class__.__name__))

########################################################################


class TestParallelNode:

    def test_parallel_ss(self):
        mock.reset_mock()
        bt = BehaviorTree()
        bt.set_verbosity(1)
        bt.run(SimpleParallel, '"Dave"')
        mock('bt finished')
        print(mock.call_args_list)
        assert mock.call_args_list == [call('__init__ SimpleParallel'),
                                       call('__init__ SayHelloAction'),
                                       call('__init__ SayHelloAction'),
                                       call('on_tick - Alice'),
                                       call('__del__ SayHelloAction'),
                                       call('on_tick - Dave'),
                                       call('__del__ SayHelloAction'),
                                       call('__del__ SimpleParallel'),
                                       call('bt finished')]
        assert bt._instance.get_status() == NodeStatus.SUCCESS
        assert bt._instance.get_message() == ''

    def test_parallel_sf(self):
        mock.reset_mock()
        bt = BehaviorTree()
        bt.set_verbosity(2)
        bt.run(SimpleParallel, '"Chuck"')
        mock('bt finished')
        print(mock.call_args_list)
        assert mock.call_args_list == [call('__init__ SimpleParallel'),
                                       call('__init__ SayHelloAction'),
                                       call('__init__ SayHelloAction'),
                                       call('on_tick - Alice'),
                                       call('__del__ SayHelloAction'),
                                       call('on_tick - Chuck'),
                                       call('handle_name_is_chuck'),
                                       call('on_abort SimpleParallel'),
                                       call('__del__ SayHelloAction'),
                                       call('__del__ SimpleParallel'),
                                       call('bt finished')]
        assert bt._instance.get_status() == NodeStatus.ABORTED
        assert bt._instance.get_message() == 'WRONG_NAME'

    def test_tick_counting_parallel(self):
        mock.reset_mock()
        bt = BehaviorTree()
        bt.set_verbosity(2)
        bt.run(TickCountingParallel)
        mock('bt finished')
        print(mock.call_args_list)
        assert mock.call_args_list == [call('__init__ TickCountingParallel'),
                                       call('__init__ TickCountingAction'),
                                       call('__init__ EachThirdCountAction'),
                                       call('TickCountingAction - count: 1'),
                                       call('TickCountingAction - count: 2'),
                                       call('TickCountingAction - count: 3'),
                                       call('EachThirdCountAction - do action'),
                                       call('TickCountingAction - count: 4'),
                                       call('TickCountingAction - count: 5'),
                                       call('TickCountingAction - count: 6'),
                                       call('EachThirdCountAction - do action'),
                                       call('TickCountingAction - count: 7'),
                                       call('TickCountingAction - count: 8'),
                                       call('TickCountingAction - count: 9'),
                                       call('EachThirdCountAction - do action'),
                                       call('EachThirdCountAction - finished'),
                                       call('__del__ EachThirdCountAction'),
                                       call('__del__ TickCountingParallel'),
                                       call('__del__ TickCountingAction'),
                                       call('bt finished')]
        assert bt._instance.get_status() == NodeStatus.SUCCESS
        assert bt._instance.get_message() == ''