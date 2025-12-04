"""
Gemini AI agent for browser automation with recording capabilities.
"""

import os
from typing import Any, Dict, List, Literal, Optional

from google import genai
from google.genai import types
from google.genai.types import (
    Candidate,
    Content,
    FinishReason,
    FunctionResponse,
    GenerateContentConfig,
    Part,
)

from naytrik.automation.browser import BrowserState, IBrowser
from naytrik.recording.recorder import WorkflowRecorder
from naytrik.schema.actions import ActionType
from naytrik.schema.selectors import ElementContext


class GeminiAutomation:
    """
    Gemini-powered browser automation with workflow recording.
    
    Follows Single Responsibility Principle: handles AI-driven automation only.
    Recording is delegated to WorkflowRecorder.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-computer-use-preview-10-2025",
        recorder: Optional[WorkflowRecorder] = None,
        verbose: bool = False,
        use_vertexai: bool = False,
        vertexai_project: Optional[str] = None,
        vertexai_location: Optional[str] = None,
    ):
        """
        Initialize Gemini automation.

        Args:
            api_key: Gemini API key (or set GEMINI_API_KEY env var)
            model_name: Model to use
            recorder: Optional workflow recorder
            verbose: Enable verbose logging
            use_vertexai: Use VertexAI instead of Gemini API
            vertexai_project: VertexAI project ID
            vertexai_location: VertexAI location
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key and not use_vertexai:
            raise ValueError("GEMINI_API_KEY must be provided or set in environment")

        self.model_name = model_name or os.environ.get("GEMINI_MODEL_NAME", "gemini-2.5-computer-use-preview-10-2025")
        self.recorder = recorder
        self.verbose = verbose

        # Initialize Gemini client
        self.client = genai.Client(
            api_key=self.api_key,
            vertexai=use_vertexai,
            project=vertexai_project,
            location=vertexai_location,
        )

        # Conversation history
        self.contents: List[Content] = []
        self.step_count = 0

        # Configuration
        self.generate_content_config = GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            tools=[
                types.Tool(
                    computer_use=types.ComputerUse(
                        environment=types.Environment.ENVIRONMENT_BROWSER,
                    ),
                ),
            ],
        )

    async def execute_task(
        self,
        task: str,
        browser: IBrowser,
        initial_url: Optional[str] = None,
        max_iterations: int = 50,
    ) -> dict:
        """
        Execute a high-level task using AI automation.

        Args:
            task: Natural language task description
            browser: Browser instance to use
            initial_url: Optional starting URL
            max_iterations: Maximum number of steps

        Returns:
            dict with execution results
        """
        if self.verbose:
            print(f"🚀 Starting task: {task}")

        # Initialize browser
        await browser.initialize()

        # Navigate to initial URL if provided
        if initial_url:
            await browser.navigate(initial_url)

        # Add task to conversation
        self.contents = [
            Content(
                role="user",
                parts=[Part(text=task)],
            )
        ]

        # Main execution loop
        status = "CONTINUE"
        while status == "CONTINUE" and self.step_count < max_iterations:
            status = await self._run_one_iteration(browser)

        if self.verbose:
            print(f"✅ Task completed in {self.step_count} steps")

        return {
            "success": status == "COMPLETE",
            "steps": self.step_count,
            "final_reasoning": getattr(self, "final_reasoning", None),
        }

    async def _run_one_iteration(self, browser: IBrowser) -> Literal["COMPLETE", "CONTINUE"]:
        """Run one iteration of the agent loop."""
        self.step_count += 1

        if self.verbose:
            print(f"\n📋 Step {self.step_count}")

        # Get response from Gemini
        response = self._get_model_response()

        if not response.candidates:
            return "COMPLETE"

        candidate = response.candidates[0]
        if candidate.content:
            self.contents.append(candidate.content)

        # Extract reasoning and function calls
        reasoning = self._get_text(candidate)
        function_calls = self._extract_function_calls(candidate)

        # Handle malformed function calls
        if (
            not function_calls
            and not reasoning
            and candidate.finish_reason == FinishReason.MALFORMED_FUNCTION_CALL
        ):
            if self.verbose:
                print("⚠️  Malformed function call, retrying...")
            return "CONTINUE"

        # Check if we're done
        if not function_calls:
            self.final_reasoning = reasoning
            if self.verbose:
                print(f"✨ Complete: {reasoning}")
            return "COMPLETE"

        # Execute function calls
        function_responses = []
        for function_call in function_calls:
            if self.verbose:
                print(f"🔧 Action: {function_call}")
                if reasoning:
                    print(f"💭 Reasoning: {reasoning}")

            # Execute action and record
            result = await self._handle_action(function_call, browser, reasoning)

            # Create function response
            function_responses.append(
                FunctionResponse(
                    name=function_call.name,
                    response={"url": result.url},
                    parts=[
                        types.FunctionResponsePart(
                            inline_data=types.FunctionResponseBlob(
                                mime_type="image/png", data=result.screenshot
                            )
                        )
                    ],
                )
            )

        # Add responses to conversation
        self.contents.append(
            Content(
                role="user",
                parts=[Part(function_response=fr) for fr in function_responses],
            )
        )

        return "CONTINUE"

    async def _handle_action(
        self, action: types.FunctionCall, browser: IBrowser, reasoning: Optional[str]
    ) -> BrowserState:
        """
        Handle a function call and record it with coordinates and element data.
        
        This method delegates to the browser for execution and to the recorder for tracking.
        Follows Single Responsibility and Open/Closed principles.
        """
        action_name = action.name
        args = dict(action.args) if action.args else {}

        # Variables to store for recording
        x_coord = None
        y_coord = None
        element_data = None
        result = None

        # Execute action based on type
        if action_name == "open_web_browser":
            result = await browser.get_current_state()
            action_type = ActionType.NAVIGATION

        elif action_name == "click_at":
            x_coord = self._denormalize_x(args["x"], browser.screen_size()[0])
            y_coord = self._denormalize_y(args["y"], browser.screen_size()[1])
            
            # Try to get element data at coordinates
            element_data = await self._get_element_at_coordinates(browser, x_coord, y_coord)
            
            result = await browser.click_at(x_coord, y_coord)
            action_type = ActionType.CLICK

        elif action_name == "hover_at":
            x_coord = self._denormalize_x(args["x"], browser.screen_size()[0])
            y_coord = self._denormalize_y(args["y"], browser.screen_size()[1])
            
            # Try to get element data at coordinates
            element_data = await self._get_element_at_coordinates(browser, x_coord, y_coord)
            
            result = await browser.hover_at(x_coord, y_coord)
            action_type = ActionType.CLICK  # Treat as click for recording

        elif action_name == "type_text_at":
            x_coord = self._denormalize_x(args["x"], browser.screen_size()[0])
            y_coord = self._denormalize_y(args["y"], browser.screen_size()[1])
            
            # Try to get element data at coordinates
            element_data = await self._get_element_at_coordinates(browser, x_coord, y_coord)
            
            result = await browser.type_text_at(
                x_coord, y_coord, args["text"], args.get("press_enter", False), args.get("clear_before_typing", True)
            )
            action_type = ActionType.INPUT
            args["text_value"] = args["text"]  # Store for recording

        elif action_name == "scroll_document":
            result = await browser.scroll_document(args["direction"])
            action_type = ActionType.SCROLL

        elif action_name == "scroll_at":
            x_coord = self._denormalize_x(args["x"], browser.screen_size()[0])
            y_coord = self._denormalize_y(args["y"], browser.screen_size()[1])
            magnitude = args.get("magnitude", 800)
            direction = args["direction"]
            if direction in ("up", "down"):
                magnitude = self._denormalize_y(magnitude, browser.screen_size()[1])
            elif direction in ("left", "right"):
                magnitude = self._denormalize_x(magnitude, browser.screen_size()[0])
            result = await browser.scroll_at(x_coord, y_coord, direction, magnitude)
            action_type = ActionType.SCROLL

        elif action_name == "wait_5_seconds":
            result = await browser.wait(5.0)
            action_type = ActionType.WAIT

        elif action_name == "go_back":
            result = await browser.go_back()
            action_type = ActionType.GO_BACK

        elif action_name == "go_forward":
            result = await browser.go_forward()
            action_type = ActionType.GO_FORWARD

        elif action_name == "navigate":
            result = await browser.navigate(args["url"])
            action_type = ActionType.NAVIGATION

        elif action_name == "key_combination":
            result = await browser.key_combination(args["keys"].split("+"))
            action_type = ActionType.KEY_PRESS

        elif action_name == "drag_and_drop":
            x_coord = self._denormalize_x(args["x"], browser.screen_size()[0])
            y_coord = self._denormalize_y(args["y"], browser.screen_size()[1])
            dest_x = self._denormalize_x(args["destination_x"], browser.screen_size()[0])
            dest_y = self._denormalize_y(args["destination_y"], browser.screen_size()[1])
            
            # Try to get element data at source coordinates
            element_data = await self._get_element_at_coordinates(browser, x_coord, y_coord)
            
            result = await browser.drag_and_drop(x_coord, y_coord, dest_x, dest_y)
            action_type = ActionType.CLICK

        else:
            raise ValueError(f"Unsupported action: {action_name}")

        # Record action if recorder is present
        if self.recorder:
            # Enhanced recording with coordinates and element data
            if hasattr(self.recorder, 'record_action_with_details'):
                await self.recorder.record_action_with_details(
                    action_type=action_type,
                    element_data=element_data,
                    x=x_coord,
                    y=y_coord,
                    parameters={**args, 'url': result.url},
                    reasoning=reasoning,
                    screenshot=result.screenshot,
                )
            else:
                # Fallback to old recording method
                element_context = ElementContext(
                    target_text=reasoning or action_name,
                    page_url=result.url,
                )
                
                await self.recorder.record_action(
                    action_type=action_type,
                    element_context=element_context if action_type in [ActionType.CLICK, ActionType.INPUT] else None,
                    parameters={**args, 'url': result.url},
                    reasoning=reasoning,
                    screenshot=result.screenshot,
                )

        return result
    
    async def _get_element_at_coordinates(
        self, browser: IBrowser, x: int, y: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get element information at given coordinates using JavaScript.
        
        Args:
            browser: Browser instance
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Dictionary with element data or None
        """
        try:
            # Get the page from browser
            page = await browser.get_page()
            
            # Execute JavaScript to get element at coordinates
            element_info = await page.evaluate("""
                (coords) => {
                    const element = document.elementFromPoint(coords.x, coords.y);
                    if (!element) return null;
                    
                    // Get element attributes
                    const attributes = {};
                    for (let attr of element.attributes) {
                        attributes[attr.name] = attr.value;
                    }
                    
                    // Get bounding box
                    const rect = element.getBoundingClientRect();
                    
                    return {
                        tag_name: element.tagName.toLowerCase(),
                        text: element.innerText || element.textContent || '',
                        attributes: attributes,
                        bounding_box: {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height
                        }
                    };
                }
            """, {"x": x, "y": y})
            
            return element_info
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Failed to get element at ({x}, {y}): {e}")
            return None

    def _get_model_response(self) -> types.GenerateContentResponse:
        """Get response from Gemini with retry logic."""
        max_retries = 2
        base_delay = 1

        for attempt in range(max_retries):
            try:
                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=self.contents,
                    config=self.generate_content_config,
                )
            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    delay = base_delay * (2**attempt)
                    if self.verbose:
                        print(f"⚠️  Retry in {delay}s: {e}")
                    time.sleep(delay)
                else:
                    raise

    def _get_text(self, candidate: Candidate) -> Optional[str]:
        """Extract text from candidate."""
        if not candidate.content or not candidate.content.parts:
            return None
        texts = [part.text for part in candidate.content.parts if part.text]
        return " ".join(texts) or None

    def _extract_function_calls(self, candidate: Candidate) -> List[types.FunctionCall]:
        """Extract function calls from candidate."""
        if not candidate.content or not candidate.content.parts:
            return []
        return [part.function_call for part in candidate.content.parts if part.function_call]

    def _denormalize_x(self, x: int, width: int) -> int:
        """Convert normalized coordinate to absolute."""
        return int(x / 1000 * width)

    def _denormalize_y(self, y: int, height: int) -> int:
        """Convert normalized coordinate to absolute."""
        return int(y / 1000 * height)



