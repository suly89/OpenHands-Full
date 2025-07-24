import os
from collections import deque
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from openhands.events.action import Action
    from openhands.llm.llm import ModelResponse

from openhands.agenthub.rd_team_agent.tools.backlog import BacklogTool
from openhands.controller.agent import Agent
from openhands.controller.state.state import State
from openhands.core.config import AgentConfig
from openhands.core.logger import openhands_logger as logger
from openhands.core.message import Message, TextContent
from openhands.events.action.agent import AgentFinishAction, AgentFinishTaskCompleted
from openhands.events.action.message import MessageAction
from openhands.events.event import Event, EventSource
from openhands.llm.llm import LLM
from openhands.llm.llm_utils import check_tools
from openhands.memory.conversation_memory import ConversationMemory
from openhands.utils.prompt import PromptManager


class RDTeamAgent(Agent):
    VERSION = '1.0'
    """
    The RD Team Agent is a comprehensive agent that functions as a complete R&D team.
    It coordinates multiple roles (Coordinator, Product Owner, Architect, Developer,
    Tester, Validator) to autonomously progress through development phases, validate
    each phase, and generate tasks in the `.openhands/backlog` folder.

    ## Overview

    This agent implements a multi-role coordination system that:
    1. **Plans**: Defines project scope, features, and milestones
    2. **Architects**: Designs system architecture and components
    3. **Develops**: Implements features with code quality focus
    4. **Tests**: Validates functionality through comprehensive testing
    5. **Validates**: Ensures each phase meets quality standards before progression

    ## Key Features

    - **Autonomous operation**: Moves through phases independently
    - **Backlog management**: Generates tasks in `.openhands/backlog`
    - **Phase validation**: Validates completion before progressing
    - **Test coverage**: Ensures comprehensive test coverage
    """

    def __init__(
        self,
        llm: LLM,
        config: AgentConfig,
    ) -> None:
        """Initializes a new instance of the RDTeamAgent class.

        Parameters:
        - llm (LLM): The language model to be used by this agent
        - config (AgentConfig): The configuration for this agent
        """
        super().__init__(llm, config)

        self.pending_actions: deque['Action'] = deque()
        # Create a ConversationMemory instance
        self.conversation_memory = ConversationMemory(self.config, self.prompt_manager)

    @property
    def prompt_manager(self) -> PromptManager:
        if self._prompt_manager is None:
            self._prompt_manager = PromptManager(
                prompt_dir=os.path.join(os.path.dirname(__file__), 'prompts'),
                system_prompt_filename=self.config.system_prompt_filename,
            )
        return self._prompt_manager

    def reset(self) -> None:
        """Resets the RDTeamAgent's internal state."""
        super().reset()
        # Only clear pending actions, not LLM metrics
        self.pending_actions.clear()

    def step(self, state: State) -> 'Action':
        """Performs one step using the RDTeamAgent.

        This includes gathering info on previous steps and prompting the model to make a decision
        about which role should take the next action (Coordinator, Product Owner, Architect,
        Developer, Tester, or Validator).

        Parameters:
        - state (State): used to get updated info

        Returns:
        - MessageAction(content) - Communication from any team role
        - AgentFinishAction() - end the interaction when complete
        """
        # Continue with pending actions if any
        if self.pending_actions:
            return self.pending_actions.popleft()

        # Check if we're done
        latest_user_message = state.get_last_user_message()
        if latest_user_message and latest_user_message.content.strip() == '/exit':
            return AgentFinishAction(
                final_thought='User requested exit',
                task_completed=AgentFinishTaskCompleted.TRUE,
            )

        # Get the current phase from state or initialize
        current_phase = self._get_current_phase(state)
        logger.info(f'Current phase: {current_phase}')

        # Handle requirements gathering phase specially
        if current_phase == 'requirements_gathering':
            return self._handle_requirements_gathering(state)

        # Process events and get messages for LLM
        condensed_history: list[Event] = []
        initial_user_message = self._get_initial_user_message(state.history)

        messages = self._get_messages(condensed_history, initial_user_message)
        params: dict = {
            'messages': self.llm.format_messages_for_llm(messages),
        }

        # Add phase information to the prompt
        if len(messages) > 0 and hasattr(messages[0], 'content'):
            original_content = messages[0].content
            combined_text = ''
            for item in original_content:
                if hasattr(item, 'text'):
                    combined_text += item.text + '\n'

            # Add phase information to the prompt
            current_phase = self._get_current_phase(state)
            phase_prompt = f"Current development phase: {current_phase}"
            combined_text += phase_prompt + '\n'
            messages[0].content = [TextContent(text=combined_text)]

        # Add tools and metadata like codeact_agent does
        params['tools'] = check_tools(self.tools, self.llm.config)
        params['extra_body'] = {'metadata': state.to_llm_metadata(agent_name=self.name)}
        response = self.llm.completion(**params)
        logger.debug(f'Response from LLM: {response}')
        action = self.response_to_actions(response)
        logger.debug(f'Action after response_to_actions: {action}')

        return action

    def _get_current_phase(self, state: State) -> str:
        """Determines the current development phase based on state history."""
        # Check for phase markers in the conversation history
        for event in reversed(state.history):
            if isinstance(event, MessageAction):
                content = event.content.lower()
                if 'phase:' in content:
                    parts = content.split('phase:')
                    if len(parts) > 1:
                        return parts[1].strip().split('\n')[0].strip()

        # Default phases in order
        default_phases = [
            'requirements_gathering',
            'planning',
            'architecture',
            'development',
            'testing',
            'validation',
        ]

        # Find the current phase based on backlog or state
        try:
            tasks = BacklogTool.get_backlog_tasks()
        except Exception as e:
            logger.warning(f'Error getting backlog tasks: {e}')
            return 'requirements_gathering'

        # Determine phase based on existing tasks - check in reverse order of phases
        if not tasks:
            return 'requirements_gathering'
        elif any('validation' in (t.get('phase', '') or '').lower() for t in tasks):
            return 'validation'
        elif any('testing' in (t.get('phase', '') or '').lower() for t in tasks):
            return 'testing'
        elif any('development' in (t.get('phase', '') or '').lower() for t in tasks):
            return 'development'
        elif any('architecture' in (t.get('phase', '') or '').lower() for t in tasks):
            return 'architecture'
        elif any('planning' in (t.get('phase', '') or '').lower() for t in tasks):
            return 'planning'

        # Return first phase if no tasks found
        return default_phases[0]

    def _get_initial_user_message(self, history: list[Event]) -> MessageAction:
        """Finds the initial user message action from the full history."""
        initial_user_message: MessageAction | None = None
        for event in history:
            if isinstance(event, MessageAction):
                initial_user_message = event
                break

        if initial_user_message is None:
            logger.error(
                f'CRITICAL: Could not find the initial user MessageAction in the full {len(history)} events history.'
            )
            raise ValueError(
                'Initial user message not found in history. Please report this issue.'
            )
        return initial_user_message

    def _handle_requirements_gathering(self, state: State) -> 'Action':
        """
        Handles the requirements gathering phase where Product Owner interacts with user.
        Returns appropriate actions based on the conversation context.
        """
        logger.info('Handling requirements gathering phase')

        # Check if we've already gathered requirements
        backlog_dir = '/workspace/OpenHands-Full/.openhands/backlog'
        os.makedirs(backlog_dir, exist_ok=True)

        # Look for existing requirements tasks
        requirements_tasks = []
        try:
            all_tasks = BacklogTool.get_backlog_tasks()
            requirements_tasks = [
                task
                for task in all_tasks
                if (task.get('phase', '').lower() == 'requirements_gathering')
            ]
        except Exception as e:
            logger.warning(f'Error getting backlog tasks: {e}')

        # If we already have requirements, move to planning
        if requirements_tasks:
            logger.info('Requirements already gathered, moving to next phase')
            return self._advance_to_planning_phase()

        # Start requirements gathering conversation
        user_messages = [
            e
            for e in state.history
            if isinstance(e, MessageAction) and e.source == 'user'
        ]

        # Always create a task for requirements gathering
        try:
            self.create_backlog_task(
                title='Gather Requirements',
                description='Collect user requirements for the project',
                phase='requirements_gathering',
                acceptance_criteria='User requirements have been collected and documented',
            )
        except Exception as e:
            logger.error(f'Failed to create requirements task: {e}')

        if not user_messages or 'requirements' not in user_messages[-1].content.lower():
            # Ask about requirements if we haven't started yet
            self.pending_actions.extend(
                [
                    MessageAction(
                        content='As the Product Owner, I need to understand your requirements before we start. Could you please describe what you need this project to accomplish? What are the key features and goals?',
                        source=EventSource.AGENT,
                    )
                ]
            )
            return self.pending_actions.popleft()

        # If user has provided some requirements, acknowledge and create task
        user_messages[-1].content

        # Create a backlog task for the requirements
        try:
            self.create_backlog_task(
                title='Gather Requirements',
                description='Collect user requirements for the project',
                phase='requirements_gathering',
                acceptance_criteria='User requirements have been collected and documented',
            )

            # Set pending actions for the next steps
            self.pending_actions.extend(
                [
                    MessageAction(
                        content='Thank you! I have created a task to gather your requirements.',
                        source=EventSource.AGENT,
                    ),
                    AgentFinishAction(
                        final_thought='Requirements gathering initiated',
                        task_completed=AgentFinishTaskCompleted.TRUE,
                    ),
                ]
            )
        except Exception as e:
            logger.error(f'Error creating requirements task: {e}')
            self.pending_actions.extend(
                [
                    MessageAction(
                        content=f'Thank you for providing those requirements. However, I encountered an error documenting them: {str(e)}',
                        source=EventSource.AGENT,
                    ),
                    AgentFinishAction(
                        final_thought='Requirements gathered but not documented due to error',
                        task_completed=AgentFinishTaskCompleted.FALSE,
                    ),
                ]
            )

        # Return the first pending action
        return self.pending_actions.popleft()

    def _advance_to_planning_phase(self) -> 'Action':
        """Advances from requirements gathering to planning phase."""
        logger.info('Advancing to planning phase')

        # Create a requirements task
        self.create_backlog_task(
            title='Gather Requirements',
            description='Collect user requirements for the project',
            phase='requirements_gathering',
            acceptance_criteria='User requirements have been collected and documented',
        )

        # Create a planning task
        self.create_backlog_task(
            title='Create Project Plan',
            description='Develop a project plan based on requirements',
            phase='planning',
            acceptance_criteria='Project plan is created with milestones and timelines',
        )

        self.pending_actions.extend(
            [
                MessageAction(
                    content="Requirements have been documented. Now moving to the planning phase where we'll define the project scope and roadmap.",
                    source=EventSource.AGENT,
                )
            ]
        )
        return self.pending_actions.popleft()

    def _get_messages(
        self, events: list[Event], initial_user_message: MessageAction
    ) -> list[Message]:
        """Constructs the message history for the LLM conversation."""
        if not self.prompt_manager:
            raise Exception('Prompt Manager not instantiated.')

        # Use ConversationMemory to process events (including SystemMessageAction)
        messages = self.conversation_memory.process_events(
            condensed_history=events,
            initial_user_action=initial_user_message,
            max_message_chars=self.llm.config.max_message_chars,
            vision_is_active=self.llm.vision_is_active(),
        )

        if self.llm.is_caching_prompt_active():
            self.conversation_memory.apply_prompt_caching(messages)

        return messages

    def create_backlog_task(
        self,
        title: str,
        description: str,
        phase: Optional[str] = None,
        status: str = 'not_started',
        acceptance_criteria: Optional[str] = None,
    ) -> str:
        """Creates a backlog task based on the current phase."""
        # Get current phase if not specified
        if phase is None:
            from openhands.controller.state.state import State
            phase = self._get_current_phase(State())

        return BacklogTool.create_backlog_task(
            title=title,
            description=description,
            phase=phase,
            status=status,
            acceptance_criteria=acceptance_criteria,
        )

    def response_to_actions(self, response: 'ModelResponse') -> 'Action':
        """Converts LLM response to actions."""
        # Simple implementation - in a real scenario this would be more complex

        content = response.content if hasattr(response, 'content') else str(response)

        # Check for finish signal
        if any(
            keyword in content.lower()
            for keyword in ['complete', 'finished', 'done', '/exit']
        ):
            self.pending_actions.extend(
                [
                    AgentFinishAction(
                        final_thought='Task completed',
                        task_completed=AgentFinishTaskCompleted.TRUE,
                    )
                ]
            )
            return self.pending_actions.popleft()

        # Create a message action with the LLM response

        self.pending_actions.extend(
            [MessageAction(content=content, source=EventSource.AGENT)]
        )
        return self.pending_actions.popleft()
