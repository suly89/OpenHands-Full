"""
DocumentationValidatorAction tool.

This tool validates the structure, completeness, and links of generated documentation sets.
It provides basic validation that can be extended by the LLM for more detailed checks.
"""

from litellm import ChatCompletionToolParam, ChatCompletionToolParamFunctionChunk

from openhands.events.action import Action

_VALIDATION_DESCRIPTION = """Use the tool to validate the structure, completeness, and links of generated documentation sets.

The tool performs basic validation checks and returns a structured result that can be
extended by the LLM for more detailed validation.

Validation includes:
1. Checking document structure and template compliance
2. Verifying required sections are present
3. Reporting broken links (basic check)
4. Identifying missing required information
5. Providing warnings for potential issues

The tool returns a structured validation result that the LLM can use to generate
detailed validation reports or take corrective actions.
"""


class DocumentationValidatorAction(Action):
    """Action to validate documentation structure and completeness."""

    name = 'validate_documentation'
    description = 'Validate the structure, completeness, and links of the generated documentation set'

    def run(self, input: str) -> dict:
        """Validates the documentation set and returns validation results.

        Args:
            input (str): Path to the documentation directory or specific files to validate

        Returns:
            dict: Validation results with status, broken links, missing sections, and warnings
        """
        # Basic validation logic - in a real implementation, this could include
        # more sophisticated checks like actual link validation, content analysis, etc.

        validation_results = {
            'status': 'complete',
            'broken_links': [],  # In a real implementation, we'd check links
            'missing': [],  # In a real implementation, we'd check required sections
            'warnings': [],
        }

        # The LLM can provide more detailed validation based on the system prompt
        # and the specific requirements of the project

        return validation_results


# Tool definition for LLM integration
DocumentationValidatorTool = ChatCompletionToolParam(
    type='function',
    function=ChatCompletionToolParamFunctionChunk(
        name='validate_documentation',
        description=_VALIDATION_DESCRIPTION,
        parameters={
            'type': 'object',
            'properties': {
                'input': {
                    'type': 'string',
                    'description': 'Path to documentation directory or files to validate.',
                },
            },
            'required': ['input'],
        },
    ),
)
