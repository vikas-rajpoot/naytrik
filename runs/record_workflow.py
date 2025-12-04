#!/usr/bin/env python3
"""
Standalone Gemini Workflow Recorder

This script provides a simple interface to record browser workflows using Gemini AI.
No CLI dependencies - just run this file directly.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the workflow automation components
from naytrik import GeminiAutomation, WorkflowRecorder, WorkflowStorage
from naytrik.automation.playwright_browser import PlaywrightBrowser


class WorkflowRecordingSession:
    """A simple class to handle workflow recording sessions."""
    
    def __init__(
        self,
        api_key: str = None,
        model_name: str = "gemini-2.5-computer-use-preview-10-2025",
        verbose: bool = True,
        record_screenshots: bool = True,
        headless: bool = False,
        screen_size: tuple = (1366, 768),
    ):
        """
        Initialize recording session.
        
        Args:
            api_key: Gemini API key (or set GEMINI_API_KEY env var)
            model_name: Model to use for automation
            verbose: Enable detailed output
            record_screenshots: Capture screenshots during recording
            headless: Run browser in headless mode
            screen_size: Browser window size (width, height)
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = model_name or os.environ.get("GEMINI_MODEL_NAME", "gemini-2.5-computer-use-preview-10-2025")
        self.verbose = verbose
        self.record_screenshots = record_screenshots
        self.headless = headless
        self.screen_size = screen_size
        
        # Validate API key
        if not self.api_key or self.api_key == "your_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY not found! Please:\n"
                "1. Get API key from: https://makersuite.google.com/app/apikey\n"
                "2. Set GEMINI_API_KEY environment variable\n"
                "3. Or pass api_key parameter to this class"
            )
    
    async def record_workflow(
        self,
        task: str,
        workflow_name: str,
        description: str = "",
        initial_url: str = None,
        max_iterations: int = 50,
        tags: list = None,
    ) -> str:
        """
        Record a workflow from a natural language task.
        
        Args:
            task: Natural language description of what to do
            workflow_name: Name for the saved workflow
            description: Optional description
            initial_url: Starting URL (optional)
            max_iterations: Maximum number of steps
            tags: Tags for categorization
            
        Returns:
            Path to the saved workflow file
        """
        print(f"🎥 Recording Workflow: {workflow_name}")
        print(f"📝 Task: {task}")
        print(f"🤖 Model: {self.model_name}")
        print(f"🌐 Initial URL: {initial_url or 'None'}")
        print("=" * 80)
        
        # Create recorder
        recorder = WorkflowRecorder(
            workflow_name=workflow_name,
            description=description or task,
            record_screenshots=self.record_screenshots,
        )
        
        # Create automation
        automation = GeminiAutomation(
            api_key=self.api_key,
            model_name=self.model_name,
            recorder=recorder,
            verbose=self.verbose,
        )
        
        # Create browser
        browser = PlaywrightBrowser(
            screen_size=self.screen_size,
            headless=self.headless,
        )
        
        try:
            print(f"\n🚀 Starting AI automation...")
            
            # Execute the task
            result = await automation.execute_task(
                task=task,
                browser=browser,
                initial_url=initial_url,
                max_iterations=max_iterations,
            )
            
            if result["success"]:
                print(f"\n✅ AI automation completed!")
                print(f"   Steps taken: {result['steps']}")
                
                # Finalize and save workflow
                workflow = recorder.finalize()
                storage = WorkflowStorage("./workflows")
                
                metadata = storage.save_workflow(
                    workflow=workflow,
                    generation_mode="ai",
                    original_task=task,
                    tags=tags or ["ai-generated"],
                )
                
                print(f"\n💾 Workflow saved!")
                print(f"   File: {metadata.file_path}")
                print(f"   ID: {metadata.id}")
                print(f"   Steps recorded: {len(workflow.steps)}")
                
                return metadata.file_path
            else:
                print(f"\n❌ AI automation failed")
                return None
                
        except Exception as e:
            print(f"\n❌ Error during recording: {e}")
            
            # Provide helpful error messages
            if "UI actions are not enabled" in str(e):
                print("\n💡 This error means your API key doesn't support Computer Use.")
                print("   Solutions:")
                print("   1. Get a Computer Use enabled API key")
                print("   2. Visit: https://ai.google.dev/gemini-api/docs/computer-use")
            elif "INVALID_ARGUMENT" in str(e):
                print("\n💡 Invalid model or API configuration.")
                print("   Try using: gemini-1.5-pro")
            
            return None
            
        finally:
            await browser.close()


# Predefined workflow examples
EXAMPLE_WORKFLOWS = [
    {
        "name": "github_search",
        "task": "Go to GitHub, search for 'browser automation', and click on the first repository",
        "url": "https://github.com",
        "tags": ["github", "search"],
    },
    {
        "name": "wikipedia_search",
        "task": "Search Wikipedia for 'artificial intelligence' and read the first paragraph",
        "url": "https://wikipedia.org",
        "tags": ["wikipedia", "research"],
    },
    {
        "name": "google_search",
        "task": "Search Google for 'python automation tutorials' and click the first result",
        "url": "https://google.com",
        "tags": ["google", "search", "tutorials"],
    },
    {
        "name": "example_demo",
        "task": "Go to example.com and click the 'Learn more' link",
        "url": "https://example.com",
        "tags": ["demo", "simple"],
    },
    {
        "name": "news_reading",
        "task": "Go to a news website and find the latest headline",
        "url": "https://news.ycombinator.com",
        "tags": ["news", "reading"],
    },
]


async def interactive_recorder():
    """Interactive mode for recording workflows."""
    print("🤖 Gemini Workflow Recorder - Interactive Mode")
    print("=" * 80)
    
    # Initialize session
    try:
        session = WorkflowRecordingSession(verbose=True)
        print(f"✅ Session initialized with model: {session.model_name}")
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    while True:
        print("\n📋 Options:")
        print("1. Record custom workflow")
        print("2. Use example workflow")
        print("3. List saved workflows")
        print("4. Exit")
        
        choice = input("\n👉 Select option (1-4): ").strip()
        
        if choice == "1":
            # Custom workflow
            print("\n📝 Custom Workflow Recording")
            print("-" * 40)
            
            task = input("Task description: ").strip()
            if not task:
                print("❌ Empty task, skipping...")
                continue
            
            name = input("Workflow name: ").strip()
            if not name:
                name = "custom_workflow"
            
            description = input("Description (optional): ").strip()
            initial_url = input("Starting URL (optional): ").strip() or None
            
            # Tags
            tags_input = input("Tags (comma-separated, optional): ").strip()
            tags = [t.strip() for t in tags_input.split(",")] if tags_input else ["custom"]
            
            # Record the workflow
            result = await session.record_workflow(
                task=task,
                workflow_name=name,
                description=description,
                initial_url=initial_url,
                tags=tags,
            )
            
            if result:
                test_now = input("\n🎮 Test the recorded workflow now? (y/N): ").strip().lower()
                if test_now in ['y', 'yes']:
                    await test_workflow(result)
        
        elif choice == "2":
            # Example workflows
            print("\n📚 Example Workflows:")
            print("-" * 40)
            
            for i, example in enumerate(EXAMPLE_WORKFLOWS, 1):
                print(f"{i}. {example['name']}: {example['task']}")
            
            try:
                example_choice = int(input(f"\n👉 Select example (1-{len(EXAMPLE_WORKFLOWS)}): ")) - 1
                if 0 <= example_choice < len(EXAMPLE_WORKFLOWS):
                    example = EXAMPLE_WORKFLOWS[example_choice]
                    
                    result = await session.record_workflow(
                        task=example["task"],
                        workflow_name=example["name"],
                        description=f"Example: {example['task']}",
                        initial_url=example["url"],
                        tags=example["tags"],
                    )
                    
                    if result:
                        test_now = input("\n🎮 Test the recorded workflow now? (y/N): ").strip().lower()
                        if test_now in ['y', 'yes']:
                            await test_workflow(result)
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input")
        
        elif choice == "3":
            # List workflows
            list_workflows()
        
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")


async def test_workflow(workflow_path: str):
    """Test a recorded workflow by playing it back."""
    print(f"\n🎮 Testing workflow: {workflow_path}")
    print("-" * 60)
    
    from naytrik import WorkflowPlayer
    
    player = WorkflowPlayer(headless=False)
    
    try:
        result = await player.execute_workflow(
            workflow_path=workflow_path,
            variables={},
        )
        
        if result.success:
            print(f"✅ Test successful!")
            print(f"   Steps: {result.steps_completed}/{result.total_steps}")
            print(f"   Time: {result.execution_time:.1f}s")
        else:
            print(f"❌ Test failed: {result.error_message}")
    except Exception as e:
        print(f"❌ Test error: {e}")


def list_workflows():
    """List all saved workflows."""
    print("\n📚 Saved Workflows:")
    print("-" * 40)
    
    from naytrik import WorkflowStorage
    
    storage = WorkflowStorage("./workflows")
    workflows = storage.list_workflows()
    
    if not workflows:
        print("No workflows found")
        return
    
    for wf in workflows:
        print(f"• {wf.name} ({wf.generation_mode})")
        print(f"  {wf.description}")
        print(f"  File: {wf.file_path}")
        if wf.tags:
            print(f"  Tags: {', '.join(wf.tags)}")
        print()


async def quick_record(task: str, name: str, url: str = None):
    """Quick recording function for simple use cases."""
    session = WorkflowRecordingSession()
    return await session.record_workflow(
        task=task,
        workflow_name=name,
        initial_url=url,
        tags=["quick-record"],
    )


async def main():
    """Main function - choose between interactive and quick modes."""
    print("🚀 Gemini Workflow Recorder")
    print("=" * 80)
    print("Record browser workflows using natural language prompts!")
    print()
    
    # Check if running with arguments for quick mode
    import sys
    if len(sys.argv) > 1:
        # Quick mode: python record_workflow.py "task description" workflow_name [url]
        task = sys.argv[1]
        name = sys.argv[2] if len(sys.argv) > 2 else "quick_workflow"
        url = sys.argv[3] if len(sys.argv) > 3 else None
        
        print(f"🏃 Quick Record Mode")
        print(f"Task: {task}")
        print(f"Name: {name}")
        print(f"URL: {url}")
        
        result = await quick_record(task, name, url)
        if result:
            print(f"\n✅ Workflow saved to: {result}")
    else:
        # Interactive mode
        await interactive_recorder()


if __name__ == "__main__":
    asyncio.run(main())