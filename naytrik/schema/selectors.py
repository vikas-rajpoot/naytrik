"""
Selector strategy definitions for robust element finding.
"""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SelectorType(str, Enum):
    """Types of selector strategies for element finding."""

    TEXT_EXACT = "text_exact"
    TEXT_FUZZY = "text_fuzzy"
    ROLE_TEXT = "role_text"
    ARIA_LABEL = "aria_label"
    PLACEHOLDER = "placeholder"
    TITLE = "title"
    ALT_TEXT = "alt_text"
    CSS = "css"
    XPATH = "xpath"
    TEST_ID = "test_id"
    ID = "id"
    NAME = "name"
    DATA_ATTR = "data_attr"
    COORDINATES = "coordinates"


class SelectorStrategy(BaseModel):
    """A single selector strategy with priority and metadata."""

    type: SelectorType = Field(..., description="Type of selector strategy")
    value: str = Field(..., description="The selector value")
    priority: int = Field(..., description="Priority order (lower = higher priority)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the selector")

    class Config:
        use_enum_values = True


class CoordinateInfo(BaseModel):
    """Stores x,y coordinates for coordinate-based interaction fallback."""
    
    x: int = Field(..., description="Absolute X coordinate where action occurred")
    y: int = Field(..., description="Absolute Y coordinate where action occurred")
    normalized_x: Optional[float] = Field(None, description="Normalized X coordinate (0-1000)")
    normalized_y: Optional[float] = Field(None, description="Normalized Y coordinate (0-1000)")
    screen_width: Optional[int] = Field(None, description="Screen width when recorded")
    screen_height: Optional[int] = Field(None, description="Screen height when recorded")
    bounding_box: Optional[Dict[str, float]] = Field(None, description="Element bounding box {x, y, width, height}")


class ElementContext(BaseModel):
    """Context information about an element for robust identification."""

    # Primary identification
    target_text: str = Field(..., description="Visible or accessible text to identify the element")

    # Multiple selector strategies (ordered by priority)
    selector_strategies: list[SelectorStrategy] = Field(
        default_factory=list, description="List of fallback selector strategies"
    )

    # Coordinate-based fallback (for when selectors fail)
    coordinates: Optional[CoordinateInfo] = Field(
        None, 
        description="X,Y coordinates as fallback when selectors fail or for AI-driven execution"
    )

    # Context hints for disambiguation
    container_hint: Optional[str] = Field(None, description="Container context hint")
    position_hint: Optional[str] = Field(None, description="Position hint for repeated elements")
    interaction_type: Optional[str] = Field(None, description="Expected interaction type")

    # Element metadata (informational)
    element_tag: Optional[str] = Field(None, description="HTML tag name")
    element_attributes: Optional[Dict[str, str]] = Field(None, description="Element attributes")

    # Page context
    page_url: Optional[str] = Field(None, description="URL where element was found")
    page_title: Optional[str] = Field(None, description="Page title")

    def get_primary_selector(self) -> Optional[SelectorStrategy]:
        """Get the highest priority selector strategy."""
        if not self.selector_strategies:
            return None
        return min(self.selector_strategies, key=lambda s: s.priority)

    def get_css_selector(self) -> Optional[str]:
        """Get CSS selector if available."""
        for strategy in self.selector_strategies:
            if strategy.type == SelectorType.CSS:
                return strategy.value
        return None

    def get_xpath_selector(self) -> Optional[str]:
        """Get XPath selector if available."""
        for strategy in self.selector_strategies:
            if strategy.type == SelectorType.XPATH:
                return strategy.value
        return None
    
    def get_coordinates(self) -> Optional[CoordinateInfo]:
        """Get coordinate information if available."""
        return self.coordinates
    
    def has_selectors(self) -> bool:
        """Check if element has any selector strategies."""
        return len(self.selector_strategies) > 0
    
    def has_coordinates(self) -> bool:
        """Check if element has coordinate information."""
        return self.coordinates is not None


    def get_primary_selector(self) -> Optional[SelectorStrategy]:
        """Get the highest priority selector strategy."""
        if not self.selector_strategies:
            return None
        return min(self.selector_strategies, key=lambda s: s.priority)

    def get_css_selector(self) -> Optional[str]:
        """Get CSS selector if available."""
        for strategy in self.selector_strategies:
            if strategy.type == SelectorType.CSS:
                return strategy.value
        return None

    def get_xpath_selector(self) -> Optional[str]:
        """Get XPath selector if available."""
        for strategy in self.selector_strategies:
            if strategy.type == SelectorType.XPATH:
                return strategy.value
        return None
