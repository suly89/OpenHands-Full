from unittest.mock import patch

import pytest

from openhands.agenthub.codeact_agent.codeact_agent import CodeActAgent
from openhands.controller.state.state import State
from openhands.events.action.message import MessageAction


class TestModeTransition:
    """Test mode transition functionality in CodeActAgent."""

    @pytest.fixture
    def agent(self):
        """Create a CodeActAgent instance for testing."""
        with patch('openhands.agenthub.codeact_agent.codeact_agent.LLM') as mock_llm:
            from openhands.core.config.agent_config import AgentConfig

            config = AgentConfig()
            agent = CodeActAgent(llm=mock_llm, config=config)
            yield agent

    def test_detect_mode_transition_planning(self, agent):
        """Test detection of planning mode transition."""
        result = agent._detect_mode_transition('We are moving to development')
        assert result == agent.EXECUTION_MODE

    def test_detect_mode_transition_completion(self, agent):
        """Test detection of completion mode transition."""
        result = agent._detect_mode_transition('Development complete')
        assert result == agent.COMPLETION_MODE

    def test_detect_mode_transition_no_change(self, agent):
        """Test no mode change when no keywords found."""
        result = agent._detect_mode_transition('Regular development message')
        assert result == agent.planning_state

    def test_initialize_planning_state_empty_history(self, agent):
        """Test planning state initialization with empty history."""
        state = State(history=[])
        agent._initialize_planning_state_from_history(state)
        assert agent.planning_state == agent.PLANNING_MODE

    def test_initialize_planning_state_execution(self, agent):
        """Test planning state initialization with execution keyword."""
        state = State(
            history=[
                MessageAction(
                    content='We are moving to development',
                )
            ]
        )
        agent._initialize_planning_state_from_history(state)
        assert agent.planning_state == agent.EXECUTION_MODE

    def test_initialize_planning_state_completion(self, agent):
        """Test planning state initialization with completion keyword."""
        state = State(
            history=[
                MessageAction(
                    content='Development complete',
                )
            ]
        )
        agent._initialize_planning_state_from_history(state)
        assert agent.planning_state == agent.COMPLETION_MODE

    def test_initialize_planning_state_default(self, agent):
        """Test planning state initialization with no keywords."""
        state = State(
            history=[
                MessageAction(
                    content='Regular message',
                )
            ]
        )
        agent._initialize_planning_state_from_history(state)
        assert agent.planning_state == agent.PLANNING_MODE

    def test_get_last_llm_response_found(self, agent):
        """Test getting the last LLM response when found."""
        state = State(
            history=[
                MessageAction(
                    content='User message',
                ),
                MessageAction(
                    content='Agent response',
                ),
            ]
        )
        state.history[0]._source = 'user'
        state.history[1]._source = 'agent'
        result = agent._get_last_llm_response(state)
        assert result.content == 'Agent response'
        assert result.source == 'agent'

    def test_get_last_llm_response_not_found(self, agent):
        """Test getting the last LLM response when not found."""
        state = State(
            history=[
                MessageAction(
                    content='User message',
                )
            ]
        )
        state.history[0]._source = 'user'
        result = agent._get_last_llm_response(state)
        assert result is None
