
# CodeAct Agent Test Plan

## Overview
This test plan covers the new planning mode functionality for the CodeAct agent. The tests are organized into three categories:
- **Unit Tests**: Test individual components and methods
- **Integration Tests**: Test interactions between components
- **End-to-End (E2E) Tests**: Test the complete agent workflow

## Test Categories

### 1. Unit Tests
**Location**: `/workspace/OpenHands-Full/tests/unit/codeact_agent/`

**Test Cases**:
1. **Mode Transition Detection**
   - Test `_detect_mode_transition()` with various inputs
   - Verify correct mode transitions based on keywords

2. **State Initialization**
   - Test `_initialize_planning_state_from_history()` with empty history
   - Test with history containing mode transition keywords

3. **Prompt Management**
   - Test prompt switching based on planning state
   - Verify correct prompt is used for each mode

4. **Helper Methods**
   - Test `_get_last_llm_response()` with various history scenarios

### 2. Integration Tests
**Location**: `/workspace/OpenHands-Full/tests/integration/codeact_agent/`

**Test Cases**:
1. **Mode Transition Workflow**
   - Test complete workflow from planning to execution to completion
   - Verify prompt switching during transitions

2. **State Persistence**
   - Test that planning state is correctly maintained across steps
   - Verify state initialization works with historical conversations

3. **LLM Interaction**
   - Mock LLM responses and test agent behavior
   - Verify correct actions are generated for each mode

### 3. End-to-End Tests
**Location**: `/workspace/OpenHands-Full/tests/e2e/codeact_agent/`

**Test Cases**:
1. **New Conversation Flow**
   - Test agent starts in planning mode with no history
   - Verify transition to execution mode after planning

2. **Existing Conversation Flow**
   - Test agent initializes from historical conversation
   - Verify correct mode based on last transition keyword

3. **Complete Development Cycle**
   - Test full cycle: planning → execution → completion
   - Verify all mode transitions and prompt usage

## Mocking Strategy
- **LLM Model**: Mock the LLM model to return predictable responses
- **State**: Use mock state objects with controlled history
- **Tools**: Mock tool execution to avoid side effects

## Expected Results
- All unit tests should pass with 100% coverage
- Integration tests should verify correct workflow execution
- E2E tests should demonstrate complete, functional agent behavior

## Test Implementation
Each test file should:
1. Import necessary modules and mocks
2. Set up test fixtures
3. Define test cases with assertions
4. Clean up after tests

## Test Execution
Tests can be run using:
```bash
# Run all tests
pytest tests/unit/codeact_agent/ tests/integration/codeact_agent/ tests/e2e/codeact_agent/

# Run specific test category
pytest tests/unit/codeact_agent/
pytest tests/integration/codeact_agent/
pytest tests/e2e/codeact_agent/
```
