"""
Automation module for AI-driven browser control.
"""

from naytrik.automation.agent import GeminiAutomation
from naytrik.automation.browser import BrowserState, IBrowser
from naytrik.automation.playwright_browser import PlaywrightBrowser

__all__ = [
    "GeminiAutomation",
    "IBrowser",
    "BrowserState",
    "PlaywrightBrowser",
]
