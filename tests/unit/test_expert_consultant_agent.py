"""
Unit tests for ExpertConsultantAgent.
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from openhands.agenthub.expert_consultant_agent.expert_consultant_agent import (
    ExpertConsultantAgent,
)
from openhands.agenthub.expert_consultant_agent.tools.generate_mermaid import (
    GenerateMermaidDiagramAction,
)
from openhands.agenthub.expert_consultant_agent.tools.validate_docs import (
    DocumentationValidatorAction,
)
from openhands.core.config import AgentConfig
from openhands.events.action import MessageAction
from openhands.llm.llm import LLM


class TestExpertConsultantAgent:
    """Test cases for ExpertConsultantAgent."""

    def setup_method(self):
        """Set up test fixtures."""
        self.llm = Mock(spec=LLM)
        self.config = AgentConfig()
        self.config.system_prompt_filename = 'system_prompt.j2'
        self.config.enable_editor = True
        self.config.enable_cmd = True
        self.config.enable_think = True
        self.config.enable_finish = True
        self.config.enable_condensation_request = True
        self.config.enable_browsing = True
        self.config.enable_jupyter = True
        self.config.enable_llm_editor = True

        # Create a temporary directory for the agent's prompt files
        self.temp_dir = tempfile.mkdtemp()
        self.prompt_dir = os.path.join(self.temp_dir, 'prompts')
        os.makedirs(self.prompt_dir)

        # Copy the system prompt to the temp directory
        import shutil

        shutil.copy(
            '/workspace/OpenHands-Full/openhands/agenthub/expert_consultant_agent/prompts/system_prompt.j2',
            os.path.join(self.prompt_dir, 'system_prompt.j2'),
        )

        # Update the config to use the temp prompt directory
        self.config.prompt_dir = self.prompt_dir

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_agent_initialization(self):
        """Test that the agent initializes correctly."""
        agent = ExpertConsultantAgent(self.llm, self.config)

        assert agent is not None
        assert agent.pending_actions == []
        assert len(agent.tools) > 0  # Should have tools

        # Check that custom tools are included
        tool_names = [tool.get('function', {}).get('name') for tool in agent.tools]
        assert 'generate_mermaid_diagram' in tool_names
        assert 'validate_documentation' in tool_names

    def test_get_tools(self):
        """Test that the agent returns the correct tools."""
        agent = ExpertConsultantAgent(self.llm, self.config)
        tools = agent._get_tools()

        # Should have all CodeActAgent tools plus custom tools
        assert len(tools) > 0

        # Check for custom tools
        tool_names = [tool.get('function', {}).get('name') for tool in tools]
        assert 'generate_mermaid_diagram' in tool_names
        assert 'validate_documentation' in tool_names

    def test_generate_mermaid_diagram_action(self):
        """Test the GenerateMermaidDiagramAction tool."""
        action = GenerateMermaidDiagramAction()
        input_content = 'graph TD; A-->B; B-->C;'
        result = action.run(input_content)

        expected = '```mermaid\n' + input_content + '\n```'
        assert result == expected

    def test_documentation_validator_action(self):
        """Test the DocumentationValidatorAction tool."""
        action = DocumentationValidatorAction()
        input_path = '/path/to/docs'
        result = action.run(input_path)

        # Should return a structured validation result
        assert isinstance(result, dict)
        assert 'status' in result
        assert 'broken_links' in result
        assert 'missing' in result
        assert 'warnings' in result

    def test_agent_step_with_exit_command(self):
        """Test that the agent handles the exit command correctly."""
        agent = ExpertConsultantAgent(self.llm, self.config)

        # Mock state with exit command
        mock_state = Mock()
        mock_state.get_last_user_message.return_value = MessageAction(
            content='/exit', source='user'
        )

        action = agent.step(mock_state)

        # Should return a finish action
        from openhands.events.action import AgentFinishAction

        assert isinstance(action, AgentFinishAction)

    def test_agent_step_with_pending_actions(self):
        """Test that the agent processes pending actions correctly."""
        agent = ExpertConsultantAgent(self.llm, self.config)

        # Add a mock pending action
        mock_action = Mock()
        agent.pending_actions.append(mock_action)

        # Mock state
        mock_state = Mock()

        action = agent.step(mock_state)

        # Should return the pending action
        assert action == mock_action

    @patch(
        'openhands.agenthub.expert_consultant_agent.expert_consultant_agent.Condenser'
    )
    def test_agent_condensed_history(self, mock_condenser):
        """Test that the agent handles condensed history correctly."""
        agent = ExpertConsultantAgent(self.llm, self.config)

        # Mock state and events
        mock_state = Mock()
        mock_event = Mock()
        mock_state.history = [mock_event]

        # Mock condensed history
        mock_condenser.from_config.return_value.condensed_history.return_value = Mock()

        # Mock initial user message
        mock_initial_msg = MessageAction(content='Test', source='user')
        with patch.object(agent, '_get_initial_user_message') as mock_get_initial:
            mock_get_initial.return_value = mock_initial_msg

            # Mock messages
            with patch.object(agent, '_get_messages') as mock_get_messages:
                mock_get_messages.return_value = []

                # Mock LLM response and actions
                mock_response = Mock()
                agent.llm.completion.return_value = mock_response
                with patch.object(
                    agent, 'response_to_actions'
                ) as mock_response_to_actions:
                    mock_response_to_actions.return_value = []

                    agent.step(mock_state)

                    # Should call all the expected methods
                    mock_condenser.from_config.assert_called_once()
                    mock_get_initial.assert_called_once()
                    mock_get_messages.assert_called_once()
                    agent.llm.completion.assert_called_once()
                    mock_response_to_actions.assert_called_once()


if __name__ == '__main__':
    pytest.main()
