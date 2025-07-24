#!/usr/bin/env python3

"""
Test script for RDTeamAgent
"""

import json
import os

from openhands.agenthub.rd_team_agent.tools.backlog import BacklogTool


def test_backlog_tool():
    """Test the BacklogTool functionality"""
    print('Testing BacklogTool...')

    # Create a test task
    task_file = BacklogTool.create_backlog_task(
        title='Test Task',
        description='This is a test task for validation',
        phase='testing',
        acceptance_criteria='Task should be created successfully',
    )

    print(f'Created task at: {task_file}')

    # Verify the task was created
    with open(task_file, 'r') as f:
        task_data = json.load(f)
        assert task_data['title'] == 'Test Task'
        assert task_data['phase'] == 'testing'
        print('✓ Task creation successful')

    # Test getting all tasks
    tasks = BacklogTool.get_backlog_tasks()
    assert len(tasks) >= 1
    print(f'✓ Found {len(tasks)} backlog tasks')

    # Test getting tasks by phase
    testing_tasks = BacklogTool.get_tasks_by_phase('testing')
    assert len(testing_tasks) >= 1
    print(f'✓ Found {len(testing_tasks)} testing tasks')

    # Test updating task status
    success = BacklogTool.update_task_status('Test Task', 'completed')
    assert success is True
    print('✓ Task status update successful')

    # Verify the update
    with open(task_file, 'r') as f:
        updated_task = json.load(f)
        assert updated_task['status'] == 'completed'
        print('✓ Task status verification successful')

    print('All BacklogTool tests passed!')


def test_agent_initialization():
    """Test RDTeamAgent initialization"""
    print('\nTesting RDTeamAgent initialization...')

    # This is a basic test - in a real scenario we'd need to mock the LLM
    try:
        from openhands.core.config.agent_config import AgentConfig

        # Create a minimal config with required attributes
        config = AgentConfig()
        config.system_prompt_filename = 'system.prompt.yaml'

        print('✓ RDTeamAgent initialization test skipped (requires proper LLM setup)')

    except Exception as e:
        print(f'✗ Failed to initialize RDTeamAgent: {e}')
        raise


def test_backlog_directory():
    """Test backlog directory creation and structure"""
    print('\nTesting backlog directory...')

    backlog_dir = '/workspace/OpenHands-Full/.openhands/backlog'
    if not os.path.exists(backlog_dir):
        os.makedirs(backlog_dir)
        print('✓ Created backlog directory')

    # List contents
    files = os.listdir(backlog_dir)
    print(f'Backlog directory contains {len(files)} items: {files}')


if __name__ == '__main__':
    test_backlog_directory()
    test_backlog_tool()
    test_agent_initialization()

    print('\nAll tests completed successfully!')
