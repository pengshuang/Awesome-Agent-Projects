"""Data models for the data synthesis system."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TaskType(str, Enum):
    """Types of data synthesis tasks."""
    LOGICAL_REASONING = "逻辑推理类"
    NUMERICAL_CALCULATION = "数值计算类"
    INFORMATION_QUERY = "信息查询类"
    SUMMARIZATION = "总结摘要类"


class QAPair(BaseModel):
    """Question-Answer pair with metadata."""
    question: str = Field(..., description="The generated question")
    answer: str = Field(..., description="The reference answer")
    reasoning: Optional[str] = Field(None, description="Reasoning for question quality")
    task_type: TaskType = Field(..., description="Type of task")
    iteration: int = Field(..., description="Iteration number when generated")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "根据文档中的信息，作者的观点如何演变？",
                "answer": "作者的观点经历了三个阶段...",
                "reasoning": "这个问题需要整合文档多个部分的信息",
                "task_type": "逻辑推理类",
                "iteration": 1
            }
        }


class ProposerOutput(BaseModel):
    """Output from the Proposer agent."""
    question: str = Field(..., description="Generated question")
    answer: str = Field(..., description="Reference answer")
    reasoning: str = Field(..., description="Reasoning for question difficulty")


class SolverOutput(BaseModel):
    """Output from the Solver agent."""
    reasoning_steps: List[str] = Field(..., description="Step-by-step reasoning")
    final_answer: str = Field(..., description="Final answer to the question")


class ValidatorOutput(BaseModel):
    """Output from the Validator agent."""
    score: float = Field(..., description="Score from 1-10 for answer quality", ge=1, le=10)
    reasoning: str = Field(..., description="Reasoning for the score")
    feedback: Optional[str] = Field(None, description="Detailed feedback on the answer")


class IterationDetail(BaseModel):
    """Details of a single iteration for UI display."""
    iteration: int = Field(..., description="Iteration number")
    proposer_output: Optional[dict] = Field(None, description="Proposer agent output")
    solver_output: Optional[dict] = Field(None, description="Solver agent output")
    validator_output: Optional[dict] = Field(None, description="Validator agent output")
    is_valid: bool = Field(False, description="Whether this iteration produced valid QA")
    timestamp: datetime = Field(default_factory=datetime.now)


class SynthesisState(BaseModel):
    """State for the data synthesis workflow using LangGraph."""
    
    # Input
    document: str = Field(..., description="Source document content")
    task_type: TaskType = Field(..., description="Type of task to generate")
    max_iterations: int = Field(10, description="Maximum iterations")
    
    # Workflow state
    current_iteration: int = Field(0, description="Current iteration number")
    history_buffer: List[QAPair] = Field(default_factory=list, description="Valid QA pairs")
    
    # Current iteration data
    current_question: Optional[str] = None
    current_reference_answer: Optional[str] = None
    current_solver_answer: Optional[str] = None
    current_reasoning: Optional[str] = None
    
    # Results
    valid_pairs: List[QAPair] = Field(default_factory=list, description="Final valid QA pairs")
    failed_attempts: int = Field(0, description="Number of failed validation attempts")
    iteration_details: List[dict] = Field(default_factory=list, description="Details of each iteration")
    
    # Status
    is_complete: bool = Field(False, description="Whether synthesis is complete")
    error: Optional[str] = Field(None, description="Error message if any")
    
    class Config:
        arbitrary_types_allowed = True


class SynthesisRequest(BaseModel):
    """Request for data synthesis."""
    document: str = Field(..., min_length=10, description="Document content")
    task_type: TaskType = Field(..., description="Type of task")
    max_iterations: int = Field(10, ge=1, le=50, description="Maximum iterations")


class SynthesisResult(BaseModel):
    """Result of data synthesis."""
    success: bool
    qa_pairs: List[QAPair]
    total_iterations: int
    failed_attempts: int
    error: Optional[str] = None
    execution_time: Optional[float] = None
