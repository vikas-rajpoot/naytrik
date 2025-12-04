"""
Basic example: Record a workflow using AI and replay it.
"""

import asyncio
import os

from naytrik import (
    GeminiAutomation,
    WorkflowPlayer,
    WorkflowRecorder,
    WorkflowStorage,
)
from naytrik.automation import PlaywrightBrowser


async def main():
    print("🎬 Example: Record and Replay Workflow\n")

    # ========== STEP 1: Record workflow with AI ==========
    print("=" * 60)
    print("STEP 1: Recording workflow with AI")
    print("=" * 60)

    # Create recorder
    recorder = WorkflowRecorder(
        workflow_name="github_search_example",
        description="Search GitHub for a repository",
        record_screenshots=False,
    )

    # Create automation
    automation = GeminiAutomation(
        api_key=os.environ.get("GEMINI_API_KEY"),
        recorder=recorder,
        verbose=True,
    )

    # Create browser
    browser = PlaywrightBrowser(
        screen_size=(1366, 768),
        headless=False,  # Set to True to run without visible browser
    )

    try:
        # Execute task with AI
        print("\n▶️  Executing task with AI...\n")
        result = await automation.execute_task(
            task="Go to GitHub homepage, search for 'playwright', and click on the first result",
            browser=browser,
            initial_url="https://github.com",
        )

        print(f"\n✅ AI automation completed!")
        print(f"   Steps taken: {result['steps']}")

        # Finalize workflow
        workflow = recorder.finalize()

        # Save workflow
        storage = WorkflowStorage("./workflows")
        metadata = storage.save_workflow(
            workflow=workflow,
            generation_mode="ai",
            original_task="GitHub search example",
            tags=["example", "github", "search"],
        )

        print(f"\n💾 Workflow saved to: {metadata.file_path}")

    finally:
        await browser.close()

    # ========== STEP 2: Replay workflow without AI ==========
    print("\n" + "=" * 60)
    print("STEP 2: Replaying workflow WITHOUT AI")
    print("=" * 60)

    # Wait a moment
    await asyncio.sleep(2)

    # Create player
    player = WorkflowPlayer(
        headless=False,
        timeout_ms=10000,
    )

    # Execute workflow
    print("\n▶️  Executing recorded workflow (no AI)...\n")
    result = await player.execute_workflow(
        workflow_path=metadata.file_path,
        variables={},  # No variables in this example
    )

    if result.success:
        print(f"\n✅ Workflow replay completed successfully!")
        print(f"   Steps: {result.steps_completed}/{result.total_steps}")
        print(f"   Time: {result.execution_time:.1f}s")
    else:
        print(f"\n❌ Workflow replay failed: {result.error_message}")

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
