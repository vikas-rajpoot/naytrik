#!/usr/bin/env python3
"""
Simple Workflow Recorder

A minimal script to record browser workflows using Gemini AI.
Directly uses the record function signature from the CLI.
"""

import asyncio
import os
import json
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from naytrik import GeminiAutomation, WorkflowRecorder, WorkflowStorage
from naytrik.automation.playwright_browser import PlaywrightBrowser

from task import TAX_COUNTY_PROMPT 

def record(
    task: str,
    name: str,
    description: str,
    initial_url: Optional[str],
    api_key: Optional[str],
    model: str,
    verbose: bool,
    record_screenshots: bool,
):
    """
    Record a new workflow using AI automation.
    
    Args:
        task: Natural language description of the task to perform
        name: Name for the workflow
        description: Optional description of the workflow
        initial_url: Starting URL (optional)
        api_key: Gemini API key (uses GEMINI_API_KEY env var if None)
        model: Gemini model to use
        verbose: Enable verbose output
        record_screenshots: Capture screenshots during recording
    """
    
    print(f"🎥 Recording workflow: {name}")
    print(f"📝 Task: {task}")
    print(f"🤖 Model: {model}")
    
    async def run_recording():
        # Create recorder
        recorder = WorkflowRecorder(
            workflow_name=name,
            description=description or task,
            record_screenshots=record_screenshots,
        )
        
        # Create automation
        automation = GeminiAutomation(
            api_key=api_key,
            model_name=model,
            recorder=recorder,
            verbose=verbose,
        )
        
        # Create browser
        browser = PlaywrightBrowser(
            screen_size=(1366, 768),
            headless=False,
        )
        
        try:
            # Execute task
            result = await automation.execute_task(
                task=task,
                browser=browser,
                initial_url=initial_url,
            )
            
            # Finalize and save workflow
            workflow = recorder.finalize()
            storage = WorkflowStorage()
            metadata = storage.save_workflow(
                workflow=workflow,
                generation_mode="ai",
                original_task=task,
            )
            
            # Save screenshots if recording was enabled
            if record_screenshots:
                screenshots_dir = f"workflows/screenshots/{name}"
                saved_screenshots = recorder.save_screenshots(screenshots_dir)
                if saved_screenshots:
                    print(f"📸 Saved {len(saved_screenshots)} screenshots to: {screenshots_dir}")
            
            print(f"✅ Workflow saved: {metadata.file_path}")
            print(f"📊 Steps recorded: {recorder.get_step_count()}")
            print(f"⏱️  Duration: {recorder.get_duration():.1f}s")
            
        finally:
            await browser.close()
    
    asyncio.run(run_recording())


# Example usage
if __name__ == "__main__":
    # Get API key from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Get model from environment or use default
    model = os.environ.get("GEMINI_MODEL_NAME", "gemini-2.5-computer-use-preview-10-2025")
    
    # Load config from JSON
    with open("workflow_config.json", "r") as f:
        config = json.load(f)
    
    # Get workflow config by ID
    workflow_id = "1"  # Change this to "1", "2", etc.
    workflow_config = config["workflows"].get(workflow_id)
    
    if not workflow_config:
        print(f"❌ Workflow '{workflow_id}' not found in config")
        exit(1)
    
    # # Create task from template with dynamic values
    # task = TAX_COUNTY_PROMPT.format(
    #     parcel_number=workflow_config["parcel_number"],
    #     search_year=workflow_config["year"],
    #     county=workflow_config["county"],
    #     state=workflow_config["state"]
    # )
    
    task = "go to the wikipedia and search for the modi that's it."
    
    # Record workflow with values from JSON
    record(
        task=task,
        name=workflow_config["name"],
        description=f"Tax county workflow for parcel {workflow_config['parcel_number']}",
        initial_url="",
        api_key=api_key,
        model=model,
        verbose=True,
        record_screenshots=True,
    )
