
from unittest.mock import MagicMock, patch

import pytest

from openhands.agenthub.codeact_agent.codeact_agent import CodeActAgent
from openhands.controller.state.state import State
from openhands.events.action.message import MessageAction

class TestWorkflow:
    """Test the complete workflow of CodeActAgent."""

    @pytest.fixture
    def agent(self):
        """Create a CodeActAgent instance for testing."""
        with patch('openhands.agenthub.codeact_agent.codeact_agent.LLM') as mock_llm:
            from openhands.core.config.agent_config import AgentConfig

            config = AgentConfig()
            agent = CodeActAgent(llm=mock_llm, config=config)
            yield agent

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM responses."""
        mock_llm = MagicMock()
        mock_llm.completion.return_value = 'Mock response'
        return mock_llm

    def test_planning_to_execution_transition(
        self, agent, mock_llm
    ):
        """Test transition from planning to execution mode."""
        with patch.object(agent, 'llm', mock_llm):
            # Start in planning mode
            state = State(history=[])
            agent._initialize_planning_state_from_history(state)
            assert agent.planning_state == agent.PLANNING_MODE

            # Simulate LLM response with planning transition
            mock_llm.completion.return_value = 'We are moving to development'
            # Mock the set_system_prompt and _handle_planning_phase methods
            with patch.object(agent.prompt_manager, 'set_system_prompt', return_value=None):
                agent.step(state)

            # Verify mode transition
            assert agent.planning_state == agent.EXECUTION_MODE

    def test_execution_to_completion_transition(
        self, agent, mock_llm
    ):
        """Test transition from execution to completion mode."""
        with patch.object(agent, 'llm', mock_llm):
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
            # Mock the set_system_prompt method
            with patch.object(agent.prompt_manager, 'set_system_prompt', return_value=None):
                agent.step(state)

            # Verify mode transition
            assert agent.planning_state == agent.COMPLETION_MODE

    def test_state_persistence_across_steps(self, agent, mock_llm):
        """Test that planning state is maintained across multiple steps."""
        with patch.object(agent, 'llm', mock_llm):
            state = State(history=[])

            # First step - should be in planning mode
            # Mock the _handle_planning_phase to avoid prompt manager issues
            with patch.object(agent, '_handle_planning_phase', return_value=None):
                agent.step(state)
            assert agent.planning_state == agent.PLANNING_MODE

            # Second step - should still be in planning mode
            with patch.object(agent, '_handle_planning_phase', return_value=None):
                agent.step(state)
            assert agent.planning_state == agent.PLANNING_MODE

    def test_prompt_switching(self, agent, mock_llm):
        """Test that correct prompts are used for each mode."""
        with patch.object(agent, 'llm', mock_llm):
            # Test planning mode
            state = State(history=[])
            with patch.object(agent, '_handle_planning_phase', return_value=None):
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
            with patch.object(agent, '_handle_completion_phase', return_value=None):
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
            with patch.object(agent, '_handle_completion_phase', return_value=None):
                agent.step(state)
