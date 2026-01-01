"""Agent implementations for data synthesis."""

import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from loguru import logger

from config import get_llm, PROMPTS, settings
from src.models import (
    ProposerOutput,
    SolverOutput,
    ValidatorOutput,
    QAPair,
    TaskType,
)


class ProposerAgent:
    """Proposer agent that generates new QA pairs with iterative curriculum."""
    
    def __init__(self):
        self.llm = get_llm(
            model_name=settings.proposer_model,
            temperature=settings.temperature
        )
        logger.info("ProposerAgent initialized with model: {}", settings.proposer_model)
    
    def generate_qa_pair(
        self,
        document: str,
        task_type: TaskType,
        history_buffer: list[QAPair] = None
    ) -> ProposerOutput:
        """
        Generate a new QA pair based on document and history.
        
        Args:
            document: Source document content
            task_type: Type of task to generate
            history_buffer: Previous valid QA pairs for curriculum learning
        
        Returns:
            ProposerOutput with question, answer, and reasoning
        """
        logger.info(
            "Generating QA pair for task type: {}, history size: {}",
            task_type.value,
            len(history_buffer) if history_buffer else 0
        )
        
        # Format history if available
        history_text = ""
        if history_buffer:
            history_text = "\n\n".join([
                f"问题 {i+1}: {qa['question'] if isinstance(qa, dict) else qa.question}\n答案: {qa['answer'] if isinstance(qa, dict) else qa.answer}"
                for i, qa in enumerate(history_buffer)
            ])
        
        # Select prompt based on whether we have history
        if not history_buffer:
            user_prompt = PROMPTS["proposer"]["user_first"].format(
                document=document,
                task_type=task_type.value
            )
        else:
            user_prompt = PROMPTS["proposer"]["user_iterative"].format(
                document=document,
                task_type=task_type.value,
                history=history_text
            )
        
        messages = [
            SystemMessage(content=PROMPTS["proposer"]["system"]),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            content = response.content
            
            # Extract JSON from response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError as json_error:
                logger.error("Failed to parse JSON: {}", str(json_error))
                logger.debug("Raw content: {}", content[:500])
                # Return a default structure when JSON parsing fails
                return {
                    "question": "[JSON解析失败，请检查LLM输出]",
                    "answer": "生成的内容格式错误",
                    "reasoning": f"JSON解析错误: {str(json_error)}"
                }
            
            # Validate and create Pydantic model
            try:
                output = ProposerOutput(**result)
            except Exception as validation_error:
                logger.error("Failed to validate output: {}", str(validation_error))
                logger.debug("Raw result: {}", result)
                # Return dict if Pydantic validation fails
                return result
            
            logger.success("Successfully generated QA pair")
            logger.debug("Question: {}", output.question[:100])
            
            return output
            
        except Exception as e:
            logger.error("Failed to generate QA pair: {}", str(e))
            # Return default instead of raising
            return {
                "question": "[生成失败]",
                "answer": "发生未预期的错误",
                "reasoning": f"错误: {str(e)}"
            }


class SolverAgent:
    """Solver agent that attempts to answer questions based on the document."""
    
    def __init__(self):
        self.llm = get_llm(
            model_name=settings.solver_model,
            temperature=settings.temperature
        )
        logger.info("SolverAgent initialized with model: {}", settings.solver_model)
    
    def solve(self, document: str, question: str) -> SolverOutput:
        """
        Solve a question based on the document.
        
        Args:
            document: Source document content
            question: Question to answer
        
        Returns:
            SolverOutput with reasoning steps and final answer
        """
        logger.info("Solving question: {}", question[:100])
        
        user_prompt = PROMPTS["solver"]["user"].format(
            document=document,
            question=question
        )
        
        messages = [
            SystemMessage(content=PROMPTS["solver"]["system"]),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            content = response.content
            
            # Extract JSON from response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError as json_error:
                logger.error("Failed to parse JSON: {}", str(json_error))
                logger.debug("Raw content: {}", content[:500])
                # Return a default structure when JSON parsing fails
                return {
                    "reasoning_steps": ["JSON解析失败，无法提取推理步骤"],
                    "final_answer": f"生成的内容格式错误: {str(json_error)}"
                }
            
            # Validate and create Pydantic model
            try:
                output = SolverOutput(**result)
            except Exception as validation_error:
                logger.error("Failed to validate solver output: {}", str(validation_error))
                logger.debug("Raw result: {}", result)
                return result
            
            logger.success("Successfully solved question")
            logger.debug("Final answer: {}", output.final_answer[:100])
            
            return output
            
        except Exception as e:
            logger.error("Failed to solve question: {}", str(e))
            # Return default instead of raising
            return {
                "reasoning_steps": ["发生未预期的错误"],
                "final_answer": f"错误: {str(e)}"
            }


class ValidatorAgent:
    """Validator agent that checks if solver's answer matches reference answer."""
    
    def __init__(self):
        self.llm = get_llm(
            model_name=settings.validator_model,
            temperature=settings.temperature
        )
        logger.info("ValidatorAgent initialized with model: {}", settings.validator_model)
    
    def validate(
        self,
        question: str,
        reference_answer: str,
        solver_answer: str
    ) -> ValidatorOutput:
        """
        Validate if solver's answer matches reference answer.
        
        Args:
            question: The question being answered
            reference_answer: Reference answer from proposer
            solver_answer: Solver's answer to validate
        
        Returns:
            ValidatorOutput with validation result and reasoning
        """
        logger.info("Validating answer for question: {}", question[:100])
        
        user_prompt = PROMPTS["validator"]["user"].format(
            question=question,
            reference_answer=reference_answer,
            solver_answer=solver_answer
        )
        
        messages = [
            SystemMessage(content=PROMPTS["validator"]["system"]),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            content = response.content
            
            # Extract JSON from response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError as json_error:
                logger.error("Failed to parse JSON: {}", str(json_error))
                logger.debug("Raw content: {}", content[:500])
                # Return a default structure when JSON parsing fails
                return {
                    "score": 1.0,
                    "reasoning": f"JSON解析失败: {str(json_error)}",
                    "feedback": "生成的验证结果格式错误"
                }
            
            # Validate and create Pydantic model
            try:
                output = ValidatorOutput(**result)
            except Exception as validation_error:
                logger.error("Failed to validate validator output: {}", str(validation_error))
                logger.debug("Raw result: {}", result)
                return result
            
            logger.success(
                "Validation complete: score = {}/10",
                output.score
            )
            
            return output
            
        except Exception as e:
            logger.error("Failed to validate answer: {}", str(e))
            # Return default instead of raising
            return {
                "score": 1.0,
                "reasoning": f"验证过程发生错误: {str(e)}",
                "feedback": "无法完成验证"
            }
