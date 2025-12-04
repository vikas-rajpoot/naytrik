"""
Workflow storage manager.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from naytrik.schema.workflow import WorkflowDefinition, WorkflowMetadata


class WorkflowStorage:
    """
    Manages workflow persistence to filesystem.
    
    Follows Single Responsibility Principle: only handles storage.
    """

    def __init__(self, storage_dir: str = "./workflows"):
        """
        Initialize storage manager.

        Args:
            storage_dir: Directory to store workflows
        """
        self.storage_dir = Path(storage_dir)
        self.workflows_dir = self.storage_dir / "definitions"
        self.metadata_file = self.storage_dir / "metadata.json"

        # Create directories
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

        # Load metadata
        self.metadata: Dict[str, WorkflowMetadata] = {}
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load workflow metadata from disk."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    data = json.load(f)
                    self.metadata = {
                        wf_id: WorkflowMetadata(**wf_data)
                        for wf_id, wf_data in data.items()
                    }
            except Exception as e:
                print(f"Warning: Could not load metadata: {e}")
                self.metadata = {}

    def _save_metadata(self) -> None:
        """Save workflow metadata to disk."""
        with open(self.metadata_file, "w") as f:
            json.dump(
                {wf_id: wf.model_dump(mode="json") for wf_id, wf in self.metadata.items()},
                f,
                indent=2,
                default=str,
            )

    def save_workflow(
        self,
        workflow: WorkflowDefinition,
        workflow_id: Optional[str] = None,
        generation_mode: str = "manual",
        original_task: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> WorkflowMetadata:
        """
        Save a workflow to storage.

        Args:
            workflow: Workflow definition to save
            workflow_id: Optional ID (for updates)
            generation_mode: How workflow was created (manual/ai)
            original_task: Original task description
            tags: Tags for categorization

        Returns:
            WorkflowMetadata for saved workflow
        """
        # Create or update metadata
        if workflow_id and workflow_id in self.metadata:
            # Update existing
            metadata = self.metadata[workflow_id]
            metadata.name = workflow.name
            metadata.description = workflow.description
            metadata.version = workflow.version
            metadata.updated_at = datetime.utcnow()
        else:
            # Create new
            workflow_id = workflow_id or str(uuid4())
            filename = f"{workflow.name.lower().replace(' ', '_')}.json"
            file_path = str(self.workflows_dir / filename)

            metadata = WorkflowMetadata(
                id=workflow_id,
                name=workflow.name,
                description=workflow.description,
                version=workflow.version,
                file_path=file_path,
                generation_mode=generation_mode,
                original_task=original_task,
                tags=tags or [],
            )

        # Save workflow file
        workflow.save_to_file(metadata.file_path)

        # Update metadata
        self.metadata[workflow_id] = metadata
        self._save_metadata()

        print(f"✅ Saved workflow: {workflow.name} ({workflow_id})")
        return metadata

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get workflow by ID."""
        if workflow_id not in self.metadata:
            return None

        metadata = self.metadata[workflow_id]
        return WorkflowDefinition.load_from_file(metadata.file_path)

    def get_workflow_by_name(self, name: str) -> Optional[WorkflowDefinition]:
        """Get workflow by name."""
        for metadata in self.metadata.values():
            if metadata.name.lower() == name.lower():
                return WorkflowDefinition.load_from_file(metadata.file_path)
        return None

    def list_workflows(self) -> List[WorkflowMetadata]:
        """List all workflows."""
        return list(self.metadata.values())

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        if workflow_id not in self.metadata:
            return False

        metadata = self.metadata[workflow_id]

        # Delete file
        try:
            Path(metadata.file_path).unlink()
        except Exception as e:
            print(f"Warning: Could not delete file: {e}")

        # Remove metadata
        del self.metadata[workflow_id]
        self._save_metadata()

        print(f"🗑️  Deleted workflow: {metadata.name}")
        return True

    def search_workflows(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        generation_mode: Optional[str] = None,
    ) -> List[WorkflowMetadata]:
        """Search workflows."""
        results = list(self.metadata.values())

        if generation_mode:
            results = [w for w in results if w.generation_mode == generation_mode]

        if tags:
            results = [w for w in results if any(t in w.tags for t in tags)]

        if query:
            query_lower = query.lower()
            results = [
                w for w in results
                if query_lower in w.name.lower() or query_lower in w.description.lower()
            ]

        return results
