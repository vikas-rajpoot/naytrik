"""
Action schema definitions for workflow steps.
"""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from naytrik.schema.selectors import ElementContext


class ActionType(str, Enum):
    """Types of actions that can be performed."""

    NAVIGATION = "navigation"
    CLICK = "click"
    INPUT = "input"
    SELECT_CHANGE = "select_change"
    KEY_PRESS = "key_press"
    SCROLL = "scroll"
    GO_BACK = "go_back"
    GO_FORWARD = "go_forward"
    EXTRACT = "extract"
    WAIT = "wait"


class BaseAction(BaseModel):
    """Base class for all actions."""

    type: str = Field(..., description="Type of action")
    description: Optional[str] = Field(None, description="Human-readable description of the action")
    output: Optional[str] = Field(None, description="Context key to store step output")
    wait_time: Optional[float] = Field(None, description="Time to wait after action (seconds)")

    # Verification
    verification_checks: Optional[List[Dict[str, Any]]] = Field(
        None, description="Verification checks to run after this step"
    )
    expected_outcome: Optional[str] = Field(None, description="Expected outcome description")

    class Config:
        use_enum_values = True
        extra = "allow"


class NavigationAction(BaseAction):
    """Navigate to a URL."""

    type: Literal["navigation"] = "navigation"
    url: str = Field(..., description="URL to navigate to")


class ClickAction(BaseAction):
    """Click an element."""

    type: Literal["click"] = "click"
    element: ElementContext = Field(..., description="Element to click")


class InputAction(BaseAction):
    """Input text into an element."""

    type: Literal["input"] = "input"
    element: ElementContext = Field(..., description="Element to input text into")
    value: str = Field(..., description="Text to input")
    default_value: Optional[str] = Field(None, description="Default value if value is empty")
    clear_before: bool = Field(default=True, description="Clear field before typing")
    press_enter: bool = Field(default=False, description="Press Enter after typing")


class SelectChangeAction(BaseAction):
    """Select an option from a dropdown."""

    type: Literal["select_change"] = "select_change"
    element: ElementContext = Field(..., description="Dropdown element")
    selected_text: str = Field(..., description="Visible text of option to select")


class KeyPressAction(BaseAction):
    """Press a key."""

    type: Literal["key_press"] = "key_press"
    element: Optional[ElementContext] = Field(None, description="Element to focus (optional)")
    key: str = Field(..., description="Key to press (e.g., 'Enter', 'Tab')")


class ScrollAction(BaseAction):
    """Scroll the page."""

    type: Literal["scroll"] = "scroll"
    scroll_x: int = Field(default=0, description="Horizontal scroll pixels")
    scroll_y: int = Field(..., description="Vertical scroll pixels")


class GoBackAction(BaseAction):
    """Navigate back in browser history."""

    type: Literal["go_back"] = "go_back"


class GoForwardAction(BaseAction):
    """Navigate forward in browser history."""

    type: Literal["go_forward"] = "go_forward"


class ExtractAction(BaseAction):
    """Extract content from page."""

    type: Literal["extract"] = "extract"
    extraction_goal: str = Field(..., description="What to extract from the page")


class WaitAction(BaseAction):
    """Wait for a specified duration."""

    type: Literal["wait"] = "wait"
    duration: float = Field(..., description="Duration to wait in seconds")


# Union of all action types
Action = Union[
    NavigationAction,
    ClickAction,
    InputAction,
    SelectChangeAction,
    KeyPressAction,
    ScrollAction,
    GoBackAction,
    GoForwardAction,
    ExtractAction,
    WaitAction,
]
