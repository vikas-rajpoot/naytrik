"""
Workflow recorder that captures automation actions with robust selectors and coordinates.
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from naytrik.schema.actions import (
    Action,
    ActionType,
    ClickAction,
    ExtractAction,
    GoBackAction,
    GoForwardAction,
    InputAction,
    KeyPressAction,
    NavigationAction,
    ScrollAction,
    SelectChangeAction,
    WaitAction,
)
from naytrik.schema.selectors import (
    CoordinateInfo,
    ElementContext,
    SelectorStrategy,
)
from naytrik.schema.workflow import (
    WorkflowDefinition,
    WorkflowStep,
)
from naytrik.recording.selector_generator import SelectorGenerator


class WorkflowRecorder:
    """
    Records automation actions into a workflow definition with robust selectors and coordinates.
    
    Follows Single Responsibility Principle: only handles recording.
    Follows Open/Closed Principle: extensible for new action types.
    """

    def __init__(
        self,
        workflow_name: str,
        description: str,
        record_screenshots: bool = False,
        screen_width: int = 1366,
        screen_height: int = 768,
    ):
        """
        Initialize the workflow recorder.

        Args:
            workflow_name: Name for the workflow
            description: Description of what the workflow does
            record_screenshots: Whether to store screenshots
            screen_width: Browser screen width (for coordinate normalization)
            screen_height: Browser screen height (for coordinate normalization)
        """
        self.workflow_name = workflow_name
        self.description = description
        self.record_screenshots = record_screenshots
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.steps: List[WorkflowStep] = []
        self.step_counter = 0
        self.start_time = time.time()

        # Optional data storage
        self.screenshots: List[bytes] = []
        self.reasoning_log: List[str] = []
        
        # Selector generator for robust element identification
        self.selector_generator = SelectorGenerator()

    async def record_action(
        self,
        action_type: ActionType,
        element_context: Optional[ElementContext] = None,
        parameters: Optional[Dict[str, Any]] = None,
        reasoning: Optional[str] = None,
        screenshot: Optional[bytes] = None,
    ) -> None:
        """
        Record an action to the workflow.

        Args:
            action_type: Type of action being recorded
            element_context: Element information (for element-based actions)
            parameters: Action parameters
            reasoning: AI reasoning for this action
            screenshot: Optional screenshot
        """
        self.step_counter += 1
        params = parameters or {}

        # Create the appropriate action object
        action = self._create_action(action_type, element_context, params, reasoning)

        # Create workflow step
        step = WorkflowStep(
            step_number=self.step_counter,
            action=action,
        )

        self.steps.append(step)

        # Store optional data
        if reasoning:
            self.reasoning_log.append(f"Step {self.step_counter}: {reasoning}")

        if screenshot and self.record_screenshots:
            self.screenshots.append(screenshot)
    
    async def record_action_with_details(
        self,
        action_type: ActionType,
        element_data: Optional[Dict[str, Any]] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        parameters: Optional[Dict[str, Any]] = None,
        reasoning: Optional[str] = None,
        screenshot: Optional[bytes] = None,
    ) -> None:
        """
        Record an action with comprehensive element data including selectors and coordinates.

        Args:
            action_type: Type of action being recorded
            element_data: Dictionary with element information:
                - tag_name: HTML tag
                - text: Visible text
                - attributes: Dict of element attributes
                - css_selector: Optional pre-computed CSS selector
                - xpath: Optional pre-computed XPath
            x: X coordinate where action occurred (absolute pixels)
            y: Y coordinate where action occurred (absolute pixels)
            parameters: Action parameters
            reasoning: AI reasoning for this action
            screenshot: Optional screenshot
        """
        element_context = None
        
        if element_data or (x is not None and y is not None):
            # Generate robust selector strategies
            selector_strategies = []
            if element_data:
                selector_strategies = self.selector_generator.generate_strategies(
                    element_data,
                    include_xpath_fallback=True,
                    include_css_fallback=True,
                )
            
            # Create coordinate info if coordinates provided
            coordinate_info = None
            if x is not None and y is not None:
                coordinate_info = CoordinateInfo(
                    x=x,
                    y=y,
                    normalized_x=int(x / self.screen_width * 1000),
                    normalized_y=int(y / self.screen_height * 1000),
                    screen_width=self.screen_width,
                    screen_height=self.screen_height,
                    bounding_box=element_data.get('bounding_box') if element_data else None,
                )
            
            # Extract text and context
            text = element_data.get('text', '') if element_data else f"Element at ({x}, {y})"
            
            # Create enhanced element context
            element_context = ElementContext(
                target_text=text or reasoning or "Element",
                selector_strategies=selector_strategies,
                coordinates=coordinate_info,
                container_hint=None,
                position_hint=None,
                interaction_type=None,
                element_tag=element_data.get('tag_name') if element_data else None,
                element_attributes=element_data.get('attributes') if element_data else None,
                page_url=parameters.get('url') if parameters else None,
                page_title=None,
            )
        
        # Record using the standard method
        await self.record_action(
            action_type=action_type,
            element_context=element_context,
            parameters=parameters,
            reasoning=reasoning,
            screenshot=screenshot,
        )

    def _create_action(
        self,
        action_type: ActionType,
        element_context: Optional[ElementContext],
        params: Dict[str, Any],
        reasoning: Optional[str],
    ) -> Action:
        """
        Create action object based on type.
        
        Follows Open/Closed Principle: add new action types here.
        """

        if action_type == ActionType.NAVIGATION:
            return NavigationAction(  # type: ignore[call-arg]
                url=params.get("url", ""),
                description=reasoning,
            )

        elif action_type == ActionType.CLICK:
            if not element_context:
                raise ValueError("Element context required for click action")
            return ClickAction(  # type: ignore[call-arg]
                element=element_context,
                description=reasoning,
            )

        elif action_type == ActionType.INPUT:
            if not element_context:
                raise ValueError("Element context required for input action")
            return InputAction(  # type: ignore[call-arg]
                element=element_context,
                value=params.get("text", ""),
                clear_before=params.get("clear_before_typing", True),
                press_enter=params.get("press_enter", False),
                description=reasoning,
            )

        elif action_type == ActionType.SELECT_CHANGE:
            if not element_context:
                raise ValueError("Element context required for select action")
            return SelectChangeAction(  # type: ignore[call-arg]
                element=element_context,
                selected_text=params.get("selected_text", ""),
                description=reasoning,
            )

        elif action_type == ActionType.KEY_PRESS:
            return KeyPressAction(  # type: ignore[call-arg]
                element=element_context,
                key=params.get("key", params.get("keys", "")),
                description=reasoning,
            )

        elif action_type == ActionType.SCROLL:
            return ScrollAction(  # type: ignore[call-arg]
                scroll_x=params.get("scroll_x", 0),
                scroll_y=params.get("scroll_y", 0),
                description=reasoning,
            )

        elif action_type == ActionType.GO_BACK:
            return GoBackAction(description=reasoning)  # type: ignore[call-arg]

        elif action_type == ActionType.GO_FORWARD:
            return GoForwardAction(description=reasoning)  # type: ignore[call-arg]

        elif action_type == ActionType.EXTRACT:
            return ExtractAction(  # type: ignore[call-arg]
                extraction_goal=params.get("goal", ""),
                description=reasoning,
            )

        elif action_type == ActionType.WAIT:
            return WaitAction(  # type: ignore[call-arg]
                duration=params.get("duration", 5.0),
                description=reasoning,
            )

        else:
            raise ValueError(f"Unsupported action type: {action_type}")

    def finalize(self) -> WorkflowDefinition:
        """
        Finalize and return the workflow definition.

        Returns:
            Complete workflow definition
        """
        workflow = WorkflowDefinition(
            name=self.workflow_name,
            description=self.description,
            version="1.0",
            steps=self.steps,
            workflow_analysis="\n".join(self.reasoning_log) if self.reasoning_log else None,
        )

        return workflow

    def get_step_count(self) -> int:
        """Get the number of recorded steps."""
        return len(self.steps)

    def get_duration(self) -> float:
        """Get elapsed recording time in seconds."""
        return time.time() - self.start_time

    def clear(self) -> None:
        """Clear all recorded steps."""
        self.steps.clear()
        self.step_counter = 0
        self.screenshots.clear()
        self.reasoning_log.clear()
        self.start_time = time.time()
    
    def save_screenshots(self, screenshots_dir: str) -> List[str]:
        """
        Save all recorded screenshots to a directory.
        
        Args:
            screenshots_dir: Directory path to save screenshots
            
        Returns:
            List of saved screenshot file paths
        """
        from pathlib import Path
        
        if not self.screenshots:
            return []
        
        # Create screenshots directory
        screenshots_path = Path(screenshots_dir)
        screenshots_path.mkdir(parents=True, exist_ok=True)
        
        saved_paths = []
        for i, screenshot_bytes in enumerate(self.screenshots, start=1):
            # Create filename with workflow name and step number
            filename = f"{self.workflow_name}_step_{i}.png"
            file_path = screenshots_path / filename
            
            # Save screenshot
            with open(file_path, "wb") as f:
                f.write(screenshot_bytes)
            
            saved_paths.append(str(file_path))
        
        return saved_paths
