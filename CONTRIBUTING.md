# Contributing to Gemini Workflow Automation

Thank you for your interest in contributing! This guide will help you set up your development environment.

## Development Setup

### 1. Clone and Install

```bash
# Clone the repository
cd gemini-workflow-automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Add your API key
echo "GEMINI_API_KEY=your_key_here" >> .env
```

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=naytrik

# Run specific test
pytest tests/test_recording.py -v
```

### 4. Code Formatting

```bash
# Format code with Black
black src/ tests/ examples/

# Lint with Ruff
ruff check src/ tests/ examples/

# Type checking with mypy
mypy src/
```

## Project Structure

```
src/naytrik/
├── automation/       # AI automation (extend here for new browsers)
├── recording/        # Recording logic (extend for new capture methods)
├── playback/         # Execution engine (extend for new actions)
├── storage/          # Persistence layer (extend for databases)
├── schema/           # Data models (extend for new action types)
└── utils/            # Utilities (add helpers here)
```

## Adding Features

### Adding a New Action Type

1. **Define the action in schema/actions.py**:
```python
class MyNewAction(BaseAction):
    type: Literal["my_new_action"] = "my_new_action"
    param1: str
    param2: int
```

2. **Add to Action union**:
```python
Action = Union[..., MyNewAction]
```

3. **Add ActionType enum value**:
```python
class ActionType(str, Enum):
    MY_NEW_ACTION = "my_new_action"
```

4. **Implement in recorder** (recording/recorder.py):
```python
def _create_action(self, action_type, ...):
    elif action_type == ActionType.MY_NEW_ACTION:
        return MyNewAction(...)
```

5. **Implement in executor** (playback/executor.py):
```python
async def _execute_action(self, action):
    elif action.type == "my_new_action":
        return await self._execute_my_new_action(action)

async def _execute_my_new_action(self, action: MyNewAction):
    # Implementation
    pass
```

6. **Write tests**:
```python
def test_my_new_action():
    action = MyNewAction(param1="test", param2=42)
    # Test action creation and execution
```

### Adding a New Browser Implementation

1. **Create new file** (automation/my_browser.py):
```python
from naytrik.automation.browser import IBrowser, BrowserState

class MyBrowser(IBrowser):
    async def initialize(self):
        # Setup
        pass
    
    async def click_at(self, x, y):
        # Implementation
        return BrowserState(...)
    
    # Implement all IBrowser methods
```

2. **Export in __init__.py**:
```python
from .my_browser import MyBrowser
__all__ = [..., "MyBrowser"]
```

3. **Write tests**:
```python
async def test_my_browser():
    browser = MyBrowser()
    await browser.initialize()
    # Test all methods
```

### Adding a New Selector Strategy

1. **Add to SelectorType enum** (schema/selectors.py):
```python
class SelectorType(str, Enum):
    MY_STRATEGY = "my_strategy"
```

2. **Implement in ElementFinder** (playback/element_finder.py):
```python
async def _try_strategy(self, strategy):
    elif strategy.type == SelectorType.MY_STRATEGY:
        # Find element using your strategy
        return locator
```

3. **Write tests**:
```python
async def test_my_selector_strategy():
    # Test selector finding
    pass
```

## Code Style

### Python Style Guide

- **Line Length**: 120 characters
- **Docstrings**: Use Google style
- **Type Hints**: Required for all public APIs
- **Imports**: Organized with isort

Example:
```python
from typing import Optional

class MyClass:
    """
    Brief description.
    
    Longer description with details about the class.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    """
    
    def my_method(self, arg: str) -> Optional[int]:
        """
        Brief description of method.
        
        Args:
            arg: Description of argument
            
        Returns:
            Description of return value
            
        Raises:
            ValueError: When arg is invalid
        """
        pass
```

### Commit Messages

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Build/tooling changes

Example:
```
feat: add support for drag and drop actions

- Implement DragDropAction schema
- Add executor logic for drag and drop
- Add tests for drag and drop
- Update documentation
```

## Testing Guidelines

### Unit Tests

Test individual components in isolation:

```python
def test_workflow_recorder_basic():
    recorder = WorkflowRecorder("test", "desc")
    recorder.record_action(ActionType.CLICK, ...)
    workflow = recorder.finalize()
    
    assert workflow.name == "test"
    assert len(workflow.steps) == 1
```

### Integration Tests

Test component interactions:

```python
async def test_automation_with_recording():
    recorder = WorkflowRecorder("test", "desc")
    automation = GeminiAutomation(recorder=recorder)
    browser = MockBrowser()
    
    await automation.execute_task("test task", browser)
    workflow = recorder.finalize()
    
    assert len(workflow.steps) > 0
```

### E2E Tests

Test complete workflows:

```python
async def test_full_workflow_lifecycle():
    # Record
    recorder = WorkflowRecorder("test", "desc")
    # ... record workflow
    workflow = recorder.finalize()
    
    # Save
    storage = WorkflowStorage()
    metadata = storage.save_workflow(workflow)
    
    # Load and execute
    player = WorkflowPlayer()
    result = await player.execute_workflow(metadata.file_path)
    
    assert result.success
```

## Documentation

### Code Documentation

- All public APIs must have docstrings
- Use type hints
- Include examples in docstrings for complex functions

### README Updates

When adding features:
1. Update main README.md
2. Update relevant sections in ARCHITECTURE.md
3. Add examples if applicable
4. Update QUICKSTART.md if it affects getting started

### Architecture Documentation

For significant changes:
1. Update ARCHITECTURE.md
2. Add diagrams if helpful (ASCII art is fine)
3. Explain design decisions

## Pull Request Process

1. **Fork and create branch**:
```bash
git checkout -b feat/my-new-feature
```

2. **Make changes**:
- Write code
- Add tests
- Update documentation

3. **Format and lint**:
```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

4. **Run tests**:
```bash
pytest --cov=naytrik
```

5. **Commit with conventional commits**:
```bash
git commit -m "feat: add my new feature"
```

6. **Push and create PR**:
```bash
git push origin feat/my-new-feature
```

7. **PR Description**:
- Describe what changes were made
- Why the changes were needed
- How to test the changes
- Any breaking changes

## Code Review Guidelines

### For Reviewers

- Check code follows SOLID principles
- Verify tests are comprehensive
- Ensure documentation is updated
- Look for potential edge cases
- Verify type hints are correct

### For Contributors

- Respond to feedback promptly
- Be open to suggestions
- Explain your design decisions
- Update PR based on feedback

## Release Process

1. Update version in pyproject.toml
2. Update CHANGELOG.md
3. Create git tag
4. Build package: `python -m build`
5. Publish: `twine upload dist/*`

## Getting Help

- Open an issue for bugs
- Use discussions for questions
- Check existing issues first
- Provide minimal reproduction cases

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
