"""
ExpertConsultantAgent module.

This module provides the ExpertConsultantAgent class, which acts as an expert consultant,
proposer, and modular documenter for software projects. It analyzes repositories,
gathers requirements, proposes architectures, and generates high-quality documentation
using LLM prompt orchestration and OpenHands tools.
"""

from openhands.agenthub.expert_consultant_agent.expert_consultant_agent import (
    ExpertConsultantAgent,
)
from openhands.agenthub.expert_consultant_agent.tools.generate_mermaid import (
    GenerateMermaidDiagramAction,
)
from openhands.agenthub.expert_consultant_agent.tools.validate_docs import (
    DocumentationValidatorAction,
)
from openhands.controller.agent import Agent

__all__ = [
    'ExpertConsultantAgent',
    'GenerateMermaidDiagramAction',
    'DocumentationValidatorAction',
]
Agent.register('ExpertConsultantAgent', ExpertConsultantAgent)
