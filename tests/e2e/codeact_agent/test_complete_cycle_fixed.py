from unittest.mock import MagicMock, patch

import pytest

from openhands.agenthub.codeact_agent.codeact_agent import CodeActAgent
from openhands.controller.state.state import State
from openhands.events.action.agent import AgentFinishAction
from openhands.events.action.message import MessageAction
from openhands.events.event import EventSource


class TestCompleteCycle:
    """Test complete development cycle of CodeActAgent."""

    def _patch_prompt_manager(self, agent):
        """Helper to patch the prompt manager for testing."""
        original_prompt_manager = agent.prompt_manager
        return patch.object(original_prompt_manager, 'set_system_prompt')

    def _set_user_message_source(self, state):
        """Helper to set the source of user messages in the state."""
        for message in state.history:
            if isinstance(message, MessageAction) and message.content == 'User request':
                message._source = EventSource.USER

    @pytest.fixture
    def agent(self):
        """Create a CodeActAgent instance for testing."""
        from openhands.agenthub.codeact_agent import codeact_agent
        from openhands.core.config.agent_config import AgentConfig

        # Patch the PromptManager class at the module level
        with patch.object(codeact_agent, 'PromptManager') as mock_prompt_manager_class:
            # Set up the mock prompt manager first
            mock_prompt_manager = MagicMock()
            mock_prompt_manager.set_system_prompt = MagicMock(return_value=None)
            # Configure get_system_message to return a string
            mock_prompt_manager.get_system_message = MagicMock(
                return_value='System prompt content'
            )
            mock_prompt_manager_class.return_value = mock_prompt_manager

            with patch(
                'openhands.agenthub.codeact_agent.codeact_agent.LLM'
            ) as mock_llm:
                config = AgentConfig()
                agent = CodeActAgent(llm=mock_llm, config=config)
                yield agent

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM responses."""
        from litellm import ModelResponse

        mock_llm = MagicMock()

        # Create a proper ModelResponse mock
        def create_response(content):
            return ModelResponse(
                id='mock-id',
                choices=[
                    {
                        'message': {
                            'content': content,
                            'role': 'assistant',
                        },
                        'index': 0,
                        'finish_reason': 'stop',
                    }
                ],
            )

        # Set up side_effect to return different responses
        mock_llm.completion.side_effect = [
            create_response("Let's start planning the development"),  # Planning
            create_response('We are moving to development'),  # Transition to execution
            create_response('Executing the development steps'),  # Execution
            create_response('Development complete'),  # Transition to completion
            create_response('Finalizing the development'),  # Completion
        ]
        return mock_llm

    @pytest.fixture
    def mock_prompt_manager(self):
        """Mock PromptManager."""
        mock_manager = MagicMock()
        mock_manager.set_system_prompt = MagicMock(return_value=None)
        # Configure get_system_message to return a string
        mock_manager.get_system_message = MagicMock(
            return_value='System prompt content'
        )
        return mock_manager

    def test_new_conversation_starts_in_planning(
        self, agent, mock_llm, mock_prompt_manager
    ):
        """Test that new conversations start in planning mode."""
        # Patch the set_system_prompt method directly on the agent's prompt_manager
        original_prompt_manager = agent.prompt_manager
        with patch.object(
            original_prompt_manager, 'set_system_prompt'
        ) as mock_set_system_prompt:
            mock_set_system_prompt.return_value = None

            with patch.object(agent, 'llm', mock_llm):
                # The mock LLM is already configured in the fixture to return a proper ModelResponse

                state = State(history=[MessageAction(content='User request')])
                state.history[0]._source = 'user'

                # Check the source
                assert state.history[0].source == 'user'

                # Check what get_system_message returns
                system_message = agent.prompt_manager.get_system_message()
                assert system_message == 'System prompt content'

                agent.step(state)

                # Verify starts in planning mode
                assert agent.planning_state == agent.PLANNING_MODE
                assert mock_set_system_prompt.call_count == 1
                mock_set_system_prompt.assert_called_with('planning_prompt.j2')

    def test_existing_conversation_initializes_correctly(
        self, agent, mock_llm, mock_prompt_manager
    ):
        """Test that existing conversations initialize from history."""
        with patch.object(agent, 'llm', mock_llm):
            # Test conversation in execution mode
            state = State(
                history=[
                    MessageAction(content='User request'),
                    MessageAction(
                        content='We are moving to development',
                    ),
                ]
            )
            state.history[0]._source = 'user'

            with self._patch_prompt_manager(agent) as mock_set_system_prompt:
                mock_set_system_prompt.return_value = None
                agent.step(state)

                assert agent.planning_state == agent.EXECUTION_MODE
                assert mock_set_system_prompt.call_count == 1
                mock_set_system_prompt.assert_called_with('system_prompt.j2')

            # Test conversation in completion mode
            state = State(
                history=[
                    MessageAction(
                        content='User request',
                    ),
                    MessageAction(
                        content='We are moving to development',
                    ),
                    MessageAction(
                        content='Development complete',
                    ),
                ]
            )
            state.history[0]._source = 'user'

            with self._patch_prompt_manager(agent) as mock_set_system_prompt:
                mock_set_system_prompt.return_value = None
                agent.step(state)

                assert agent.planning_state == agent.COMPLETION_MODE
                assert mock_set_system_prompt.call_count == 1
                mock_set_system_prompt.assert_called_with('completion_prompt.j2')

    def test_complete_development_cycle(self, agent, mock_llm, mock_prompt_manager):
        """Test complete development cycle: planning → execution → completion."""
        with patch.object(agent, 'llm', mock_llm):
            # The mock LLM is already configured to return a proper ModelResponse

            # Step 1: Planning phase
            state = State(history=[MessageAction(content='User request')])
            state.history[0]._source = 'user'

            with self._patch_prompt_manager(agent) as mock_set_system_prompt:
                mock_set_system_prompt.return_value = None
                agent.step(state)
                assert agent.planning_state == agent.PLANNING_MODE
                assert mock_set_system_prompt.call_count == 1
                mock_set_system_prompt.assert_called_with('planning_prompt.j2')

            # Step 2: Transition to execution
            state = State(
                history=[
                    MessageAction(content='User request'),
                    MessageAction(
                        content="Let's start planning the development",
                    ),
                ]
            )
            state.history[0]._source = 'user'

            with self._patch_prompt_manager(agent) as mock_set_system_prompt:
                mock_set_system_prompt.return_value = None
                agent.step(state)
                assert agent.planning_state == agent.EXECUTION_MODE
                assert mock_set_system_prompt.call_count == 1
                mock_set_system_prompt.assert_called_with('system_prompt.j2')

            # Step 3: Execution phase
            state = State(
                history=[
                    MessageAction(content='User request'),
                    MessageAction(
                        content="Let's start planning the development",
                    ),
                    MessageAction(
                        content='We are moving to development',
                    ),
                ]
            )
            state.history[0]._source = 'user'

            with self._patch_prompt_manager(agent) as mock_set_system_prompt:
                mock_set_system_prompt.return_value = None
                agent.step(state)
                assert agent.planning_state == agent.EXECUTION_MODE

            # Step 4: Transition to completion
            state = State(
                history=[
                    MessageAction(content='User request'),
                    MessageAction(
                        content="Let's start planning the development",
                    ),
                    MessageAction(
                        content='We are moving to development',
                    ),
                    MessageAction(
                        content='Executing the development steps',
                    ),
                ]
            )
            state.history[0]._source = 'user'

            with self._patch_prompt_manager(agent) as mock_set_system_prompt:
                mock_set_system_prompt.return_value = None
                agent.step(state)
                assert agent.planning_state == agent.COMPLETION_MODE
                assert mock_set_system_prompt.call_count == 1
                mock_set_system_prompt.assert_called_with('completion_prompt.j2')

            # Step 5: Completion phase
            state = State(
                history=[
                    MessageAction(content='User request'),
                    MessageAction(
                        content="Let's start planning the development",
                    ),
                    MessageAction(
                        content='We are moving to development',
                    ),
                    MessageAction(
                        content='Executing the development steps',
                    ),
                    MessageAction(
                        content='Development complete',
                    ),
                ]
            )
            state.history[0]._source = 'user'

            with self._patch_prompt_manager(agent) as mock_set_system_prompt:
                mock_set_system_prompt.return_value = None
                agent.step(state)
                assert agent.planning_state == agent.COMPLETION_MODE

    def test_exit_command_handling(self, agent, mock_llm, mock_prompt_manager):
        """Test that /exit command is handled correctly in all modes."""
        with patch.object(agent, 'llm', mock_llm):
            # Test in planning mode
            state = State(history=[MessageAction(content='User request')])
            state.history[0]._source = 'user'
            latest_message = MessageAction(
                content='/exit',
            )
            state.history.append(latest_message)

            with self._patch_prompt_manager(agent) as mock_set_system_prompt:
                mock_set_system_prompt.return_value = None
                action = agent.step(state)
                assert isinstance(action, AgentFinishAction)

            # Test in execution mode
            state = State(
                history=[
                    MessageAction(content='User request'),
                    MessageAction(
                        content='We are moving to development',
                    ),
                ]
            )
            state.history[0]._source = 'user'
            latest_message = MessageAction(
                content='/exit',
            )
            state.history.append(latest_message)

            with self._patch_prompt_manager(agent) as mock_set_system_prompt:
                mock_set_system_prompt.return_value = None
                action = agent.step(state)
                assert isinstance(action, AgentFinishAction)

            # Test in completion mode
            state = State(
                history=[
                    MessageAction(content='User request'),
                    MessageAction(
                        content='We are moving to development',
                    ),
                    MessageAction(
                        content='Development complete',
                    ),
                ]
            )
            state.history[0]._source = 'user'
            latest_message = MessageAction(
                content='/exit',
            )
            state.history.append(latest_message)

            with self._patch_prompt_manager(agent) as mock_set_system_prompt:
                mock_set_system_prompt.return_value = None
                action = agent.step(state)
                assert isinstance(action, AgentFinishAction)
