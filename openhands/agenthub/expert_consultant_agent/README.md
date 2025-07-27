

# ExpertConsultantAgent

ExpertConsultantAgent is an OpenHands agent designed to act as an expert consultant, proposer, and modular documenter for software projects. It analyzes repositories, gathers requirements, proposes architectures, and generates high-quality documentation using LLM prompt orchestration and OpenHands tools.

## Features

- **Repository Analysis**: Analyzes code structure, dependencies, and tech stack
- **Requirement Gathering**: Asks structured questions to gather functional and technical requirements
- **Architecture Proposals**: Provides architectural and implementation recommendations
- **Documentation Generation**: Creates modular, well-structured documentation
- **Documentation Validation**: Validates document structure, completeness, and links
- **Diagram Generation**: Creates architecture diagrams using Mermaid

## Agent Structure

The agent follows OpenHands architectural principles:
- **Stateless, prompt-driven**: All logic embedded in system prompt
- **Tool-powered**: All actions performed through well-defined tools
- **Minimal agent class**: No custom orchestration logic

## Tools

The agent uses all existing CodeActAgent tools plus two custom tools:

1. **GenerateMermaidDiagramAction**: Formats Mermaid diagrams for architecture visualization
2. **DocumentationValidatorAction**: Validates document structure and completeness

## Configuration

The agent can be configured through the `consultant_agent_config.yml` file:

```yaml
agent_config:
  max_questions: 50
  documentation:
    template_style: "corporate"
    include_diagrams: true
    split_threshold_lines: 1000
```

## Integration

The agent integrates seamlessly with CodeActAgent through system prompt extension. Documents generated in `.openhands/microagents/` directory are automatically consumed by CodeActAgent for implementation.

## Testing

Tests are located in `tests/unit/test_expert_consultant_agent.py` and cover:
- Basic flow verification
- Document generation
- Tool usage
- Integration with CodeActAgent

## Implementation

The agent is implemented in `/openhands/agenthub/expert_consultant_agent/` and includes:
- `expert_consultant_agent.py`: Main agent class
- `tools/`: Custom tool implementations
- `prompts/`: System prompt templates
