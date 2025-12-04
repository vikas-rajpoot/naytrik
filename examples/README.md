# Examples

This directory contains example scripts demonstrating the Gemini Workflow Automation framework.

## Prerequisites

1. Install the package:
```bash
pip install -e .
```

2. Set your Gemini API key:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Examples

### 1. Basic Recording (`basic_recording.py`)

Records a simple workflow using AI and replays it without AI.

```bash
python examples/basic_recording.py
```

**What it does:**
- Uses AI to navigate GitHub and search for a repository
- Records all actions automatically
- Saves the workflow to a file
- Replays the exact same actions without AI

**Key concepts:**
- AI-driven automation
- Automatic action recording
- Deterministic playback

### 2. Parameterized Workflow (`parameterized_workflow.py`)

Creates a reusable workflow with variables.

```bash
python examples/parameterized_workflow.py
```

**What it does:**
- Records a login workflow
- Adds variables for email and password
- Replays the workflow multiple times with different credentials

**Key concepts:**
- Variable interpolation
- Reusable workflows
- Multiple test scenarios

### 3. Advanced Automation (`advanced_automation.py`)

Demonstrates complex automation scenarios.

```bash
python examples/advanced_automation.py
```

**What it does:**
- Multi-step form filling
- Data extraction
- Error handling
- Custom verification

**Key concepts:**
- Complex workflows
- Data extraction
- Error recovery

## Creating Your Own Examples

### Basic Template

```python
import asyncio
from naytrik import (
    GeminiAutomation,
    WorkflowRecorder,
    WorkflowPlayer,
)
from naytrik.automation import PlaywrightBrowser

async def main():
    # 1. Record workflow
    recorder = WorkflowRecorder(
        workflow_name="my_workflow",
        description="What my workflow does",
    )
    
    automation = GeminiAutomation(recorder=recorder)
    browser = PlaywrightBrowser()
    
    await automation.execute_task(
        task="Your natural language task",
        browser=browser,
        initial_url="https://example.com"
    )
    
    workflow = recorder.finalize()
    
    # 2. Save workflow
    from naytrik import WorkflowStorage
    storage = WorkflowStorage()
    storage.save_workflow(workflow)
    
    # 3. Replay workflow
    player = WorkflowPlayer()
    await player.execute_workflow("workflows/my_workflow.json")

asyncio.run(main())
```

## Tips

1. **Start Simple**: Begin with simple navigation and click actions
2. **Use Descriptive Names**: Clear workflow names help organization
3. **Test Incrementally**: Test each step during recording
4. **Handle Errors**: Add verification checks for critical steps
5. **Use Variables**: Make workflows reusable with parameters

## Troubleshooting

### Element Not Found
- Ensure selectors are robust
- Add wait times for dynamic content
- Use semantic selectors (text, ARIA) over CSS

### Timeout Errors
- Increase timeout in WorkflowPlayer
- Check network speed
- Verify page loads completely

### AI Not Understanding Task
- Be specific in task descriptions
- Break complex tasks into smaller steps
- Provide context (URLs, element descriptions)

## Next Steps

- Review the [main README](../README.md) for architecture details
- Check the [CLI documentation](../README.md#cli-usage)
- Explore the source code in `src/`
