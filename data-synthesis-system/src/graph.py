"""LangGraph workflow for data synthesis with iterative curriculum."""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from loguru import logger

from config import settings
from src.models import (
    SynthesisState,
    QAPair,
    TaskType,
)
from src.agents import ProposerAgent, SolverAgent, ValidatorAgent


class DataSynthesisGraph:
    """LangGraph workflow for multi-agent data synthesis."""
    
    def __init__(self):
        """Initialize the synthesis graph with three agents."""
        self.proposer = ProposerAgent()
        self.solver = SolverAgent()
        self.validator = ValidatorAgent()
        
        # Build the graph
        self.graph = self._build_graph()
        logger.info("DataSynthesisGraph initialized")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""
        # Create workflow
        workflow = StateGraph(dict)
        
        # Add nodes
        workflow.add_node("propose", self._propose_node)
        workflow.add_node("solve", self._solve_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("update", self._update_node)
        
        # Set entry point
        workflow.set_entry_point("propose")
        
        # Add edges
        workflow.add_edge("propose", "solve")
        workflow.add_edge("solve", "validate")
        workflow.add_edge("validate", "update")
        
        # Add conditional edge from update
        workflow.add_conditional_edges(
            "update",
            self._should_continue,
            {
                "continue": "propose",
                "end": END
            }
        )
        
        return workflow.compile()
    
    def _propose_node(self, state: dict) -> dict:
        """Proposer agent generates a new QA pair."""
        logger.info(
            "=== Iteration {}/{} ===",
            state["current_iteration"] + 1,
            state["max_iterations"]
        )
        logger.info("Proposer generating new question...")
        
        # Initialize iteration detail
        if "iteration_details" not in state:
            state["iteration_details"] = []
        
        iteration_detail = {
            "iteration": state["current_iteration"] + 1,
            "proposer_output": None,
            "solver_output": None,
            "validator_output": None,
            "is_valid": False,
        }
        
        try:
            output = self.proposer.generate_qa_pair(
                document=state["document"],
                task_type=TaskType(state["task_type"]),
                history_buffer=state["history_buffer"]
            )
            
            # Handle both ProposerOutput object and dict
            if isinstance(output, dict):
                question = output.get("question", "")
                answer = output.get("answer", "")
                reasoning = output.get("reasoning", "")
            else:
                question = output.question
                answer = output.answer
                reasoning = output.reasoning
            
            state["current_question"] = question
            state["current_reference_answer"] = answer
            state["current_reasoning"] = reasoning
            
            # Save proposer output to iteration detail
            iteration_detail["proposer_output"] = {
                "question": question,
                "answer": answer,
                "reasoning": reasoning,
            }
            
            logger.success("Question generated: {}", question[:100])
            
        except Exception as e:
            logger.error("Proposer failed: {}", str(e))
            # Don't stop the workflow, just use default values
            state["current_question"] = "[生成失败]"
            state["current_reference_answer"] = "发生错误"
            state["current_reasoning"] = f"错误: {str(e)}"
            iteration_detail["proposer_output"] = {
                "question": "[生成失败]",
                "answer": "发生错误",
                "reasoning": f"错误: {str(e)}",
            }
        
        # Store the iteration detail (will be updated by subsequent nodes)
        state["current_iteration_detail"] = iteration_detail
        
        return state
    
    def _solve_node(self, state: dict) -> dict:
        """Solver agent attempts to answer the question."""
        logger.info("Solver attempting to answer...")
        
        try:
            output = self.solver.solve(
                document=state["document"],
                question=state["current_question"]
            )
            
            # Handle both SolverOutput object and dict
            if isinstance(output, dict):
                reasoning_steps = output.get("reasoning_steps", [])
                final_answer = output.get("final_answer", "")
            else:
                reasoning_steps = output.reasoning_steps
                final_answer = output.final_answer
            
            state["current_solver_answer"] = final_answer
            
            # Save solver output to iteration detail
            if "current_iteration_detail" in state:
                state["current_iteration_detail"]["solver_output"] = {
                    "reasoning_steps": reasoning_steps,
                    "final_answer": final_answer,
                }
            
            logger.success("Solver answer: {}", final_answer[:100])
            
        except Exception as e:
            logger.error("Solver failed: {}", str(e))
            # Don't stop the workflow, just use default value
            state["current_solver_answer"] = f"求解失败: {str(e)}"
            if "current_iteration_detail" in state:
                state["current_iteration_detail"]["solver_output"] = {
                    "reasoning_steps": ["发生错误"],
                    "final_answer": f"错误: {str(e)}",
                }
        
        return state
    
    def _validate_node(self, state: dict) -> dict:
        """Validator agent checks the answer."""
        logger.info("Validator checking answer...")
        
        try:
            output = self.validator.validate(
                question=state["current_question"],
                reference_answer=state["current_reference_answer"],
                solver_answer=state["current_solver_answer"]
            )
            
            # Handle both ValidatorOutput object and dict
            if isinstance(output, dict):
                score = output.get("score", 0)
                reasoning = output.get("reasoning", "")
                feedback = output.get("feedback", "")
            else:
                score = output.score
                reasoning = output.reasoning
                feedback = output.feedback
            
            # Get score threshold from settings or state
            score_threshold = state.get("score_threshold", settings.score_threshold)
            is_valid = score >= score_threshold
            
            # Save validator output to iteration detail
            if "current_iteration_detail" in state:
                state["current_iteration_detail"]["validator_output"] = {
                    "score": score,
                    "is_valid": is_valid,
                    "reasoning": reasoning,
                    "feedback": feedback,
                }
                state["current_iteration_detail"]["is_valid"] = is_valid
            
            if is_valid:
                logger.success("✓ Validation PASSED (score: {}/10, threshold: {})", score, score_threshold)
                # Create QA pair
                qa_pair = {
                    "question": state["current_question"],
                    "answer": state["current_reference_answer"],
                    "reasoning": state["current_reasoning"],
                    "task_type": state["task_type"],
                    "iteration": state["current_iteration"] + 1,
                    "score": score,  # Add score to QA pair
                }
                
                # Add to valid pairs
                if "valid_pairs" not in state:
                    state["valid_pairs"] = []
                state["valid_pairs"].append(qa_pair)
                
                # Add to history buffer
                if "history_buffer" not in state:
                    state["history_buffer"] = []
                state["history_buffer"].append(qa_pair)
                
                logger.info("Valid QA pairs: {}", len(state["valid_pairs"]))
            else:
                logger.warning("✗ Validation FAILED (score: {}/10 < threshold: {}): {}", score, score_threshold, feedback)
                state["failed_attempts"] = state.get("failed_attempts", 0) + 1
            
        except Exception as e:
            logger.error("Validator failed: {}", str(e))
            # Don't stop the workflow, treat as failed validation
            if "current_iteration_detail" in state:
                state["current_iteration_detail"]["validator_output"] = {
                    "score": 1.0,
                    "is_valid": False,
                    "reasoning": f"验证过程出错: {str(e)}",
                    "feedback": "无法完成验证",
                }
                state["current_iteration_detail"]["is_valid"] = False
            state["failed_attempts"] = state.get("failed_attempts", 0) + 1
        
        return state
    
    def _update_node(self, state: dict) -> dict:
        """Update iteration counter and check completion."""
        # Add current iteration detail to list
        if "current_iteration_detail" in state:
            if "iteration_details" not in state:
                state["iteration_details"] = []
            state["iteration_details"].append(state["current_iteration_detail"])
            # Clean up temporary field
            del state["current_iteration_detail"]
        
        state["current_iteration"] += 1
        
        # Check if we should continue
        if state["current_iteration"] >= state["max_iterations"]:
            state["is_complete"] = True
            logger.info("Max iterations reached. Synthesis complete.")
        elif state.get("error"):
            state["is_complete"] = True
            logger.error("Error occurred. Stopping synthesis.")
        
        return state
    
    def _should_continue(self, state: dict) -> str:
        """Determine if we should continue or end."""
        if state.get("is_complete", False):
            return "end"
        return "continue"
    
    def stream(self, state_dict: dict):
        """
        Run the synthesis workflow with streaming output.
        
        Args:
            state_dict: Initial state dictionary
        
        Yields:
            State updates after each node execution
        """
        logger.info("Starting data synthesis workflow (streaming)")
        logger.info("Task type: {}", state_dict["task_type"])
        logger.info("Max iterations: {}", state_dict["max_iterations"])
        
        try:
            # Initialize state
            if "current_iteration" not in state_dict:
                state_dict["current_iteration"] = 0
            if "history_buffer" not in state_dict:
                state_dict["history_buffer"] = []
            if "valid_pairs" not in state_dict:
                state_dict["valid_pairs"] = []
            if "failed_attempts" not in state_dict:
                state_dict["failed_attempts"] = 0
            if "is_complete" not in state_dict:
                state_dict["is_complete"] = False
            if "iteration_details" not in state_dict:
                state_dict["iteration_details"] = []
            
            # Stream the graph execution with recursion limit
            for output in self.graph.stream(state_dict, {"recursion_limit": 100}):
                # output is a dict with node name as key
                yield output
            
        except Exception as e:
            logger.error("Workflow streaming failed: {}", str(e))
            raise
    
    def run(self, state_dict: dict) -> dict:
        """
        Run the synthesis workflow.
        
        Args:
            state_dict: Initial state dictionary
        
        Returns:
            Final state dictionary
        """
        logger.info("Starting data synthesis workflow")
        logger.info("Task type: {}", state_dict["task_type"])
        logger.info("Max iterations: {}", state_dict["max_iterations"])
        
        try:
            # Initialize state
            if "current_iteration" not in state_dict:
                state_dict["current_iteration"] = 0
            if "history_buffer" not in state_dict:
                state_dict["history_buffer"] = []
            if "valid_pairs" not in state_dict:
                state_dict["valid_pairs"] = []
            if "failed_attempts" not in state_dict:
                state_dict["failed_attempts"] = 0
            if "is_complete" not in state_dict:
                state_dict["is_complete"] = False
            if "iteration_details" not in state_dict:
                state_dict["iteration_details"] = []
            
            # Run the graph with recursion limit
            final_state = self.graph.invoke(state_dict, {"recursion_limit": 100})
            
            logger.info("=== Synthesis Complete ===")
            logger.info("Total iterations: {}", final_state["current_iteration"])
            logger.info("Valid QA pairs: {}", len(final_state.get("valid_pairs", [])))
            logger.info("Failed attempts: {}", final_state.get("failed_attempts", 0))
            
            return final_state
            
        except Exception as e:
            logger.error("Workflow failed: {}", str(e))
            raise
