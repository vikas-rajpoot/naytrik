<div align="center">

# 🚀 Naytrik

### AI-Powered Browser Automation with Record & Playback

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Playwright](https://img.shields.io/badge/Playwright-enabled-brightgreen.svg)](https://playwright.dev/)

**Record once with AI. Replay infinitely without it.**

[Quick Start](#-quick-start) • [Features](#-features) • [Documentation](#-documentation) • [Examples](#-examples)

</div>

---

## 🎯 What is Naytrik?

Naytrik is a **next-generation browser automation framework** that combines the intelligence of Google's Gemini AI with the speed and reliability of deterministic playback. 

**The Problem:** Traditional browser automation is fragile. AI-only automation is slow and expensive.

**The Solution:** Record workflows once using AI, then replay them instantly without any AI calls.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   🤖 Record     │ ──► │   💾 Save       │ ──► │   ⚡ Replay     │
│   with AI       │     │   Workflow      │     │   Without AI    │
│   (One-time)    │     │   (Selectors)   │     │   (Infinite)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎬 **Smart Recording** | AI understands your intent and captures robust selectors |
| ⚡ **Fast Playback** | Deterministic execution without AI API calls |
| 🔄 **Multi-Strategy Fallback** | CSS → XPath → Text → Coordinates |
| 🎛️ **Parameterized Workflows** | Use variables for dynamic data injection |
| 📸 **Screenshot Capture** | Visual debugging and documentation |
| 🖥️ **CLI & Python API** | Flexible integration options |
| 🔌 **Extensible Architecture** | SOLID principles, easy to customize |

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/naytrik.git
cd naytrik

# Run the install script
chmod +x install.sh && ./install.sh

# Activate virtual environment
source venv/bin/activate
```

### Configuration

```bash
# Copy example environment file
cp .env.example .env

# Add your Gemini API key
echo "GEMINI_API_KEY=your_api_key_here" >> .env
```

> 🔑 Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Record Your First Workflow

**Using CLI:**

```bash
naytrik record "Go to github.com and search for playwright" \
  --name github-search \
  --initial-url https://github.com
```

**Using Python:**

```python
import asyncio
from naytrik import GeminiAutomation, WorkflowRecorder, WorkflowStorage
from naytrik.automation import PlaywrightBrowser

async def main():
    recorder = WorkflowRecorder(workflow_name="my_workflow")
    automation = GeminiAutomation(recorder=recorder)
    browser = PlaywrightBrowser(headless=False)

    await automation.execute_task(
        task="Go to example.com and click 'More information'",
        browser=browser,
        initial_url="https://example.com"
    )

    workflow = recorder.finalize()
    WorkflowStorage().save_workflow(workflow)

asyncio.run(main())
```

### Replay Without AI

```bash
naytrik play github-search
```

```python
from naytrik import WorkflowPlayer

player = WorkflowPlayer(headless=False)
await player.execute_workflow("workflows/definitions/github-search.json")
```

## 🏗️ Architecture

```
naytrik/
├── automation/      # AI-driven browser control (Gemini integration)
├── recording/       # Smart action & selector capture
├── playback/        # Deterministic workflow execution
├── storage/         # Workflow persistence (JSON/YAML)
└── schema/          # Pydantic models for validation
```

### How It Works

1. **Record Phase**: Gemini AI navigates the browser while Naytrik captures every action with multiple selector strategies
2. **Save Phase**: Workflows are saved as JSON/YAML with robust element identification
3. **Playback Phase**: Execute workflows deterministically using captured selectors—no AI needed

### Selector Priority

```
1. CSS Selector     (fastest, most stable)
2. XPath            (complex element paths)
3. Text Content     (human-readable fallback)
4. Coordinates      (last resort)
```

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Quick Start](docs/QUICKSTART.md) | Get up and running in 5 minutes |
| [Architecture](docs/ARCHITECTURE.md) | System design and principles |
| [Enhanced Recording](docs/ENHANCED_RECORDING.md) | Advanced recording features |
| [Examples](examples/) | Ready-to-run code samples |

## 💡 Examples

```bash
examples/
├── basic_recording.py       # Simple record & replay
├── enhanced_recording.py    # Multi-strategy selectors
├── parameterized_workflow.py # Dynamic variables
└── playback_enhanced.py     # Advanced playback options
```

## 🔧 CLI Commands

```bash
# Record a new workflow
naytrik record "your task description" --name workflow-name

# Play back a workflow
naytrik play workflow-name

# List all workflows
naytrik list

# Show workflow details
naytrik show workflow-name
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ using [Playwright](https://playwright.dev/) and [Google Gemini](https://deepmind.google/technologies/gemini/)**

</div>
