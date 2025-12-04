#!/usr/bin/env python3
"""
Test script to verify Gemini 2.5 Computer Use model is working correctly.
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from naytrik import GeminiAutomation, WorkflowRecorder
from naytrik.automation import PlaywrightBrowser


async def test_model():
    """Test the Gemini 2.5 Computer Use model."""
    
    print("🧪 Testing Gemini 2.5 Computer Use Model")
    print("=" * 60)
    
    # Check API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ GEMINI_API_KEY not configured!")
        return
    
    # Check model
    model_name = os.environ.get("GEMINI_MODEL_NAME", "gemini-2.5-computer-use-preview-10-2025")
    print(f"🤖 Using model: {model_name}")
    
    # Create recorder
    recorder = WorkflowRecorder(
        workflow_name="model_test",
        description="Test Gemini 2.5 Computer Use model",
        record_screenshots=True,
    )
    
    # Create automation
    automation = GeminiAutomation(
        api_key=api_key,
        model_name=model_name,
        recorder=recorder,
        verbose=True,
    )
    
    print(f"✅ Model initialized: {automation.model_name}")
    print(f"🔧 Configuration:")
    print(f"   - Temperature: {automation.generate_content_config.temperature}")
    print(f"   - Max tokens: {automation.generate_content_config.max_output_tokens}")
    print(f"   - Computer Use: {bool(automation.generate_content_config.tools)}")
    
    # Create browser
    browser = PlaywrightBrowser(
        screen_size=(1366, 768),
        headless=False
    )
    
    try:
        print(f"\n🎬 Testing simple task with {model_name}...")
        print("Task: Go to example.com and click the Learn more link")
        
        result = await automation.execute_task(
            task="Go to example.com and click the Learn more link",
            browser=browser,
            initial_url="https://example.com",
        )
        
        if result["success"]:
            print(f"\n✅ Test successful!")
            print(f"   Steps completed: {result['steps']}")
            
            # Save the workflow
            workflow = recorder.finalize()
            from naytrik import WorkflowStorage
            storage = WorkflowStorage("./workflows")
            metadata = storage.save_workflow(
                workflow=workflow,
                generation_mode="ai",
                original_task="Model test with Gemini 2.5 Computer Use",
                tags=["test", "gemini-2.5", "computer-use"],
            )
            
            print(f"   Workflow saved: {metadata.file_path}")
        else:
            print(f"\n❌ Test failed")
            
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        if "UI actions are not enabled" in str(e):
            print("\n💡 Possible solutions:")
            print("1. Ensure your API key supports Computer Use")
            print("2. Try using gemini-1.5-pro model instead")
            print("3. Check if the model name is correct")
        
    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_model())