from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from openhands.agenthub.codeact_agent.codeact_agent import CodeActAgent
from openhands.controller.state.state import State
from openhands.core.config.condenser_config import NoOpCondenserConfig
from openhands.events.action.message import MessageAction


class TestWorkflow:
    """Test the complete workflow of CodeActAgent."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        mock_llm = MagicMock()
        mock_config = MagicMock()
        mock_config.system_prompt_filename = 'system_prompt.j2'
        mock_config.condenser = NoOpCondenserConfig()
        agent = CodeActAgent(mock_llm, mock_config)
        yield agent

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM responses."""
        mock_llm = MagicMock()
        mock_llm.completion.return_value = 'Mock response'
        return mock_llm

    @pytest.fixture
    def mock_prompt_manager(self):
        """Mock prompt manager."""
        mock_manager = MagicMock()
        return mock_manager

    def test_planning_to_execution_transition(
        self, agent, mock_llm, mock_prompt_manager
    ):
        """Test transition from planning to execution mode."""
        with (
            patch.object(agent, 'llm', mock_llm),
            patch(
                'openhands.agenthub.codeact_agent.codeact_agent.CodeActAgent._prompt_manager',
                new_callable=lambda: PropertyMock(return_value=mock_prompt_manager),
            ),
        ):
            # Start in planning mode
            state = State(history=[])
            agent._initialize_planning_state_from_history(state)
            assert agent.planning_state == agent.PLANNING_MODE

            # Simulate LLM response with planning transition
            mock_llm.completion.return_value = 'We are moving to development'
            agent.step(state)

            # Verify mode transition
            assert agent.planning_state == agent.EXECUTION_MODE

    def test_execution_to_completion_transition(
        self, agent, mock_llm, mock_prompt_manager
    ):
        """Test transition from execution to completion mode."""
        with (
            patch.object(agent, 'llm', mock_llm),
            patch(
                'openhands.agenthub.codeact_agent.codeact_agent.CodeActAgent._prompt_manager',
                new_callable=lambda: PropertyMock(return_value=mock_prompt_manager),
            ),
        ):
            # Start in execution mode
            state = State(
                history=[
                    MessageAction(
                        content='We are moving to development',
                    )
                ]
            )
            state.history[0]._source = 'agent'
            agent._initialize_planning_state_from_history(state)
            assert agent.planning_state == agent.EXECUTION_MODE

            # Simulate LLM response with completion transition
            mock_llm.completion.return_value = 'Development complete'
            agent.step(state)

            # Verify mode transition
            assert agent.planning_state == agent.COMPLETION_MODE

    def test_state_persistence_across_steps(self, agent, mock_llm, mock_prompt_manager):
        """Test that planning state is maintained across multiple steps."""
        with (
            patch.object(agent, 'llm', mock_llm),
            patch(
                'openhands.agenthub.codeact_agent.codeact_agent.CodeActAgent._prompt_manager',
                new_callable=lambda: PropertyMock(return_value=mock_prompt_manager),
            ),
        ):
            state = State(history=[])

            # First step - should be in planning mode
            agent.step(state)
            assert agent.planning_state == agent.PLANNING_MODE

            # Second step - should transition to execution
            mock_llm.completion.return_value = 'We are moving to development'
            agent.step(state)
            assert agent.planning_state == agent.EXECUTION_MODE

            # Third step - should transition to completion
            mock_llm.completion.return_value = 'Development complete'
            agent.step(state)
            assert agent.planning_state == agent.COMPLETION_MODE

            # Verify state is maintained
            assert agent.planning_state == agent.COMPLETION_MODE

    def test_prompt_switching(self, agent, mock_llm, mock_prompt_manager):
        """Test that correct prompts are used for each mode."""
        with (
            patch.object(agent, 'llm', mock_llm),
            patch(
                'openhands.agenthub.codeact_agent.codeact_agent.CodeActAgent._prompt_manager',
                new_callable=lambda: PropertyMock(return_value=mock_prompt_manager),
            ),
        ):
            # Test planning mode
            state = State(history=[])
            agent.step(state)

            # Test execution mode
            state = State(
                history=[
                    MessageAction(
                        content='We are moving to development',
                    )
                ]
            )
            state.history[0]._source = 'agent'
            agent.step(state)

            # Test completion mode
            state = State(
                history=[
                    MessageAction(
                        content='We are moving to development',
                    ),
                    MessageAction(
                        content='Development complete',
                    ),
                ]
            )
            state.history[0]._source = 'agent'
            state.history[1]._source = 'agent'
            agent.step(state)
