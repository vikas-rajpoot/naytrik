"""
Browser abstraction interface for automation.

Following the Dependency Inversion Principle - high-level automation
logic depends on this abstraction, not concrete implementations.
"""

import abc
from typing import Any, Optional, Tuple

from pydantic import BaseModel


class BrowserState(BaseModel):
    """Current state of the browser."""

    screenshot: bytes
    url: str
    title: Optional[str] = None


class IBrowser(abc.ABC):
    """Abstract interface for browser operations."""

    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize the browser."""
        pass

    @abc.abstractmethod
    async def close(self) -> None:
        """Close the browser."""
        pass

    @abc.abstractmethod
    def screen_size(self) -> Tuple[int, int]:
        """Get the screen size (width, height)."""
        pass

    @abc.abstractmethod
    async def get_current_state(self) -> BrowserState:
        """Get current browser state (screenshot, URL, etc.)."""
        pass

    @abc.abstractmethod
    async def navigate(self, url: str) -> BrowserState:
        """Navigate to a URL."""
        pass

    @abc.abstractmethod
    async def click_at(self, x: int, y: int) -> BrowserState:
        """Click at coordinates."""
        pass

    @abc.abstractmethod
    async def hover_at(self, x: int, y: int) -> BrowserState:
        """Hover at coordinates."""
        pass

    @abc.abstractmethod
    async def type_text_at(
        self,
        x: int,
        y: int,
        text: str,
        press_enter: bool = False,
        clear_before_typing: bool = True,
    ) -> BrowserState:
        """Type text at coordinates."""
        pass

    @abc.abstractmethod
    async def scroll_document(self, direction: str) -> BrowserState:
        """Scroll the entire document."""
        pass

    @abc.abstractmethod
    async def scroll_at(
        self, x: int, y: int, direction: str, magnitude: int
    ) -> BrowserState:
        """Scroll at specific coordinates."""
        pass

    @abc.abstractmethod
    async def go_back(self) -> BrowserState:
        """Navigate back in history."""
        pass

    @abc.abstractmethod
    async def go_forward(self) -> BrowserState:
        """Navigate forward in history."""
        pass

    @abc.abstractmethod
    async def key_combination(self, keys: list[str]) -> BrowserState:
        """Press key combination."""
        pass

    @abc.abstractmethod
    async def drag_and_drop(
        self, x: int, y: int, destination_x: int, destination_y: int
    ) -> BrowserState:
        """Drag and drop from source to destination."""
        pass

    @abc.abstractmethod
    async def wait(self, seconds: float = 5.0) -> BrowserState:
        """Wait for specified seconds."""
        pass

    @abc.abstractmethod
    async def get_page(self) -> Optional[Any]:
        """Get the current page object for direct manipulation."""
        pass
