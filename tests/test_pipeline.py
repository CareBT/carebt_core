from tests.global_mock import mock

from unittest.mock import call

from carebt.actionNode import ActionNode
from carebt.behaviorTree import BehaviorTree
from carebt.nodeStatus import NodeStatus
from carebt.pipelineSequenceNode import PipelineSequenceNode


success_queue = []

########################################################################


class HelloWorldAction(ActionNode):

    def __init__(self, bt):
        super().__init__(bt)
        mock('__init__ {}'.format(self.__class__.__name__))

    def on_tick(self) -> None:
        mock('HelloWorldAction: Hello World !!!')
        self.set_status(NodeStatus.SUCCESS)

    def __del__(self):
        mock('__del__ {}'.format(self.__class__.__name__))

########################################################################


class MultiTickHelloWorldAction(ActionNode):

    def __init__(self, bt):
        super().__init__(bt, '?success')
        self._success = 0
        self.attempts = 1
        mock('__init__ {}'.format(self.__class__.__name__))

    def on_tick(self) -> None:
        self.set_status(NodeStatus.RUNNING)
        mock('MultiTickHelloWorldAction: Hello World ... '
             'takes several ticks ... (attempts = {}/{})'
             .format(self.attempts, self._success))
        if(self.attempts % self._success == 0):
            self.attempts = 1
            if(success_queue.pop(0)):
                mock('MultiTickHelloWorldAction: Hello World DONE !!!')
                self.set_status(NodeStatus.SUCCESS)
            else:
                mock('MultiTickHelloWorldAction: Hello World FAILURE !!!')
                self.set_status(NodeStatus.FAILURE)
                self.set_message('HELLO_FAILS')
        else:
            self.attempts += 1

    def __del__(self):
        mock('__del__ {}'.format(self.__class__.__name__))

########################################################################


class ExamplePipelineSequence(PipelineSequenceNode):

    def __init__(self, bt):
        super().__init__(bt)
        self.set_period_ms(500)
        self.set_max_cycles(3)
        self.add_child(HelloWorldAction)
        self.add_child(MultiTickHelloWorldAction, '2')
        self.add_child(MultiTickHelloWorldAction, '3')
        mock('__init__ {}'.format(self.__class__.__name__))

    def __del__(self):
        mock('__del__ {}'.format(self.__class__.__name__))

########################################################################


class TestPipelineSequenceNode:

    def test_pipeline_sequence_tt(self):
        mock.reset_mock()
        success_queue.clear()
        success_queue.append(True)
        success_queue.append(True)
        bt = BehaviorTree()
        bt.run(ExamplePipelineSequence)
        mock('bt finished')
        print(mock.call_args_list)
        assert mock.call_args_list == [call('__init__ ExamplePipelineSequence'),  # noqa: E501
                                       call('__init__ HelloWorldAction'),  # noqa: E501
                                       call('HelloWorldAction: Hello World !!!'),  # noqa: E501
                                       call('__init__ MultiTickHelloWorldAction'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 1/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 2/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World DONE !!!'),  # noqa: E501
                                       call('__init__ MultiTickHelloWorldAction'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 1/3)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 2/3)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 3/3)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World DONE !!!'),  # noqa: E501

                                       call('__del__ HelloWorldAction'),  # noqa: E501
                                       call('__del__ MultiTickHelloWorldAction'),  # noqa: E501
                                       call('__del__ MultiTickHelloWorldAction'),  # noqa: E501
                                       call('__del__ ExamplePipelineSequence'),  # noqa: E501
                                       call('bt finished')  # noqa: E501
                                       ]
        assert bt._instance.get_status() == NodeStatus.SUCCESS
        assert bt._instance.get_message() == ''

    def test_pipeline_sequence_ftt(self):
        mock.reset_mock()
        success_queue.append(False)
        success_queue.append(True)
        success_queue.append(True)
        bt = BehaviorTree()
        bt.run(ExamplePipelineSequence)
        mock('bt finished')
        print(mock.call_args_list)
        assert mock.call_args_list == [call('__init__ ExamplePipelineSequence'),  # noqa: E501,
                                       call('__init__ HelloWorldAction'),  # noqa: E501
                                       call('HelloWorldAction: Hello World !!!'),  # noqa: E501
                                       call('__init__ MultiTickHelloWorldAction'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 1/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 2/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World FAILURE !!!'),  # noqa: E501
                                       call('HelloWorldAction: Hello World !!!'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 1/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 2/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World DONE !!!'),  # noqa: E501
                                       call('__init__ MultiTickHelloWorldAction'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 1/3)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 2/3)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 3/3)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World DONE !!!'),  # noqa: E501

                                       call('__del__ HelloWorldAction'),  # noqa: E501
                                       call('__del__ MultiTickHelloWorldAction'),  # noqa: E501
                                       call('__del__ MultiTickHelloWorldAction'),  # noqa: E501
                                       call('__del__ ExamplePipelineSequence'),  # noqa: E501
                                       call('bt finished')  # noqa: E501
                                       ]
        assert bt._instance.get_status() == NodeStatus.SUCCESS
        assert bt._instance.get_message() == ''

    def test_pipeline_sequence_ftftt(self):
        mock.reset_mock()
        success_queue.append(False)
        success_queue.append(True)
        success_queue.append(False)
        success_queue.append(True)
        success_queue.append(True)
        bt = BehaviorTree()
        bt.run(ExamplePipelineSequence)
        mock('bt finished')
        print(mock.call_args_list)
        assert mock.call_args_list == [call('__init__ ExamplePipelineSequence'),  # noqa: E501
                                       call('__init__ HelloWorldAction'),  # noqa: E501
                                       call('HelloWorldAction: Hello World !!!'),  # noqa: E501
                                       call('__init__ MultiTickHelloWorldAction'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 1/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 2/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World FAILURE !!!'),  # noqa: E501

                                       call('HelloWorldAction: Hello World !!!'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 1/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 2/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World DONE !!!'),  # noqa: E501
                                       call('__init__ MultiTickHelloWorldAction'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 1/3)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 2/3)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 3/3)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World FAILURE !!!'),  # noqa: E501

                                       call('HelloWorldAction: Hello World !!!'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 1/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 2/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World DONE !!!'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 1/3)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 2/3)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 3/3)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World DONE !!!'),  # noqa: E501

                                       call('__del__ HelloWorldAction'),  # noqa: E501
                                       call('__del__ MultiTickHelloWorldAction'),  # noqa: E501
                                       call('__del__ MultiTickHelloWorldAction'),  # noqa: E501
                                       call('__del__ ExamplePipelineSequence'),  # noqa: E501
                                       call('bt finished')  # noqa: E501
                                       ]
        assert bt._instance.get_status() == NodeStatus.SUCCESS
        assert bt._instance.get_message() == ''

    def test_pipeline_sequence_fff(self):
        mock.reset_mock()
        success_queue.clear()
        success_queue.append(False)
        success_queue.append(False)
        success_queue.append(False)
        bt = BehaviorTree()
        bt.run(ExamplePipelineSequence)
        mock('bt finished')
        print(mock.call_args_list)
        assert mock.call_args_list == [call('__init__ ExamplePipelineSequence'),  # noqa: E501
                                       call('__init__ HelloWorldAction'),  # noqa: E501
                                       call('HelloWorldAction: Hello World !!!'),  # noqa: E501
                                       call('__init__ MultiTickHelloWorldAction'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 1/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 2/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World FAILURE !!!'),  # noqa: E501

                                       call('HelloWorldAction: Hello World !!!'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 1/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 2/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World FAILURE !!!'),  # noqa: E501

                                       call('HelloWorldAction: Hello World !!!'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 1/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World ... takes several ticks ... (attempts = 2/2)'),  # noqa: E501
                                       call('MultiTickHelloWorldAction: Hello World FAILURE !!!'),  # noqa: E501

                                       call('__del__ HelloWorldAction'),  # noqa: E501
                                       call('__del__ MultiTickHelloWorldAction'),  # noqa: E501
                                       call('__del__ ExamplePipelineSequence'),  # noqa: E501
                                       call('bt finished')  # noqa: E501
                                       ]
        assert bt._instance.get_status() == NodeStatus.FAILURE
        assert bt._instance.get_message() == 'HELLO_FAILS'