"""
Example: Deterministic Playback with Enhanced Workflows

This example demonstrates how to play back a workflow recorded with the
enhanced recording system. The playback will:
1. Try all selector strategies first (most reliable)
2. Fall back to coordinates if selectors fail
3. Only use AI if explicitly needed (not shown here)

This is much faster and more cost-effective than AI-driven execution.
"""

import asyncio
import os
from pathlib import Path

from naytrik.playback.executor import WorkflowPlayer


async def main():
    """Play back an enhanced workflow deterministically."""
    
    print("=" * 70)
    print("ENHANCED WORKFLOW PLAYBACK DEMO")
    print("=" * 70)
    print("\nThis demo will:")
    print("1. Load a recorded workflow")
    print("2. Execute steps using selectors (no AI needed)")
    print("3. Fall back to coordinates if selectors fail")
    print("4. Show which strategy was used for each step")
    print("=" * 70)
    print()
    
    # Find the workflow file
    workflow_path = "workflows/definitions/enhanced_demo.yaml"
    
    if not Path(workflow_path).exists():
        print(f"❌ Workflow file not found: {workflow_path}")
        print("\n💡 Run the enhanced_recording.py example first to create a workflow.")
        return
    
    # Create workflow player
    player = WorkflowPlayer(
        headless=False,  # Show browser for demo
        timeout_ms=10000,  # 10 second timeout per step
        slow_mo=500,  # Slow down for visibility
    )
    
    try:
        # Execute the workflow
        print(f"▶️  Starting playback of: {workflow_path}\n")
        
        result = await player.execute_workflow(
            workflow_path=workflow_path,
            variables={
                # You can pass variables here if the workflow uses them
                # "username": "john_doe",
                # "email": "john@example.com",
            },
            start_step=1,
        )
        
        # Show results
        print("\n" + "=" * 70)
        print("PLAYBACK RESULTS")
        print("=" * 70)
        print(f"\nSuccess: {result.success}")
        print(f"Workflow: {result.workflow_name}")
        print(f"Steps completed: {result.steps_completed}/{result.total_steps}")
        print(f"Execution time: {result.execution_time:.2f} seconds")
        
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
        
        # Show what data was extracted (if any)
        if result.extracted_data:
            print("\n" + "=" * 70)
            print("EXTRACTED DATA")
            print("=" * 70)
            for key, value in result.extracted_data.items():
                print(f"{key}: {value}")
        
        print("\n" + "=" * 70)
        print("STRATEGY ANALYSIS")
        print("=" * 70)
        print("""
        The playback system automatically:
        
        1. ✓ Tries ID selector (highest priority)
        2. ✓ Tries name attribute
        3. ✓ Tries data attributes
        4. ✓ Tries text-based selectors
        5. ✓ Tries ARIA labels
        6. ✓ Tries role-based selectors
        7. ✓ Tries CSS selectors
        8. ✓ Tries XPath selectors
        9. ✓ Falls back to coordinates
        
        This cascade ensures maximum reliability!
        """)
        
    except Exception as e:
        print(f"\n❌ Error during playback: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("COMPARISON: AI vs Deterministic Playback")
    print("=" * 70)
    print("""
    AI-Driven Playback:
      • Requires API calls for each step
      • Costs money per execution
      • Slower (network latency)
      • Non-deterministic results
      • Flexible for dynamic content
    
    Deterministic Playback (This Demo):
      • No API calls needed
      • Free to execute
      • Very fast (local only)
      • Deterministic results
      • Reliable for stable workflows
    
    Best Practice:
      • Use deterministic playback for stable workflows
      • Use AI only for dynamic decisions
      • Mix both for optimal results
    """)


if __name__ == "__main__":
    asyncio.run(main())
