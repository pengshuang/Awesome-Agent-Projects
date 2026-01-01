"""Multi-Agent 系统实现"""

import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI

from config.llm_config import llm_config
from config.prompts import prompts_config
from config.settings import settings
from src.models import (
    ProposerOutput, SolverOutput, ValidationResult,
    QAPair, IterationState
)
from src.utils import get_image_data_url, extract_json_from_text, setup_logger


# 设置日志
logger = setup_logger("agents", settings.LOG_DIR, settings.LOG_LEVEL)


class MultimodalLLMClient:
    """多模态 LLM 客户端"""
    
    def __init__(self, config=None):
        self.config = config or llm_config
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def call_with_images(
        self,
        system_prompt: str,
        user_prompt: str,
        image_paths: List[str],
        temperature: Optional[float] = None
    ) -> str:
        """调用支持图片的 LLM"""
        try:
            # 构建消息
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # 构建用户消息（包含文本和图片）
            content = [{"type": "text", "text": user_prompt}]
            
            # 添加图片
            for image_path in image_paths:
                image_url = get_image_data_url(image_path)
                content.append({
                    "type": "image_url",
                    "image_url": {"url": image_url}
                })
            
            messages.append({"role": "user", "content": content})
            
            # 调用 API
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=temperature or self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"LLM 调用失败: {str(e)}")
            raise


class ProposerAgent:
    """提议者 Agent - 生成新的问答对"""
    
    def __init__(self, llm_client: MultimodalLLMClient):
        self.llm_client = llm_client
        self.prompts_config = prompts_config
    
    def propose(
        self,
        image_paths: List[str],
        task_type: str,
        difficulty: float,
        history_qa_pairs: List[QAPair] = None
    ) -> ProposerOutput:
        """生成新的问答对"""
        logger.info(f"提议者开始生成问答对 - 难度: {difficulty}")
        
        try:
            # 格式化 Prompt
            system_prompt, user_prompt = self.prompts_config.format_proposer_prompt(
                task_type=task_type,
                difficulty_level=difficulty,
                history_qa_pairs=[qa.dict() for qa in history_qa_pairs] if history_qa_pairs else None
            )
            
            # 调用 LLM
            response = self.llm_client.call_with_images(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                image_paths=image_paths
            )
            
            # 解析响应
            result = extract_json_from_text(response)
            
            output = ProposerOutput(
                question=result["question"],
                answer=result["answer"]
            )
            
            logger.info(f"提议者生成问题: {output.question[:50]}...")
            return output
        
        except Exception as e:
            logger.error(f"提议者执行失败: {str(e)}")
            raise


class SolverAgent:
    """求解者 Agent - 尝试回答问题"""
    
    def __init__(self, llm_client: MultimodalLLMClient):
        self.llm_client = llm_client
        self.prompts_config = prompts_config
    
    def solve(
        self,
        image_paths: List[str],
        question: str
    ) -> SolverOutput:
        """回答问题"""
        logger.info(f"求解者开始回答问题: {question[:50]}...")
        
        try:
            # 格式化 Prompt
            system_prompt, user_prompt = self.prompts_config.format_solver_prompt(
                question=question
            )
            
            # 调用 LLM
            response = self.llm_client.call_with_images(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                image_paths=image_paths
            )
            
            # 解析响应
            result = extract_json_from_text(response)
            
            output = SolverOutput(answer=result["answer"])
            
            logger.info(f"求解者生成答案: {output.answer[:50]}...")
            return output
        
        except Exception as e:
            logger.error(f"求解者执行失败: {str(e)}")
            raise


class ValidatorAgent:
    """验证者 Agent - 验证答案的正确性"""
    
    def __init__(self, llm_client: MultimodalLLMClient):
        self.llm_client = llm_client
        self.prompts_config = prompts_config
        self.validation_threshold = settings.VALIDATION_THRESHOLD
    
    def validate(
        self,
        image_paths: List[str],
        question: str,
        reference_answer: str,
        predicted_answer: str
    ) -> ValidationResult:
        """验证答案"""
        logger.info(f"验证者开始验证答案")
        
        try:
            # 格式化 Prompt
            system_prompt, user_prompt = self.prompts_config.format_validator_prompt(
                question=question,
                reference_answer=reference_answer,
                predicted_answer=predicted_answer
            )
            
            # 调用 LLM（验证不需要图片，但为了统一接口保留）
            response = self.llm_client.call_with_images(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                image_paths=image_paths,
                temperature=0.1  # 验证时使用较低温度
            )
            
            # 解析响应
            result = extract_json_from_text(response)
            
            validation = ValidationResult(
                is_valid=result["is_valid"],
                similarity_score=result["similarity_score"],
                reason=result["reason"]
            )
            
            logger.info(
                f"验证结果: {'通过' if validation.is_valid else '未通过'} "
                f"(相似度: {validation.similarity_score:.2f})"
            )
            
            return validation
        
        except Exception as e:
            logger.error(f"验证者执行失败: {str(e)}")
            raise
