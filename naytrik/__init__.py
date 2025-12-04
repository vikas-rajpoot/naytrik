"""
Gemini Workflow Automation

A modular browser automation framework combining Gemini Computer Use with
workflow recording and deterministic playback.
"""

__version__ = "1.0.0"

from naytrik.automation.agent import GeminiAutomation
from naytrik.playback.executor import WorkflowPlayer
from naytrik.recording.recorder import WorkflowRecorder
from naytrik.storage.manager import WorkflowStorage

__all__ = [
    "GeminiAutomation",
    "WorkflowPlayer",
    "WorkflowRecorder",
    "WorkflowStorage",
]
