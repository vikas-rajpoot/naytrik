#!/usr/bin/env python3
"""
Demo script to show Gemini Workflow Automation functionality.
This script demonstrates the package's capabilities without requiring API keys.
"""

import asyncio
import os
from pathlib import Path

from naytrik import (
    WorkflowPlayer,
    WorkflowRecorder,
    WorkflowStorage,
)
from naytrik.schema.workflow import (
    WorkflowDefinition,
    WorkflowStep,
    WorkflowInputSchema,
)
from naytrik.schema.actions import ClickAction, InputAction, NavigationAction
from naytrik.schema.selectors import ElementContext


async def create_demo_workflow():
    """Create a demo workflow manually for testing playback."""
    print("🏗️  Creating demo workflow...")
    
    # Create a workflow manually
    workflow = WorkflowDefinition(
        name="demo_workflow",
        description="A demo workflow for testing",
        version="1.0",
        steps=[
            WorkflowStep(
                step_number=1,
                action=NavigationAction(url="https://example.com"),
                description="Navigate to example.com"
            ),
            WorkflowStep(
                step_number=2,
                action=ClickAction(
                    element=ElementContext(target_text="More information...")
                ),
                description="Click on More information link"
            ),
        ],
        input_schema=[],
        metadata={
            "created_by": "demo",
            "tags": ["demo", "example"],
        }
    )
    
    # Save the workflow
    storage = WorkflowStorage("./workflows")
    metadata = storage.save_workflow(
        workflow=workflow,
        generation_mode="manual",
        original_task="Demo workflow",
        tags=["demo", "test"],
    )
    
    print(f"✅ Demo workflow created: {metadata.file_path}")
    return metadata.file_path


async def demo_workflow_playback(workflow_path: str):
    """Demonstrate workflow playback without AI."""
    print(f"\n🎬 Playing back workflow: {workflow_path}")
    
    # Create player
    player = WorkflowPlayer(
        headless=False,  # Set to True for headless mode
        timeout_ms=10000,
    )
    
    try:
        # Execute workflow
        result = await player.execute_workflow(
            workflow_path=workflow_path,
            variables={},
        )
        
        if result.success:
            print(f"✅ Workflow completed successfully!")
            print(f"   Steps: {result.steps_completed}/{result.total_steps}")
            print(f"   Time: {result.execution_time:.1f}s")
        else:
            print(f"❌ Workflow failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Error executing workflow: {e}")


def demo_cli_commands():
    """Demonstrate CLI commands."""
    print("\n📟 CLI Commands Demo:")
    print("=" * 50)
    
    # List workflows
    print("📋 Available workflows:")
    os.system("gemini-workflow list")
    
    print("\n🔍 CLI Help:")
    os.system("gemini-workflow --help")


def demo_package_components():
    """Demonstrate package components without execution."""
    print("\n🧩 Package Components Demo:")
    print("=" * 50)
    
    # Demo recorder
    print("📹 WorkflowRecorder:")
    recorder = WorkflowRecorder(
        workflow_name="test_recorder",
        description="Test recorder instance"
    )
    print(f"   - Name: {recorder.workflow_name}")
    print(f"   - Description: {recorder.description}")
    
    # Demo storage
    print("\n💾 WorkflowStorage:")
    storage = WorkflowStorage("./workflows")
    print(f"   - Storage directory: {storage.storage_dir}")
    print(f"   - Workflows directory: {storage.workflows_dir}")
    
    # Demo player
    print("\n🎮 WorkflowPlayer:")
    player = WorkflowPlayer()
    print(f"   - Timeout: {player.timeout_ms}ms")
    print(f"   - Headless: {player.headless}")


async def main():
    """Main demo function."""
    print("🚀 Gemini Workflow Automation - Demo")
    print("=" * 60)
    print("This demo shows the package functionality without requiring API keys.")
    print("=" * 60)
    
    # Demo package components
    demo_package_components()
    
    # Create demo workflow
    workflow_path = await create_demo_workflow()
    
    # Demo CLI commands
    demo_cli_commands()
    
    # Ask user if they want to run the browser demo
    print("\n" + "=" * 60)
    response = input("🌐 Would you like to run the browser demo? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("\n🎬 Running browser demo...")
        await demo_workflow_playback(workflow_path)
    else:
        print("👍 Skipping browser demo.")
    
    print("\n" + "=" * 60)
    print("✨ Demo completed!")
    print("=" * 60)
    print("\n📚 Next steps:")
    print("1. Set up GEMINI_API_KEY in .env file")
    print("2. Run: python examples/basic_recording.py")
    print("3. Explore CLI: gemini-workflow --help")
    print("4. Check documentation in README.md")


if __name__ == "__main__":
    asyncio.run(main())