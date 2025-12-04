"""
Multi-strategy element finder for robust playback with coordinate fallback.
"""

from typing import Optional, Tuple, Union

from playwright.async_api import Locator, Page

from naytrik.schema.selectors import (
    CoordinateInfo,
    ElementContext,
    SelectorStrategy,
    SelectorType,
)


class ElementFinder:
    """
    Finds elements using multiple fallback strategies including coordinates.
    
    Follows Single Responsibility Principle: only handles element finding.
    """

    def __init__(self, page: Page, timeout_ms: int = 5000):
        """
        Initialize element finder.

        Args:
            page: Playwright page
            timeout_ms: Timeout for element finding
        """
        self.page = page
        self.timeout_ms = timeout_ms

    async def find_element(
        self, 
        context: ElementContext, 
        use_coordinates_fallback: bool = True
    ) -> Tuple[Union[Locator, Tuple[int, int]], str]:
        """
        Find element using multiple strategies with coordinate fallback.

        Args:
            context: Element context with selector strategies and optional coordinates
            use_coordinates_fallback: Whether to use coordinates as last resort

        Returns:
            Tuple of (locator_or_coords, strategy_used)
            - If found by selector: (Locator, "strategy_type:value")
            - If using coordinates: ((x, y), "coordinates")

        Raises:
            Exception if element not found with any strategy
        """
        # First try all selector strategies
        if context.selector_strategies:
            # Sort strategies by priority
            strategies = sorted(context.selector_strategies, key=lambda s: s.priority)

            errors = []

            for strategy in strategies:
                try:
                    locator = await self._try_strategy(strategy)
                    if locator:
                        # Verify element is visible
                        await locator.wait_for(state="visible", timeout=self.timeout_ms)
                        return locator, f"{strategy.type}:{strategy.value}"
                except Exception as e:
                    errors.append(f"{strategy.type}: {str(e)}")
                    continue

        # If all selectors failed, try coordinates as fallback
        if use_coordinates_fallback and context.coordinates:
            try:
                coords = self._get_absolute_coordinates(context.coordinates)
                # Verify coordinates are valid
                if coords[0] >= 0 and coords[1] >= 0:
                    return coords, "coordinates"
            except Exception as e:
                errors.append(f"coordinates: {str(e)}")

        # All strategies failed
        error_msg = f"Could not find element '{context.target_text}'."
        if context.selector_strategies:
            error_msg += f" Tried {len(context.selector_strategies)} selector strategies."
        if context.coordinates:
            error_msg += " Coordinate fallback also failed."
        if 'errors' in locals():
            error_msg += f" Errors: {'; '.join(errors)}"
        
        raise Exception(error_msg)

    async def _try_strategy(self, strategy: SelectorStrategy) -> Optional[Locator]:
        """Try a single selector strategy."""
        
        if strategy.type == SelectorType.ID:
            # ID selector
            return self.page.locator(f'#{strategy.value}').first
        
        elif strategy.type == SelectorType.NAME:
            # Name attribute selector
            return self.page.locator(f'[name="{strategy.value}"]').first
        
        elif strategy.type == SelectorType.DATA_ATTR:
            # Data attribute selector
            attr_name = strategy.metadata.get('attribute', 'data-testid')
            return self.page.locator(f'[{attr_name}="{strategy.value}"]').first
        
        elif strategy.type == SelectorType.TEXT_EXACT:
            # Exact text match
            tag = strategy.metadata.get('tag')
            if tag:
                return self.page.locator(tag).get_by_text(strategy.value, exact=True)
            return self.page.get_by_text(strategy.value, exact=True)

        elif strategy.type == SelectorType.TEXT_FUZZY:
            # Fuzzy text match
            tag = strategy.metadata.get('tag')
            if tag:
                return self.page.locator(tag).get_by_text(strategy.value, exact=False)
            return self.page.get_by_text(strategy.value, exact=False)

        elif strategy.type == SelectorType.ROLE_TEXT:
            # Role-based selector with text
            role = strategy.metadata.get('role')
            if role:
                return self.page.get_by_role(role, name=strategy.value)
            return None

        elif strategy.type == SelectorType.ARIA_LABEL:
            return self.page.get_by_label(strategy.value)

        elif strategy.type == SelectorType.PLACEHOLDER:
            return self.page.get_by_placeholder(strategy.value)

        elif strategy.type == SelectorType.TITLE:
            return self.page.get_by_title(strategy.value)

        elif strategy.type == SelectorType.ALT_TEXT:
            return self.page.get_by_alt_text(strategy.value)

        elif strategy.type == SelectorType.TEST_ID:
            return self.page.get_by_test_id(strategy.value)

        elif strategy.type == SelectorType.CSS:
            return self.page.locator(strategy.value).first

        elif strategy.type == SelectorType.XPATH:
            return self.page.locator(f"xpath={strategy.value}").first

        return None
    
    def _get_absolute_coordinates(self, coord_info: CoordinateInfo) -> Tuple[int, int]:
        """
        Get absolute coordinates, handling normalization if needed.
        
        Args:
            coord_info: Coordinate information
            
        Returns:
            Tuple of (x, y) absolute coordinates
        """
        # If we have absolute coordinates, use them
        if coord_info.x is not None and coord_info.y is not None:
            return (coord_info.x, coord_info.y)
        
        # If we have normalized coordinates, denormalize them
        if coord_info.normalized_x is not None and coord_info.normalized_y is not None:
            # Get current viewport size
            viewport = self.page.viewport_size
            if viewport:
                x = int(coord_info.normalized_x * viewport['width'] / 1000)
                y = int(coord_info.normalized_y * viewport['height'] / 1000)
                return (x, y)
        
        raise ValueError("No valid coordinates available")

    async def find_by_text(self, text: str, exact: bool = True) -> Locator:
        """Simple text-based element finding."""
        locator = self.page.get_by_text(text, exact=exact)
        await locator.wait_for(state="visible", timeout=self.timeout_ms)
        return locator

    async def find_by_css(self, selector: str) -> Locator:
        """Simple CSS selector finding."""
        locator = self.page.locator(selector).first
        await locator.wait_for(state="visible", timeout=self.timeout_ms)
        return locator
