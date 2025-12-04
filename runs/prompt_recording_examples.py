#!/usr/bin/env python3
"""
Prompt-Based Workflow Recording Examples

This script demonstrates how to use natural language prompts to record workflows
using the Gemini Computer Use API.
"""

import asyncio
import os
from pathlib import Path

from naytrik import (
    GeminiAutomation,
    WorkflowPlayer,
    WorkflowRecorder,
    WorkflowStorage,
)
from naytrik.automation import PlaywrightBrowser


async def record_from_prompt(task_prompt: str, workflow_name: str, initial_url: str = None):
    """
    Record a workflow from a natural language prompt.
    
    Args:
        task_prompt: Natural language description of what to do
        workflow_name: Name for the saved workflow
        initial_url: Starting URL (optional)
    """
    print(f"\n🎬 Recording workflow: {workflow_name}")
    print(f"📝 Task: {task_prompt}")
    print("=" * 60)
    
    # Check if API key is set
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ GEMINI_API_KEY not set!")
        print("   Please get your API key from: https://makersuite.google.com/app/apikey")
        print("   Then set it in the .env file")
        return None
    
    # Create recorder
    recorder = WorkflowRecorder(
        workflow_name=workflow_name,
        description=f"Automated workflow: {task_prompt}",
        record_screenshots=True,  # Enable screenshots for better debugging
    )
    
    # Create automation with Gemini
    automation = GeminiAutomation(
        api_key=api_key,
        recorder=recorder,
        verbose=True,  # Show detailed output
    )
    
    # Create browser
    browser = PlaywrightBrowser(
        screen_size=(1366, 768),
        headless=False,  # Set to True to run without visible browser
        slow_mo=1000,    # Slow down for better visibility
    )
    
    try:
        # Execute the prompt-based task
        print(f"\n🤖 AI is executing: {task_prompt}\n")
        
        result = await automation.execute_task(
            task=task_prompt,
            browser=browser,
            initial_url=initial_url,
        )
        
        print(f"\n✅ AI automation completed!")
        print(f"   Steps taken: {result.get('steps', 'Unknown')}")
        
        # Finalize and save workflow
        workflow = recorder.finalize()
        storage = WorkflowStorage("./workflows")
        
        metadata = storage.save_workflow(
            workflow=workflow,
            generation_mode="ai",
            original_task=task_prompt,
            tags=["ai-generated", "prompt-based"],
        )
        
        print(f"\n💾 Workflow saved to: {metadata.file_path}")
        return metadata.file_path
        
    except Exception as e:
        print(f"\n❌ Error during recording: {e}")
        return None
    finally:
        await browser.close()


async def test_recorded_workflow(workflow_path: str, variables: dict = None):
    """
    Test a recorded workflow by playing it back.
    
    Args:
        workflow_path: Path to the workflow file
        variables: Optional variables for parameterized workflows
    """
    print(f"\n🎮 Testing recorded workflow: {workflow_path}")
    print("=" * 60)
    
    if not Path(workflow_path).exists():
        print(f"❌ Workflow file not found: {workflow_path}")
        return
    
    # Create player
    player = WorkflowPlayer(
        headless=False,
        timeout_ms=15000,
        slow_mo=500,
    )
    
    # Execute workflow
    result = await player.execute_workflow(
        workflow_path=workflow_path,
        variables=variables or {},
    )
    
    if result.success:
        print(f"\n✅ Workflow replay completed successfully!")
        print(f"   Steps: {result.steps_completed}/{result.total_steps}")
        print(f"   Time: {result.execution_time:.1f}s")
    else:
        print(f"\n❌ Workflow replay failed: {result.error_message}")


# Example prompts and workflows
EXAMPLE_WORKFLOWS = [
    {
        "name": "github_search",
        "prompt": "Go to GitHub, search for 'playwright', and click on the first repository result",
        "url": "https://github.com",
    },
    {
        "name": "wikipedia_search", 
        "prompt": "Search Wikipedia for 'artificial intelligence' and click on the first article",
        "url": "https://wikipedia.org",
    },
    {
        "name": "google_search",
        "prompt": "Search Google for 'python automation' and click on the first result",
        "url": "https://google.com",
    },
    {
        "name": "weather_check",
        "prompt": "Go to weather.com and search for weather in 'San Francisco'",
        "url": "https://weather.com",
    },
]


async def interactive_recording():
    """Interactive mode for custom prompt recording."""
    print("\n🎭 Interactive Prompt Recording")
    print("=" * 60)
    
    while True:
        print("\nOptions:")
        print("1. Record from custom prompt")
        print("2. Use example workflow")
        print("3. Test existing workflow")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            # Custom prompt
            task_prompt = input("\n📝 Enter your task prompt: ").strip()
            if not task_prompt:
                print("❌ Empty prompt, skipping...")
                continue
                
            workflow_name = input("📁 Enter workflow name: ").strip()
            if not workflow_name:
                workflow_name = "custom_workflow"
                
            initial_url = input("🌐 Enter starting URL (optional): ").strip()
            if not initial_url:
                initial_url = None
                
            workflow_path = await record_from_prompt(task_prompt, workflow_name, initial_url)
            
            if workflow_path:
                test_choice = input("\n🎮 Test the recorded workflow? (y/N): ").strip().lower()
                if test_choice in ['y', 'yes']:
                    await test_recorded_workflow(workflow_path)
        
        elif choice == "2":
            # Example workflows
            print("\n📚 Example Workflows:")
            for i, example in enumerate(EXAMPLE_WORKFLOWS, 1):
                print(f"  {i}. {example['name']}: {example['prompt']}")
            
            try:
                example_choice = int(input("\nSelect example (1-4): ")) - 1
                if 0 <= example_choice < len(EXAMPLE_WORKFLOWS):
                    example = EXAMPLE_WORKFLOWS[example_choice]
                    workflow_path = await record_from_prompt(
                        example["prompt"], 
                        example["name"], 
                        example["url"]
                    )
                    
                    if workflow_path:
                        test_choice = input("\n🎮 Test the recorded workflow? (y/N): ").strip().lower()
                        if test_choice in ['y', 'yes']:
                            await test_recorded_workflow(workflow_path)
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == "3":
            # Test existing workflow
            print("\n📋 Available workflows:")
            storage = WorkflowStorage("./workflows")
            workflows = storage.list_workflows()
            
            if not workflows:
                print("❌ No workflows found")
                continue
                
            for i, wf in enumerate(workflows, 1):
                print(f"  {i}. {wf.name}: {wf.description}")
            
            try:
                wf_choice = int(input("\nSelect workflow to test: ")) - 1
                if 0 <= wf_choice < len(workflows):
                    await test_recorded_workflow(workflows[wf_choice].file_path)
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")


async def main():
    """Main function with examples and interactive mode."""
    print("🤖 Gemini Workflow Automation - Prompt-Based Recording")
    print("=" * 80)
    
    # Check API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("⚠️  GEMINI_API_KEY not configured!")
        print("\n📋 Setup Instructions:")
        print("1. Get API key: https://makersuite.google.com/app/apikey")
        print("2. Edit .env file and set: GEMINI_API_KEY=your_actual_key")
        print("3. Re-run this script")
        print("\n🎮 For now, you can test existing workflows or run in demo mode.")
    else:
        print("✅ API key configured - ready for AI recording!")
    
    # Show usage examples
    print("\n📚 How Prompt-Based Recording Works:")
    print("=" * 50)
    print("1. 🤖 AI interprets your natural language prompt")
    print("2. 🌐 AI controls the browser to complete the task")
    print("3. 📹 Every action is automatically recorded")
    print("4. 💾 Workflow is saved for future replay")
    print("5. 🎮 You can replay without AI (instant + free)")
    
    print("\n🎯 Example Prompts:")
    for example in EXAMPLE_WORKFLOWS:
        print(f"  • {example['prompt']}")
    
    # Run interactive mode
    await interactive_recording()


if __name__ == "__main__":
    asyncio.run(main())