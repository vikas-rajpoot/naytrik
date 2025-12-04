"""
Command-line interface for Gemini Workflow Automation.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Gemini Workflow Automation CLI"""
    pass


@main.command()
@click.argument("task")
@click.option("--name", "-n", required=True, help="Workflow name")
@click.option("--description", "-d", default="", help="Workflow description")
@click.option("--initial-url", "-u", help="Starting URL", default=None) 
@click.option("--api-key", "-k", envvar="GEMINI_API_KEY", help="Gemini API key")
@click.option("--model", "-m", envvar="GEMINI_MODEL_NAME", default="gemini-2.5-computer-use-preview-10-2025", help="Gemini model to use")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output", default=True) 
@click.option("--record-screenshots", is_flag=True, help="Record screenshots", default=True) 
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
    """Record a new workflow using AI automation."""
    click.echo(f"🎥 Recording workflow: {name}")
    click.echo(f"📝 Task: {task}")
    click.echo(f"🤖 Model: {model}")

    # Import here to avoid circular imports
    from naytrik import GeminiAutomation, WorkflowRecorder, WorkflowStorage
    from naytrik.automation.playwright_browser import PlaywrightBrowser

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

            click.echo(f"✅ Workflow saved: {metadata.file_path}")
            click.echo(f"📊 Steps recorded: {recorder.get_step_count()}")
            click.echo(f"⏱️  Duration: {recorder.get_duration():.1f}s")

        finally:
            await browser.close()

    asyncio.run(run_recording())


@main.command()
@click.argument("workflow_file")
@click.option("--var", "-v", multiple=True, help="Variable (name=value)")
@click.option("--headless", is_flag=True, help="Run in headless mode")
@click.option("--start-step", default=1, help="Start from step N")
def execute(
    workflow_file: str,
    var: tuple,
    headless: bool,
    start_step: int,
):
    """Execute a workflow without AI."""
    click.echo(f"▶️  Executing workflow: {workflow_file}")

    # Parse variables
    variables = {}
    for v in var:
        if "=" in v:
            key, value = v.split("=", 1)
            variables[key] = value

    # Import here
    from naytrik import WorkflowPlayer

    async def run_workflow():
        player = WorkflowPlayer(headless=headless)

        result = await player.execute_workflow(
            workflow_path=workflow_file,
            variables=variables,
            start_step=start_step,
        )

        if result.success:
            click.echo(f"✅ Workflow completed successfully")
            click.echo(f"📊 Steps: {result.steps_completed}/{result.total_steps}")
            click.echo(f"⏱️  Time: {result.execution_time:.1f}s")
        else:
            click.echo(f"❌ Workflow failed: {result.error_message}", err=True)
            sys.exit(1)

    asyncio.run(run_workflow())


@main.command()
@click.option("--tag", "-t", multiple=True, help="Filter by tag")
@click.option("--mode", "-m", type=click.Choice(["all", "ai", "manual"]), default="all")
def list(tag: tuple, mode: str):
    """List all workflows."""
    from naytrik import WorkflowStorage

    storage = WorkflowStorage()

    # Filter
    generation_mode = None if mode == "all" else mode
    tags = list(tag) if tag else None

    workflows = storage.search_workflows(tags=tags, generation_mode=generation_mode)

    if not workflows:
        click.echo("No workflows found")
        return

    click.echo(f"\n📚 Found {len(workflows)} workflow(s):\n")

    for wf in workflows:
        click.echo(f"  • {wf.name} ({wf.id})")
        click.echo(f"    {wf.description}")
        click.echo(f"    Version: {wf.version} | Mode: {wf.generation_mode}")
        click.echo(f"    File: {wf.file_path}")
        if wf.tags:
            click.echo(f"    Tags: {', '.join(wf.tags)}")
        click.echo()


@main.command()
@click.argument("workflow_id")
def delete(workflow_id: str):
    """Delete a workflow."""
    from naytrik import WorkflowStorage

    storage = WorkflowStorage()

    if click.confirm(f"Delete workflow {workflow_id}?"):
        if storage.delete_workflow(workflow_id):
            click.echo("✅ Workflow deleted")
        else:
            click.echo("❌ Workflow not found", err=True)


@main.command()
@click.argument("workflow_file")
def info(workflow_file: str):
    """Show workflow information."""
    from naytrik.schema.workflow import WorkflowDefinition

    workflow = WorkflowDefinition.load_from_file(workflow_file)

    click.echo(f"\n📄 Workflow: {workflow.name}")
    click.echo(f"📝 Description: {workflow.description}")
    click.echo(f"🔢 Version: {workflow.version}")
    click.echo(f"📊 Steps: {len(workflow.steps)}")

    if workflow.input_schema:
        click.echo(f"\n🔤 Input Variables:")
        for inp in workflow.input_schema:
            required = " (required)" if inp.required else ""
            click.echo(f"  • {inp.name}: {inp.type}{required}")
            if inp.description:
                click.echo(f"    {inp.description}")

    click.echo(f"\n📋 Steps:")
    for step in workflow.steps[:10]:  # Show first 10 steps
        click.echo(f"  {step.step_number}. {step.action.type}")
        if step.action.description:
            click.echo(f"     {step.action.description}")

    if len(workflow.steps) > 10:
        click.echo(f"  ... and {len(workflow.steps) - 10} more steps")


if __name__ == "__main__":
    main()
