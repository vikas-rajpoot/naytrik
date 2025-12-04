#!/usr/bin/env python3
"""
Create a working demo workflow that actually works with example.com
"""

import asyncio
from naytrik import WorkflowStorage
from naytrik.schema.workflow import WorkflowDefinition, WorkflowStep
from naytrik.schema.actions import NavigationAction, ClickAction
from naytrik.schema.selectors import ElementContext, SelectorStrategy, SelectorType


async def create_working_demo():
    """Create a demo workflow that actually works with example.com"""
    print("🏗️  Creating working demo workflow...")
    
    # Create element context with proper selector strategies
    learn_more_element = ElementContext(
        target_text="Learn more",
        selector_strategies=[
            SelectorStrategy(
                type=SelectorType.TEXT_EXACT,
                value="Learn more",
                priority=1
            ),
            SelectorStrategy(
                type=SelectorType.CSS,
                value="a[href*='iana.org']",
                priority=2
            ),
            SelectorStrategy(
                type=SelectorType.XPATH,
                value="//a[contains(text(), 'Learn more')]",
                priority=3
            )
        ]
    )
    
    # Create workflow with working steps
    workflow = WorkflowDefinition(
        name="working_demo_workflow",
        description="A working demo that clicks the Learn more link on example.com",
        version="1.0",
        steps=[
            WorkflowStep(
                step_number=1,
                action=NavigationAction(url="https://example.com"),
                description="Navigate to example.com"
            ),
            WorkflowStep(
                step_number=2,
                action=ClickAction(element=learn_more_element),
                description="Click on Learn more link"
            ),
        ],
        input_schema=[],
        metadata={
            "created_by": "demo",
            "tags": ["demo", "working", "example"],
        }
    )
    
    # Save the workflow
    storage = WorkflowStorage("./workflows")
    metadata = storage.save_workflow(
        workflow=workflow,
        generation_mode="manual",
        original_task="Working demo workflow",
        tags=["demo", "working", "test"],
    )
    
    print(f"✅ Working demo workflow created: {metadata.file_path}")
    return metadata.file_path


if __name__ == "__main__":
    asyncio.run(create_working_demo())