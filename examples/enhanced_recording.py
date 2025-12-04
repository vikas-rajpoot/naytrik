"""
Example: Enhanced Recording with Multiple Selector Strategies and Coordinates

This example demonstrates the new robust recording system that captures:
1. Multiple selector strategies (ID, name, text, ARIA, etc.)
2. X,Y coordinates as fallback
3. Element metadata for debugging

The recorded workflows can then be played back deterministically without AI,
falling back to coordinates only when selectors fail.
"""

import asyncio
import os

from naytrik.automation.agent import GeminiAutomation
from naytrik.automation.playwright_browser import PlaywrightBrowser
from naytrik.recording.recorder import WorkflowRecorder


async def main():
    """Record a workflow with enhanced capture."""
    
    # Create recorder with screen dimensions
    recorder = WorkflowRecorder(
        workflow_name="enhanced_demo_workflow",
        description="Demo workflow showing enhanced recording capabilities",
        record_screenshots=True,
        screen_width=1366,  # Standard laptop screen
        screen_height=768,
    )
    
    # Create AI agent with recorder
    agent = GeminiAutomation(
        api_key=os.environ.get("GEMINI_API_KEY"),
        model_name="gemini-2.5-computer-use-preview-10-2025",
        recorder=recorder,
        verbose=True,
    )
    
    # Create browser
    browser = PlaywrightBrowser(
        headless=False,  # Show browser for demo
        width=1366,
        height=768,
    )
    
    print("=" * 70)
    print("ENHANCED RECORDING DEMO")
    print("=" * 70)
    print("\nThis demo will:")
    print("1. Navigate to a form")
    print("2. Record actions with multiple selector strategies")
    print("3. Capture x,y coordinates for each interaction")
    print("4. Generate a robust workflow file")
    print("\nThe recorded workflow can be played back without AI!")
    print("=" * 70)
    print()
    
    try:
        # Execute a task - all actions will be recorded with enhanced data
        await agent.execute_task(
            task="""
            Navigate to https://www.w3schools.com/html/html_forms.asp
            Find the form on the page.
            Fill in the First name field with 'John'.
            Fill in the Last name field with 'Doe'.
            Click the Submit button.
            """,
            browser=browser,
            max_iterations=15,
        )
        
        # Finalize and save the workflow
        workflow = recorder.finalize()
        
        print("\n" + "=" * 70)
        print("RECORDING COMPLETE")
        print("=" * 70)
        print(f"\nWorkflow: {workflow.name}")
        print(f"Steps recorded: {len(workflow.steps)}")
        print(f"Recording duration: {recorder.get_duration():.2f} seconds")
        
        # Save to file
        output_dir = "workflows/definitions"
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/enhanced_demo.yaml"
        
        workflow.save_to_file(output_path)
        print(f"\n✅ Workflow saved to: {output_path}")
        
        # Show a sample of what was recorded
        print("\n" + "=" * 70)
        print("SAMPLE RECORDED STEP")
        print("=" * 70)
        
        if workflow.steps:
            step = workflow.steps[0]
            print(f"\nStep {step.step_number}: {step.action.type}")
            
            if hasattr(step.action, 'element') and step.action.element:
                elem = step.action.element
                print(f"Target Text: {elem.target_text}")
                
                if elem.selector_strategies:
                    print(f"\nSelector Strategies ({len(elem.selector_strategies)}):")
                    for i, strategy in enumerate(elem.selector_strategies[:5], 1):
                        print(f"  {i}. [{strategy.type}] priority={strategy.priority} value='{strategy.value[:50]}'")
                    if len(elem.selector_strategies) > 5:
                        print(f"  ... and {len(elem.selector_strategies) - 5} more")
                
                if elem.coordinates:
                    print(f"\nCoordinates:")
                    print(f"  Absolute: ({elem.coordinates.x}, {elem.coordinates.y})")
                    print(f"  Normalized: ({elem.coordinates.normalized_x}, {elem.coordinates.normalized_y})")
                    print(f"  Screen: {elem.coordinates.screen_width}x{elem.coordinates.screen_height}")
        
        print("\n" + "=" * 70)
        print("KEY BENEFITS")
        print("=" * 70)
        print("""
        ✓ Multiple selector strategies ensure reliability
        ✓ Coordinates provide fallback when selectors fail
        ✓ Workflows can be played back WITHOUT AI (deterministic)
        ✓ AI only needed for dynamic decisions
        ✓ Human-readable workflow files
        ✓ Easy debugging with clear selector chains
        """)
        
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print(f"""
        1. View the recorded workflow: {output_path}
        2. Run playback with: python examples/playback_enhanced.py
        3. Modify variables in the workflow
        4. Test on different screen sizes
        """)
        
    except Exception as e:
        print(f"\n❌ Error during recording: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close browser
        try:
            await browser.close()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())
