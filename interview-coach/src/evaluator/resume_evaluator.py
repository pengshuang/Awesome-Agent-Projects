"""
简历评估引擎
基于 LLM 对简历进行多维度评估和打分
"""

import time
from typing import Dict, Any, Optional

from openai import OpenAI
from loguru import logger

from config import get_llm_client
from config.prompts import PromptManager
from src.constants import (
    SUCCESS_EVALUATION_COMPLETED,
    INFO_EVALUATING_RESUME,
)


class ResumeEvaluator:
    """
    简历评估器
    
    功能：
    1. 多维度评分
    2. 优缺点分析
    3. 改进建议
    """
    
    def __init__(self):
        """
        初始化简历评估器
        """
        # 获取 LLM 客户端
        self.client, self.model, self.temperature = get_llm_client()
        
        logger.info("简历评估器已初始化")
    
    def evaluate(
        self,
        resume_content: str,
        position: Optional[str] = None,
        requirements: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        评估简历
        
        Args:
            resume_content: 简历内容
            position: 目标岗位（可选）
            requirements: 岗位要求（可选）
            
        Returns:
            评估结果字典
        """
        logger.info(f"{INFO_EVALUATING_RESUME}")
        start_time = time.time()
        
        # 使用 PromptManager 构建评估提示词
        prompt = PromptManager.get_resume_evaluation_prompt(
            resume_content=resume_content,
            position=position or "未指定",
            requirements=requirements or "无特殊要求",
        )
        
        # 打印Prompt日志
        logger.info(f"[LLM API] 简历评估 - Prompt:\n{'-'*60}\n{prompt}\n{'-'*60}")
        
        # 调用 LLM 进行评估
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            evaluation_text = response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise
        
        elapsed_time = time.time() - start_time
        
        logger.info(f"{SUCCESS_EVALUATION_COMPLETED} | 耗时: {elapsed_time:.2f}秒")
        
        # 返回评估结果
        return {
            "evaluation": evaluation_text,
            "resume_content": resume_content,
            "position": position,
            "requirements": requirements,
            "metadata": {
                "elapsed_time": elapsed_time,
                "model": self.model,
            }
        }
    
    def quick_score(self, resume_content: str) -> Dict[str, Any]:
        """
        快速打分（只返回分数，不详细分析）
        
        Args:
            resume_content: 简历内容
            
        Returns:
            快速评分结果
        """
        logger.info("执行快速评分...")
        start_time = time.time()
        
        # 使用 PromptManager 获取快速评分 Prompt
        prompt = PromptManager.get_quick_score_prompt(resume_content)
        
        # 打印Prompt日志
        logger.info(f"[LLM API] 快速评分 - Prompt:\n{'-'*60}\n{prompt}\n{'-'*60}")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            score_text = response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise
        
        elapsed_time = time.time() - start_time
        
        return {
            "score_text": score_text,
            "metadata": {
                "elapsed_time": elapsed_time,
                "model": self.model,
            }
        }
    
    def suggest_improvements(self, resume_content: str) -> Dict[str, Any]:
        """
        提供改进建议
        
        Args:
            resume_content: 简历内容
            
        Returns:
            改进建议
        """
        logger.info("生成改进建议...")
        start_time = time.time()
        
        # 使用 PromptManager 获取改进建议 Prompt
        prompt = PromptManager.get_improvement_suggestions_prompt(resume_content)
        
        # 打印Prompt日志
        logger.info(f"[LLM API] 改进建议 - Prompt:\n{'-'*60}\n{prompt}\n{'-'*60}")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            suggestions = response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise
        
        elapsed_time = time.time() - start_time
        
        return {
            "suggestions": suggestions,
            "metadata": {
                "elapsed_time": elapsed_time,
                "model": self.model,
            }
        }
