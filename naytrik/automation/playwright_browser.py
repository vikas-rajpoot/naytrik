"""
Playwright implementation of the browser interface.
"""

import asyncio
from typing import Optional, Tuple

from playwright.async_api import Browser, Page, async_playwright

from naytrik.automation.browser import BrowserState, IBrowser


class PlaywrightBrowser(IBrowser):
    """
    Playwright-based browser implementation.
    
    Follows Liskov Substitution Principle: can be used wherever IBrowser is expected.
    """

    def __init__(
        self,
        screen_size: Tuple[int, int] = (1366, 768),
        headless: bool = False,
        initial_url: Optional[str] = None,
    ):
        """
        Initialize Playwright browser.

        Args:
            screen_size: Browser window size (width, height)
            headless: Run in headless mode
            initial_url: Optional URL to navigate to on init
        """
        self._screen_size = screen_size
        self._headless = headless
        self._initial_url = initial_url

        self._playwright = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None

    async def initialize(self) -> None:
        """Initialize the browser."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self._headless,
        )

        context = await self._browser.new_context(
            viewport={"width": self._screen_size[0], "height": self._screen_size[1]},
        )

        self._page = await context.new_page()

        if self._initial_url:
            await self._page.goto(self._initial_url)
            await self._page.wait_for_load_state()

    async def close(self) -> None:
        """Close the browser."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    def screen_size(self) -> Tuple[int, int]:
        """Get screen size."""
        return self._screen_size

    async def get_current_state(self) -> BrowserState:
        """Get current browser state."""
        assert self._page is not None, "Browser not initialized"
        screenshot = await self._page.screenshot()
        url = self._page.url
        title = await self._page.title()

        return BrowserState(
            screenshot=screenshot,
            url=url,
            title=title,
        )

    async def navigate(self, url: str) -> BrowserState:
        """Navigate to a URL."""
        assert self._page is not None, "Browser not initialized"
        await self._page.goto(url, wait_until="domcontentloaded")
        await self._page.wait_for_load_state()
        # Reduced from 0.5s to 0.1s
        await asyncio.sleep(0.1)
        return await self.get_current_state()

    async def click_at(self, x: int, y: int) -> BrowserState:
        """Click at specific coordinates."""
        assert self._page is not None, "Browser not initialized"
        await self._page.mouse.click(x, y)
        # Reduced from 0.3s to 0.1s
        await asyncio.sleep(0.1)
        return await self.get_current_state()

    async def hover_at(self, x: int, y: int) -> BrowserState:
        """Hover at coordinates."""
        assert self._page is not None, "Browser not initialized"
        await self._page.mouse.move(x, y)
        # Reduced from 0.2s to 0.05s
        await asyncio.sleep(0.05)
        return await self.get_current_state()

    async def type_text_at(
        self,
        x: int,
        y: int,
        text: str,
        press_enter: bool = False,
        clear_before_typing: bool = True,
    ) -> BrowserState:
        """Type text at coordinates."""
        assert self._page is not None, "Browser not initialized"
        # Click to focus
        await self._page.mouse.click(x, y)
        # Reduced from 0.2s to 0.05s
        await asyncio.sleep(0.05)

        # Clear if needed
        if clear_before_typing:
            await self._page.keyboard.press("Control+A")
            await self._page.keyboard.press("Delete")

        # Type text
        await self._page.keyboard.type(text)

        # Press enter if requested
        if press_enter:
            await self._page.keyboard.press("Enter")

        # Reduced from 0.3s to 0.1s
        await asyncio.sleep(0.1)
        return await self.get_current_state()

    async def scroll_document(self, direction: str) -> BrowserState:
        """Scroll the entire document."""
        assert self._page is not None, "Browser not initialized"
        scroll_amount = 500
        if direction == "down":
            await self._page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        elif direction == "up":
            await self._page.evaluate(f"window.scrollBy(0, -{scroll_amount})")
        elif direction == "right":
            await self._page.evaluate(f"window.scrollBy({scroll_amount}, 0)")
        elif direction == "left":
            await self._page.evaluate(f"window.scrollBy(-{scroll_amount}, 0)")

        # Reduced from 0.3s to 0.1s
        await asyncio.sleep(0.1)
        return await self.get_current_state()

    async def scroll_at(
        self, x: int, y: int, direction: str, magnitude: int
    ) -> BrowserState:
        """Scroll at specific coordinates."""
        assert self._page is not None, "Browser not initialized"
        # Move mouse to position
        await self._page.mouse.move(x, y)

        # Calculate scroll delta
        delta_x = 0
        delta_y = 0

        if direction == "down":
            delta_y = magnitude
        elif direction == "up":
            delta_y = -magnitude
        elif direction == "right":
            delta_x = magnitude
        elif direction == "left":
            delta_x = -magnitude

        # Perform scroll
        await self._page.mouse.wheel(delta_x, delta_y)

        # Reduced from 0.3s to 0.1s
        await asyncio.sleep(0.1)
        return await self.get_current_state()

    async def go_back(self) -> BrowserState:
        """Navigate back."""
        assert self._page is not None, "Browser not initialized"
        await self._page.go_back(wait_until="domcontentloaded")
        await self._page.wait_for_load_state()
        # Reduced from 0.5s to 0.2s (keep slightly longer for navigation)
        await asyncio.sleep(0.2)
        return await self.get_current_state()

    async def go_forward(self) -> BrowserState:
        """Navigate forward."""
        assert self._page is not None, "Browser not initialized"
        await self._page.go_forward(wait_until="domcontentloaded")
        await self._page.wait_for_load_state()
        # Reduced from 0.5s to 0.2s (keep slightly longer for navigation)
        await asyncio.sleep(0.2)
        return await self.get_current_state()

    async def key_combination(self, keys: list[str]) -> BrowserState:
        """Press key combination."""
        assert self._page is not None, "Browser not initialized"
        # Press keys in sequence
        for key in keys:
            await self._page.keyboard.down(key)

        # Release in reverse order
        for key in reversed(keys):
            await self._page.keyboard.up(key)

        # Reduced from 0.2s to 0.05s
        await asyncio.sleep(0.05)
        return await self.get_current_state()

    async def drag_and_drop(
        self, x: int, y: int, destination_x: int, destination_y: int
    ) -> BrowserState:
        """Drag and drop."""
        assert self._page is not None, "Browser not initialized"
        await self._page.mouse.move(x, y)
        await self._page.mouse.down()
        await self._page.mouse.move(destination_x, destination_y)
        await self._page.mouse.up()

        # Reduced from 0.5s to 0.2s
        await asyncio.sleep(0.2)
        return await self.get_current_state()

    async def wait(self, seconds: float = 5.0) -> BrowserState:
        """Wait for specified seconds."""
        await asyncio.sleep(seconds)
        return await self.get_current_state()

    async def get_page(self):
        """Get the current page object for direct manipulation."""
        return self._page

    async def __aenter__(self):
        """Context manager support."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager support."""
        await self.close()
