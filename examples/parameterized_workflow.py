"""
Advanced example: Parameterized workflow with variables.
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


async def record_login_workflow():
    """Record a login workflow with variables."""
    print("🎥 Recording login workflow...\n")

    recorder = WorkflowRecorder(
        workflow_name="login_parameterized",
        description="Login to a website with username and password variables",
    )

    automation = GeminiAutomation(
        api_key=os.environ.get("GEMINI_API_KEY"),
        recorder=recorder,
        verbose=True,
    )

    browser = PlaywrightBrowser(headless=False)

    try:
        # Record the workflow
        # Note: In real usage, you'd use actual credentials for recording
        # Then replace them with variables in the saved workflow
        await automation.execute_task(
            task="Go to the login page, enter test@example.com in email field, enter password123 in password field, and click login button",
            browser=browser,
            initial_url="https://example.com/login",
        )

        workflow = recorder.finalize()

        # Manually add input schema for variables
        # In a real system, this could be auto-detected
        from naytrik.schema.workflow import WorkflowInputSchema

        workflow.input_schema = [
            WorkflowInputSchema(
                name="email",
                type="string",
                required=True,
                description="User email address",
            ),
            WorkflowInputSchema(
                name="password",
                type="string",
                required=True,
                description="User password",
            ),
        ]

        # Save workflow
        storage = WorkflowStorage()
        metadata = storage.save_workflow(
            workflow=workflow,
            generation_mode="ai",
            tags=["login", "parameterized"],
        )

        print(f"\n✅ Workflow saved: {metadata.file_path}")
        return metadata.file_path

    finally:
        await browser.close()


async def replay_with_different_credentials(workflow_path: str):
    """Replay the workflow with different credentials."""
    print("\n🔄 Replaying with different credentials...\n")

    player = WorkflowPlayer(headless=False)

    # Test with different credentials
    test_credentials = [
        {"email": "user1@example.com", "password": "password1"},
        {"email": "user2@example.com", "password": "password2"},
    ]

    for i, creds in enumerate(test_credentials, 1):
        print(f"\nTest {i}: {creds['email']}")

        result = await player.execute_workflow(
            workflow_path=workflow_path,
            variables=creds,
        )

        if result.success:
            print(f"✅ Test {i} passed")
        else:
            print(f"❌ Test {i} failed: {result.error_message}")

        await asyncio.sleep(2)


async def main():
    # Record workflow
    workflow_path = await record_login_workflow()

    # Wait a moment
    await asyncio.sleep(3)

    # Replay with different parameters
    await replay_with_different_credentials(workflow_path)

    print("\n✨ Example completed!")


if __name__ == "__main__":
    asyncio.run(main())
