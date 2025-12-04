#!/usr/bin/env python3
"""
Simple Workflow Playback

A minimal script to play back recorded workflows deterministically (without AI).
"""

import asyncio
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from naytrik.playback.executor import WorkflowPlayer


def playback(
    workflow_path: str,
    headless: bool = False,
    slow_mo: int = 0,
    timeout_ms: int = 30000,
    variables: Optional[dict] = None,
    start_step: int = 1,
):
    """
    Play back a recorded workflow.
    
    Args:
        workflow_path: Path to the workflow file (.json or .yaml)
        headless: Run browser in headless mode
        slow_mo: Slow down operations by N milliseconds (useful for debugging)
        timeout_ms: Timeout for each operation in milliseconds
        variables: Variables to substitute in the workflow (e.g., {"username": "john"})
        start_step: Step number to start from (useful for debugging)
    """
    
    print(f"▶️  Playing back workflow: {workflow_path}")
    if variables:
        print(f"📝 Variables: {variables}")
    print(f"⚙️  Settings: headless={headless}, timeout={timeout_ms}ms")
    print()
    
    async def run_playback():
        # Create player with optimization settings
        player = WorkflowPlayer(
            headless=headless, 
            timeout_ms=timeout_ms, 
            slow_mo=0,  # Removed slow_mo delay for faster execution
            save_screenshots=True  # Enable screenshot saving during playback
        )
        
        try:
            # Execute workflow
            result = await player.execute_workflow(
                workflow_path=workflow_path,
                variables=variables or {},
                start_step=start_step,
            )
            
            # Show results
            print()
            print("=" * 70)
            print("PLAYBACK RESULTS")
            print("=" * 70)
            print(f"✅ Success: {result.success}")
            print(f"📊 Steps completed: {result.steps_completed}/{result.total_steps}")
            print(f"⏱️  Execution time: {result.execution_time:.2f}s")
            
            if result.error_message:
                print(f"\n❌ Error: {result.error_message}")
            
            # Show step details
            if result.step_results:
                print("\n" + "=" * 70)
                print("STEP DETAILS")
                print("=" * 70)
                
                for step_result in result.step_results:
                    status = "✅" if step_result["success"] else "❌"
                    print(f"\n{status} Step {step_result['step_number']}: {step_result['action_type']}")
                    
                    if step_result["success"]:
                        result_msg = step_result.get("result", "")
                        if result_msg:
                            print(f"   {result_msg}")
                    else:
                        error = step_result.get("error", "Unknown error")
                        print(f"   Error: {error}")
            
            # Show extracted data if any
            if result.extracted_data:
                print("\n" + "=" * 70)
                print("EXTRACTED DATA")
                print("=" * 70)
                for key, value in result.extracted_data.items():
                    print(f"{key}: {value}")
            
            return result
            
        except Exception as e:
            print(f"\n❌ Error during playback: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    result = asyncio.run(run_playback())
    return result


# Example usage
if __name__ == "__main__":
    # Specify the workflow file to play back
    # workflow_path = "workflows/definitions/tax_workflow_1.json"
    # workflow_path = "/Users/vikasrajpoot/Documents/gemini recording/gemini-workflow-automation/workflows/definitions/testing_tax_recording.json"
    
    workflow_path = "/Users/vikasrajpoot/adv_proj/gemini recording/gemini-workflow-automation/workflows/definitions/testing-1.json"
    
    # Check if file exists
    if not Path(workflow_path).exists():
        print(f"❌ Workflow file not found: {workflow_path}")
        print("\nAvailable workflows:")
        workflows_dir = Path("workflows/definitions")
        if workflows_dir.exists():
            for file in workflows_dir.glob("*.json"):
                print(f"  - {file}")
            for file in workflows_dir.glob("*.yaml"):
                print(f"  - {file}")
        exit(1)
    
    # Optional: Provide variables for parameterized workflows
    # variables = {
    #     "parcel_number": "176-34-612-004",
    #     "year": "2024",
    #     "county": "Clark",
    #     "state": "Nevada",
    # }
    variables = None
    
    # Play back the workflow
    result = playback(
        workflow_path=workflow_path,
        headless=False,           # Set to True to hide browser
        slow_mo=500,              # Slow down by 500ms per action (good for watching)
        timeout_ms=30000,         # 30 second timeout per action
        variables=variables,
        start_step=1,             # Start from step 1 (change if debugging)
    )
    
    # Exit with appropriate code
    if result and result.success:
        print("\n✅ Workflow completed successfully!")
        exit(0)
    else:
        print("\n❌ Workflow failed!")
        exit(1)
