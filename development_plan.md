
# CodeAct Agent Planning Phase Implementation Plan

## Table of Contents
1. [Introduction](#introduction)
2. [Current Architecture Overview](#current-architecture-overview)
3. [Files to Modify](#files-to-modify)
4. [Implementation Strategy](#implementation-strategy)
5. [Detailed Implementation Plan](#detailed-implementation-plan)
6. [New Components](#new-components)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Plan](#deployment-plan)
9. [Rollback Strategy](#rollback-strategy)
10. [Conclusion](#conclusion)

## Introduction

This document outlines the implementation plan for adding a planning phase to the CodeAct Agent in OpenHands. The goal is to transform the agent from a reactive executor to a proactive collaborator by introducing a structured planning process before code execution.

## Current Architecture Overview

The CodeAct Agent consists of several key components:

- **Main Agent Class**: `CodeActAgent` in `codeact_agent.py`
- **Core Method**: `step()` method handles the main agent logic
- **State Management**: Uses `State` class for tracking conversation state
- **Prompt System**: `PromptManager` for managing system and user prompts
- **Action Execution**: Uses a queue system for managing actions
- **Function Calling**: `function_calling.py` converts LLM responses to actions

## Files to Modify

Based on the codebase exploration, the following files need modification:

1. **`/workspace/OpenHands-Full/openhands/agenthub/codeact_agent/codeact_agent.py`** - Main agent logic
2. **Prompt files in `/workspace/OpenHands-Full/openhands/agenthub/codeact_agent/prompts/`** - For planning-related prompts
3. **`/workspace/OpenHands-Full/openhands/agenthub/codeact_agent/function_calling.py`** - For handling planning-related actions (if needed)

## Implementation Strategy

The implementation will follow a layered approach:

1. **Add Planning State**: Introduce a new state to track when the agent is in planning mode
2. **Modify Core Logic**: Update the `step()` method to include planning phase detection
3. **Implement Planning Methods**: Add new methods for handling the planning process
4. **Update Prompts**: Extend existing prompts to support planning
5. **Add Progress Reporting**: Modify execution actions to report progress

## Detailed Implementation Plan

### Phase 1: Basic Integration (1-2 days)

1. **Add Planning State Constants**
   - Add `PLANNING_MODE = "planning"`
   - Add `EXECUTION_MODE = "execution"`
   - Add `COMPLETION_MODE = "completion"`

2. **Modify `step()` Method**
   - Add logic to detect mode transition keywords in LLM responses
   - Add logic to switch between planning, execution, and completion modes
   - Redirect to appropriate phase when needed

3. **Implement Mode Transition Methods**
   - `_handle_planning_phase()`: Main planning logic
   - `_handle_execution_phase()`: Main execution logic
   - `_handle_completion_phase()`: Handle post-execution tasks
   - `_detect_mode_transition()`: Checks for mode transition keywords in LLM responses

### Phase 2: Refinement (2-3 days)

1. **Improve Requirement Analysis**
   - Enhance the LLM prompts to better understand user requirements
   - Add validation for plan components

2. **Add Time Estimates**
   - Implement basic time estimation for tasks
   - Add progress tracking

3. **Implement Plan Modification Handling**
   - Add logic to handle user feedback and plan adjustments
   - Maintain plan versioning

### Phase 3: Optimization (1-2 days)

1. **Fine-tune Prompts**
   - Adjust prompts based on real usage data
   - Optimize for different types of development requests

2. **Optimize Request Type Detection**
   - Improve accuracy in identifying development vs. non-development requests
   - Add more sophisticated natural language processing

3. **Add User Satisfaction Metrics**
   - Implement feedback collection
   - Track plan approval times and iterations

## New Components

### 1. Planning State Management

```python
# Add to codeact_agent.py
PLANNING_MODE = "planning"
EXECUTION_MODE = "execution"
COMPLETION_MODE = "completion"

# Add to agent state
self.planning_state = EXECUTION_MODE  # Default to execution mode
```

### 2. Mode Transition Methods

```python
# Add to codeact_agent.py

def _detect_mode_transition(self, response_content: str) -> str:
    """Detect mode transition keywords in LLM responses."""
    # Check for planning mode transition
    if "moving to development" in response_content.lower():
        return self.EXECUTION_MODE
    # Check for completion mode transition
    elif "development complete" in response_content.lower():
        return self.COMPLETION_MODE
    # Default: stay in current mode
    return self.planning_state

def _handle_planning_phase(self, state: State) -> 'Action':
    """Handle the planning phase before execution."""
    self.planning_state = self.PLANNING_MODE

    # Continue with normal processing but with planning prompt
    return self._get_response(state)

def _handle_execution_phase(self, state: State) -> 'Action':
    """Handle the execution phase."""
    self.planning_state = self.EXECUTION_MODE

    # Continue with normal processing
    return self._get_response(state)

def _handle_completion_phase(self, state: State) -> 'Action':
    """Handle the completion phase."""
    self.planning_state = self.COMPLETION_MODE

    # Continue with normal processing but with completion prompt
    return self._get_response(state)
```

### 3. Dynamic Prompt Selection

```python
# Add to codeact_agent.py

def get_current_prompt(self):
    """Get the appropriate prompt based on current mode."""
    if self.planning_state == self.PLANNING_MODE:
        return self.prompt_manager.get_prompt('planning_prompt.j2')
    elif self.planning_state == self.COMPLETION_MODE:
        return self.prompt_manager.get_prompt('completion_prompt.j2')
    else:
        return self.prompt_manager.get_system_message()

# Update step method to handle mode transitions
def step(self, state: State) -> 'Action':
    # Get the last LLM response to check for mode transitions
    last_response = self._get_last_llm_response(state)
    if last_response:
        new_mode = self._detect_mode_transition(last_response.content)
        if new_mode != self.planning_state:
            # Switch to the new mode
            if new_mode == self.EXECUTION_MODE:
                return self._handle_execution_phase(state)
            elif new_mode == self.COMPLETION_MODE:
                return self._handle_completion_phase(state)

    # Continue with current mode
    if self.planning_state == self.PLANNING_MODE:
        return self._handle_planning_phase(state)
    elif self.planning_state == self.COMPLETION_MODE:
        return self._handle_completion_phase(state)
    else:
        return self._handle_execution_phase(state)
```

### 4. New Prompts

Create new prompt files with focused instructions:

1. **`planning_prompt.j2`** for planning mode:
   - Requirement analysis
   - Plan creation
   - Plan presentation
   - Approval detection
   - Mode transition instructions (e.g., "Moving to development")

2. **`completion_prompt.j2`** for completion mode:
   - Post-execution analysis
   - Testing and validation
   - Documentation generation
   - Mode transition instructions (e.g., "Development complete")

### 5. Updated Prompts

Add planning-related content to existing prompt files:
- `system_prompt.j2` (minimal changes)
- `user_prompt.j2` (if needed)
- New `planning_prompt.j2` for planning mode
- New `completion_prompt.j2` for completion mode

## Testing Strategy

1. **Unit Tests**: Test individual planning methods
2. **Integration Tests**: Test the complete planning flow
3. **User Acceptance Testing**: Validate with real users
4. **Regression Tests**: Ensure existing functionality still works

## Deployment Plan

1. **Development**: Implement features in a separate branch
2. **Testing**: Thorough testing in staging environment
3. **Code Review**: Peer review of all changes
4. **Documentation**: Update documentation to reflect new behavior
5. **Gradual Rollout**: Start with opt-in feature, then make it default

## Rollback Strategy

1. **Feature Flag**: Implement as an optional feature that can be disabled
2. **Backup**: Maintain backup of original `step()` method
3. **Database**: Store planning state separately for easy removal
4. **Monitoring**: Set up monitoring to detect issues early

## Technical Viability Analysis

### Compatibility Assessment

The proposed approach is technically viable and maintains backward compatibility because:

1. **Minimal Core Changes**: Only the `step()` method is modified to include planning detection
2. **State Management**: Planning state is tracked separately without affecting existing state management
3. **Prompt Separation**: Dynamic prompt selection ensures the LLM gets appropriate instructions for each mode
4. **Action Reuse**: Existing action types (`MessageAction`) are used for planning interactions
5. **Modular Design**: New functionality is added as separate components that don't interfere with existing ones

### Risk Assessment

1. **Low Risk**: Changes are isolated to the planning phase and don't affect core execution logic
2. **Backward Compatible**: Existing functionality remains unchanged when planning is disabled
3. **Testable**: Each component can be tested independently
4. **Reversible**: Changes can be easily rolled back if issues arise

### Implementation Feasibility

1. **Development Time**: Estimated 5-7 days for complete implementation
2. **Resource Requirements**: Minimal additional resources needed
3. **Dependency Impact**: No changes to external dependencies
4. **Integration Effort**: Seamless integration with existing agent architecture

## Conclusion

This implementation plan outlines a structured approach to adding a planning phase to the CodeAct Agent. The changes are designed to be minimal and non-invasive, maintaining backward compatibility while significantly improving the user experience. The phased approach allows for incremental development and testing, reducing risk while delivering high impact.

The technical viability analysis confirms that this approach is feasible, low-risk, and maintains full compatibility with existing functionality.
