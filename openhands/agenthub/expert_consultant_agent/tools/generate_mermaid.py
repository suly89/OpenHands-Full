"""
GenerateMermaidDiagramAction tool.

This tool generates Mermaid diagrams from architecture or flow descriptions
provided by the LLM, formatting them as proper markdown code blocks.
"""

from litellm import ChatCompletionToolParam, ChatCompletionToolParamFunctionChunk

from openhands.events.action import Action

_THINK_DESCRIPTION = """Use the tool to generate Mermaid diagrams from architecture or flow descriptions.
The LLM provides the diagram content, and this tool formats it as a proper markdown code block.

Common use cases:
1. Creating architecture diagrams to visualize system components and their interactions
2. Generating flowcharts to illustrate processes and workflows
3. Producing sequence diagrams to show how components interact over time
4. Creating class diagrams to represent object-oriented designs
5. Visualizing state diagrams for finite state machines

The tool takes the raw diagram content from the LLM and returns it formatted as:
```
```mermaid
[LLM-provided content]
```
"""


class GenerateMermaidDiagramAction(Action):
    """Action to generate Mermaid diagrams from LLM-provided content."""

    name = 'generate_mermaid_diagram'
    description = 'Generate a Mermaid diagram from architecture or flow description'

    def run(self, input: str) -> str:
        """Formats the input as a Mermaid diagram markdown code block.

        Args:
            input (str): The Mermaid diagram content provided by the LLM

        Returns:
            str: Formatted markdown code block containing the Mermaid diagram
        """
        return f'```mermaid\n{input}\n```'


# Tool definition for LLM integration
GenerateMermaidDiagramTool = ChatCompletionToolParam(
    type='function',
    function=ChatCompletionToolParamFunctionChunk(
        name='generate_mermaid_diagram',
        description=_THINK_DESCRIPTION,
        parameters={
            'type': 'object',
            'properties': {
                'input': {
                    'type': 'string',
                    'description': 'The Mermaid diagram content to format.',
                },
            },
            'required': ['input'],
        },
    ),
)
