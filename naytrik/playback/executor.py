"""
Workflow executor for deterministic playback without AI.
"""

import asyncio
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union

from playwright.async_api import Page, async_playwright

from naytrik.playback.element_finder import ElementFinder
from naytrik.schema.actions import (
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
from naytrik.schema.workflow import (
    WorkflowDefinition,
    WorkflowExecutionResult,
)


class WorkflowPlayer:
    """
    Executes workflows deterministically without AI.
    
    Follows Single Responsibility Principle: only handles workflow execution.
    Follows Open/Closed Principle: extensible for new action types.
    """

    def __init__(
        self,
        headless: bool = False,
        timeout_ms: int = 30000,
        slow_mo: int = 0,
        save_screenshots: bool = False,
        screenshots_dir: str = "workflows/playback_screenshots",
    ):
        """
        Initialize workflow player.

        Args:
            headless: Run browser in headless mode
            timeout_ms: Default timeout for operations
            slow_mo: Slow down operations by N milliseconds
            save_screenshots: Save screenshots after each step
            screenshots_dir: Directory to save screenshots
        """
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.slow_mo = slow_mo
        self.save_screenshots = save_screenshots
        self.screenshots_dir = Path(screenshots_dir)

        self.page: Optional[Page] = None
        self.element_finder: Optional[ElementFinder] = None
        self.context_data: Dict[str, Any] = {}

    async def execute_workflow(
        self,
        workflow_path: Union[str, Path],
        variables: Optional[Dict[str, Any]] = None,
        start_step: int = 1,
    ) -> WorkflowExecutionResult:
        """
        Execute a workflow from file.

        Args:
            workflow_path: Path to workflow YAML/JSON file
            variables: Variable values for parameterized workflows
            start_step: Step number to start from (for debugging)

        Returns:
            WorkflowExecutionResult with execution details
        """
        # Load workflow
        workflow = WorkflowDefinition.load_from_file(workflow_path)

        # Merge variables into context
        if variables:
            self.context_data.update(variables)

        # Execute
        return await self.execute_workflow_definition(workflow, start_step)

    async def execute_workflow_definition(
        self,
        workflow: WorkflowDefinition,
        start_step: int = 1,
    ) -> WorkflowExecutionResult:
        """
        Execute a workflow definition.

        Args:
            workflow: Workflow definition to execute
            start_step: Step number to start from

        Returns:
            WorkflowExecutionResult with execution details
        """
        start_time = time.time()
        steps_completed = 0
        step_results = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
            )

            context = await browser.new_context(
                viewport={"width": 1366, "height": 768},
            )

            self.page = await context.new_page()
            self.element_finder = ElementFinder(self.page, self.timeout_ms)

            try:
                # Execute steps
                for step in workflow.steps:
                    if step.step_number < start_step:
                        continue

                    step_start_time = time.time()
                    
                    try:
                        print(f"⚙️  Step {step.step_number}: {step.action.type}")

                        # Execute action
                        result = await self._execute_action(step.action)
                        
                        step_duration = time.time() - step_start_time
                        print(f"   ✓ Completed in {step_duration:.2f}s")

                        # Save screenshot if enabled
                        if self.save_screenshots:
                            await self._save_step_screenshot(workflow.name, step.step_number)

                        step_results.append({
                            "step_number": step.step_number,
                            "action_type": step.action.type,
                            "success": True,
                            "result": result,
                            "duration": step_duration,
                        })

                        steps_completed += 1

                        # Minimal wait between steps (removed default wait_time)
                        # Only wait if explicitly specified in action
                        wait_time = step.action.wait_time if hasattr(step.action, 'wait_time') and step.action.wait_time else 0
                        if wait_time > 0:
                            await asyncio.sleep(wait_time)

                    except Exception as e:
                        step_duration = time.time() - step_start_time
                        error_msg = f"Step {step.step_number} failed: {str(e)}"
                        print(f"❌ {error_msg}")
                        print(f"   Action: {step.action.type}")
                        print(f"   Duration: {step_duration:.2f}s")
                        
                        # Save error screenshot
                        if self.save_screenshots:
                            await self._save_step_screenshot(workflow.name, step.step_number, error=True)

                        step_results.append({
                            "step_number": step.step_number,
                            "action_type": step.action.type,
                            "success": False,
                            "error": str(e),
                            "duration": step_duration,
                        })

                        # Return failure result
                        execution_time = time.time() - start_time
                        return WorkflowExecutionResult(
                            success=False,
                            workflow_name=workflow.name,
                            steps_completed=steps_completed,
                            total_steps=len(workflow.steps),
                            error_message=error_msg,
                            extracted_data=self.context_data,
                            execution_time=execution_time,
                            step_results=step_results,
                        )

                # Success
                execution_time = time.time() - start_time
                return WorkflowExecutionResult(
                    success=True,
                    workflow_name=workflow.name,
                    steps_completed=steps_completed,
                    total_steps=len(workflow.steps),
                    error_message=None,
                    extracted_data=self.context_data,
                    execution_time=execution_time,
                    step_results=step_results,
                )

            finally:
                await browser.close()

    async def _save_step_screenshot(self, workflow_name: str, step_number: int, error: bool = False) -> None:
        """Save screenshot for a step."""
        assert self.page is not None, "Page not initialized"
        try:
            # Create screenshots directory
            workflow_dir = self.screenshots_dir / workflow_name.replace(" ", "_")
            workflow_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            prefix = "error" if error else "step"
            filename = f"{prefix}_{step_number}.png"
            filepath = workflow_dir / filename
            
            # Save screenshot
            await self.page.screenshot(path=str(filepath))
            
            if error:
                print(f"   📸 Error screenshot saved: {filepath}")
            
        except Exception as e:
            print(f"   ⚠️  Failed to save screenshot: {e}")

    async def _execute_action(self, action) -> Optional[str]:
        """
        Execute a single action.
        
        Follows Open/Closed Principle: add new action handlers here.
        """
        action_type = action.type

        if action_type == "navigation":
            return await self._execute_navigation(action)

        elif action_type == "click":
            return await self._execute_click(action)

        elif action_type == "input":
            return await self._execute_input(action)

        elif action_type == "select_change":
            return await self._execute_select_change(action)

        elif action_type == "key_press":
            return await self._execute_key_press(action)

        elif action_type == "scroll":
            return await self._execute_scroll(action)

        elif action_type == "go_back":
            return await self._execute_go_back(action)

        elif action_type == "go_forward":
            return await self._execute_go_forward(action)

        elif action_type == "extract":
            return await self._execute_extract(action)

        elif action_type == "wait":
            return await self._execute_wait(action)

        else:
            raise ValueError(f"Unsupported action type: {action_type}")

    async def _execute_navigation(self, action: NavigationAction) -> str:
        """Navigate to URL."""
        assert self.page is not None, "Page not initialized"
        url = self._interpolate_variables(action.url)
        await self.page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
        await self.page.wait_for_load_state()
        return f"Navigated to {url}"

    async def _execute_click(self, action: ClickAction) -> str:
        """Click element using selectors or coordinates."""
        assert self.page is not None, "Page not initialized"
        assert self.element_finder is not None, "Element finder not initialized"
        result = await self.element_finder.find_element(action.element)
        
        # Check if we got coordinates or a locator
        if isinstance(result[0], tuple):
            # Coordinate-based click
            x, y = result[0]
            await self.page.mouse.click(x, y)
            return f"Clicked at coordinates ({x}, {y})"
        else:
            # Locator-based click
            locator, strategy = result
            await locator.click()  # type: ignore[union-attr]
            return f"Clicked element using {strategy}"

    async def _execute_input(self, action: InputAction) -> str:
        """Input text using selectors or coordinates."""
        assert self.page is not None, "Page not initialized"
        assert self.element_finder is not None, "Element finder not initialized"
        result = await self.element_finder.find_element(action.element)

        value = self._interpolate_variables(action.value)
        if not value and action.default_value:
            value = action.default_value

        # Check if we got coordinates or a locator
        if isinstance(result[0], tuple):
            # Coordinate-based input
            x, y = result[0]
            await self.page.mouse.click(x, y)  # Click to focus
            
            if action.clear_before:
                # Select all and delete
                await self.page.keyboard.press("Control+A")
                await self.page.keyboard.press("Backspace")
            
            await self.page.keyboard.type(value)
            
            if action.press_enter:
                await self.page.keyboard.press("Enter")
            
            return f"Input text at coordinates ({x}, {y})"
        else:
            # Locator-based input
            locator, strategy = result
            
            if action.clear_before:
                await locator.clear()  # type: ignore[union-attr]

            await locator.fill(value)  # type: ignore[union-attr]

            if action.press_enter:
                await locator.press("Enter")  # type: ignore[union-attr]

            return f"Input text using {strategy}"

    async def _execute_select_change(self, action: SelectChangeAction) -> str:
        """Select dropdown option."""
        assert self.element_finder is not None, "Element finder not initialized"
        locator, strategy = await self.element_finder.find_element(action.element)

        selected_text = self._interpolate_variables(action.selected_text)
        await locator.select_option(label=selected_text)  # type: ignore[union-attr]

        return f"Selected '{selected_text}' using {strategy}"

    async def _execute_key_press(self, action: KeyPressAction) -> str:
        """Press key."""
        assert self.page is not None, "Page not initialized"
        assert self.element_finder is not None, "Element finder not initialized"
        if action.element:
            locator, _ = await self.element_finder.find_element(action.element)
            await locator.press(action.key)  # type: ignore[union-attr]
        else:
            await self.page.keyboard.press(action.key)

        return f"Pressed key: {action.key}"

    async def _execute_scroll(self, action: ScrollAction) -> str:
        """Scroll page."""
        assert self.page is not None, "Page not initialized"
        await self.page.evaluate(
            f"window.scrollBy({action.scroll_x}, {action.scroll_y})"
        )
        return f"Scrolled by ({action.scroll_x}, {action.scroll_y})"

    async def _execute_go_back(self, action: GoBackAction) -> str:
        """Go back in history."""
        assert self.page is not None, "Page not initialized"
        await self.page.go_back(wait_until="domcontentloaded")
        await self.page.wait_for_load_state()
        return "Navigated back"

    async def _execute_go_forward(self, action: GoForwardAction) -> str:
        """Go forward in history."""
        assert self.page is not None, "Page not initialized"
        await self.page.go_forward(wait_until="domcontentloaded")
        await self.page.wait_for_load_state()
        return "Navigated forward"

    async def _execute_extract(self, action: ExtractAction) -> str:
        """Extract content from page."""
        assert self.page is not None, "Page not initialized"
        # Simple extraction - get page text
        content = await self.page.inner_text("body")

        # Store in context
        if action.output:
            self.context_data[action.output] = content

        return f"Extracted content (length: {len(content)})"

    async def _execute_wait(self, action: WaitAction) -> str:
        """Wait for duration."""
        await asyncio.sleep(action.duration)
        return f"Waited {action.duration} seconds"

    def _interpolate_variables(self, value: str) -> str:
        """
        Interpolate variables in string.
        
        Replaces {variable_name} with values from context_data.
        """
        if not value or "{" not in value:
            return value

        result = value
        for key, val in self.context_data.items():
            result = result.replace(f"{{{key}}}", str(val))

        return result
