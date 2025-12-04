"""
Schema definitions for workflow automation.
"""

from naytrik.schema.actions import (
    ActionType,
    BaseAction,
    ClickAction,
    ExtractAction,
    GoBackAction,
    GoForwardAction,
    InputAction,
    KeyPressAction,
    NavigationAction,
    ScrollAction,
    SelectChangeAction,
)
from naytrik.schema.selectors import SelectorStrategy, SelectorType
from naytrik.schema.workflow import (
    WorkflowDefinition,
    WorkflowInputSchema,
    WorkflowMetadata,
    WorkflowStep,
)

__all__ = [
    # Actions
    "ActionType",
    "BaseAction",
    "ClickAction",
    "InputAction",
    "SelectChangeAction",
    "KeyPressAction",
    "NavigationAction",
    "ScrollAction",
    "GoBackAction",
    "GoForwardAction",
    "ExtractAction",
    # Selectors
    "SelectorStrategy",
    "SelectorType",
    # Workflow
    "WorkflowDefinition",
    "WorkflowStep",
    "WorkflowInputSchema",
    "WorkflowMetadata",
]
