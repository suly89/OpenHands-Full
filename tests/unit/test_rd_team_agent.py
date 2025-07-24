import json
import os
from unittest.mock import MagicMock, patch

from openhands.agenthub.rd_team_agent.rd_team_agent import RDTeamAgent
from openhands.controller.state.state import State
from openhands.core.config import AgentConfig
from openhands.events.action.message import MessageAction
from openhands.llm.llm import LLM


def test_rd_team_agent_initialization():
    """Test that RDTeamAgent initializes correctly."""
    mock_llm = MagicMock(spec=LLM)
    config = AgentConfig()

    agent = RDTeamAgent(mock_llm, config)

    assert agent is not None
    assert hasattr(agent, 'pending_actions')
    assert hasattr(agent, 'conversation_memory')


def test_backlog_directory_creation():
    """Test that the backlog directory is created when tasks are added."""
    # Clean up any existing backlog directory
    backlog_dir = '/workspace/OpenHands-Full/.openhands/backlog'
    if os.path.exists(backlog_dir):
        import shutil

        shutil.rmtree(backlog_dir)

    from openhands.agenthub.rd_team_agent.tools.backlog import BacklogTool

    # Create a task - this should create the backlog directory
    task_file = BacklogTool.create_task(
        'test_task',
        'planning',
        'This is a test task',
        'Task should be completed successfully',
    )

    assert os.path.exists(backlog_dir), (
        f'Backlog directory {backlog_dir} was not created'
    )
    assert os.path.exists(task_file), f'Task file {task_file} was not created'

    # Clean up
    if os.path.exists(backlog_dir):
        import shutil

        shutil.rmtree(backlog_dir)


def test_task_creation():
    """Test that tasks are created correctly with proper JSON structure."""
    from openhands.agenthub.rd_team_agent.tools.backlog import BacklogTool

    # Clean up any existing backlog directory
    backlog_dir = '/workspace/OpenHands-Full/.openhands/backlog'
    if os.path.exists(backlog_dir):
        import shutil

        shutil.rmtree(backlog_dir)

    task_file = BacklogTool.create_task(
        'implement_feature',
        'development',
        'Implement user authentication feature',
        'Feature should allow users to login and logout',
    )

    assert os.path.exists(task_file)

    with open(task_file, 'r') as f:
        task_data = json.load(f)

    expected_keys = [
        'phase',
        'name',
        'description',
        'acceptance_criteria',
        'status',
        'created_by',
    ]
    for key in expected_keys:
        assert key in task_data, f'Task JSON missing required key: {key}'

    assert task_data['phase'] == 'development'
    assert task_data['name'] == 'implement_feature'
    assert task_data['description'] == 'Implement user authentication feature'
    assert (
        task_data['acceptance_criteria']
        == 'Feature should allow users to login and logout'
    )
    assert task_data['status'] == 'pending'
    assert task_data['created_by'] == 'RDTeamAgent'

    # Clean up
    if os.path.exists(backlog_dir):
        import shutil

        shutil.rmtree(backlog_dir)


def test_get_current_phase():
    """Test that the current phase is determined correctly."""
    agent = RDTeamAgent(MagicMock(), AgentConfig())

    # Test with no tasks (should return first default phase)
    with patch.object(agent, '_get_initial_user_message') as mock_msg:
        mock_msg.return_value = MessageAction(
            content='Start project',
        )
        current_phase = agent._get_current_phase(State())
        assert current_phase == 'planning'


def test_response_to_actions():
    """Test that LLM responses are converted to actions correctly."""
    from openhands.events.action.agent import AgentFinishAction

    mock_llm = MagicMock()
    mock_llm.config.max_message_chars = 4096
    mock_llm.vision_is_active.return_value = False
    mock_llm.is_caching_prompt_active.return_value = False

    agent = RDTeamAgent(mock_llm, AgentConfig())

    # Test normal message response
    class MockResponse:
        content = 'This is a test response'

    actions = agent.response_to_actions(MockResponse())
    assert len(actions) == 1
    assert isinstance(actions[0], MessageAction)
    assert actions[0].content == 'This is a test response'
    assert actions[0].source == 'agent'

    # Test finish action
    class MockFinishResponse:
        content = 'I am done'

    mock_llm.completion.return_value = MockFinishResponse()

    with patch('openhands.agenthub.rd_team_agent.rd_team_agent.AgentFinishAction'):
        actions = agent.response_to_actions(MockFinishResponse())
        assert any(isinstance(action, AgentFinishAction) for action in actions)


if __name__ == '__main__':
    test_rd_team_agent_initialization()
    test_backlog_directory_creation()
    test_task_creation()
    test_get_current_phase()
    test_response_to_actions()
    print('All tests passed!')
