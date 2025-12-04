"""
Workflow definition schema.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Literal, Optional, Union

import yaml
from pydantic import BaseModel, Field

from naytrik.schema.actions import Action


class WorkflowInputSchema(BaseModel):
    """Schema definition for workflow inputs (variables)."""

    name: str = Field(..., description="Input parameter name")
    type: Literal["string", "number", "bool"] = Field(..., description="Input parameter type")
    format: Optional[str] = Field(None, description="Format specification for the input")
    required: bool = Field(default=True, description="Whether this input is required")
    default: Optional[Union[str, int, float, bool]] = Field(None, description="Default value")
    description: Optional[str] = Field(None, description="Description of the input")


class WorkflowStep(BaseModel):
    """A single step in the workflow."""

    step_number: int = Field(..., description="Sequential step number")
    action: Action = Field(..., description="Action to perform")
    
    class Config:
        extra = "allow"


class WorkflowDefinition(BaseModel):
    """Complete workflow definition."""

    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    version: str = Field(default="1.0", description="Workflow version")
    
    # Steps
    steps: List[WorkflowStep] = Field(..., min_length=1, description="Ordered list of workflow steps")
    
    # Input parameters
    input_schema: List[WorkflowInputSchema] = Field(
        default_factory=list, description="Input parameter definitions"
    )
    
    # Configuration
    default_wait_time: float = Field(default=0.5, description="Default wait time between steps (seconds)")
    
    # Metadata (optional)
    workflow_analysis: Optional[str] = Field(None, description="Analysis/reasoning about the workflow")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
    class Config:
        extra = "allow"

    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> "WorkflowDefinition":
        """Load workflow from JSON or YAML file."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Workflow file not found: {file_path}")
        
        with open(path, "r") as f:
            if path.suffix in [".yaml", ".yml"]:
                import yaml
                data = yaml.safe_load(f)
                return cls(**data)
            else:
                import json
                data = json.load(f)
                return cls(**data)

    def save_to_file(self, file_path: Union[str, Path], format: str = "json") -> Path:
        """Save workflow to file in JSON or YAML format."""
        path = Path(file_path)
        
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Auto-detect format from extension if not specified
        if format == "yaml" and path.suffix not in [".yaml", ".yml"]:
            path = path.with_suffix(".yaml")
        elif format == "json" and path.suffix != ".json":
            path = path.with_suffix(".json")
        
        with open(path, "w") as f:
            if format == "yaml":
                import yaml
                yaml.dump(self.model_dump(), f, default_flow_style=False, indent=2)
            else:
                import json
                json.dump(self.model_dump(), f, indent=2)
        
        return path


class WorkflowMetadata(BaseModel):
    """Metadata for a stored workflow."""

    id: str = Field(..., description="Unique workflow ID")
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    version: str = Field(default="1.0", description="Workflow version")
    
    # File info
    file_path: str = Field(..., description="Path to workflow file")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Generation info
    generation_mode: str = Field(default="manual", description="How workflow was created (manual/ai)")
    original_task: Optional[str] = Field(None, description="Original task description (for AI-generated)")
    
    # Categorization
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
    class Config:
        extra = "allow"


class WorkflowExecutionResult(BaseModel):
    """Result of workflow execution."""

    success: bool = Field(..., description="Whether execution succeeded")
    workflow_name: str = Field(..., description="Name of executed workflow")
    steps_completed: int = Field(default=0, description="Number of steps completed")
    total_steps: int = Field(..., description="Total number of steps")
    
    # Output data
    extracted_data: Optional[dict] = Field(None, description="Extracted data from execution")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Timing
    execution_time: float = Field(..., description="Total execution time in seconds")
    
    # Detailed step results
    step_results: List[dict] = Field(default_factory=list, description="Results for each step")
