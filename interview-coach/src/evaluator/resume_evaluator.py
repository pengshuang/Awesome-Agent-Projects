"""
简历评估引擎
基于 LLM 对简历进行多维度评估和打分
"""

import time
from typing import Dict, Any, Optional

from openai import OpenAI
from loguru import logger

from config import get_llm_client
from src.constants import (
    SUCCESS_EVALUATION_COMPLETED,
    INFO_EVALUATING_RESUME,
    DEFAULT_EVALUATION_PROMPT,
    EVALUATION_DIMENSIONS,
)


class ResumeEvaluator:
    """
    简历评估器
    
    功能：
    1. 多维度评分
    2. 优缺点分析
    3. 改进建议
    """
    
    def __init__(self, custom_prompt: Optional[str] = None):
        """
        初始化简历评估器
        
        Args:
            custom_prompt: 自定义评估提示词
        """
        self.evaluation_prompt = custom_prompt or DEFAULT_EVALUATION_PROMPT
        
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
        
        # 构建评估提示词
        prompt = self._build_evaluation_prompt(
            resume_content=resume_content,
            position=position,
            requirements=requirements,
        )
        
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
    
    def _build_evaluation_prompt(
        self,
        resume_content: str,
        position: Optional[str] = None,
        requirements: Optional[str] = None,
    ) -> str:
        """
        构建评估提示词
        
        Args:
            resume_content: 简历内容
            position: 目标岗位
            requirements: 岗位要求
            
        Returns:
            完整的评估提示词
        """
        prompt = self.evaluation_prompt.format(resume_content=resume_content)
        
        # 添加岗位信息
        if position:
            prompt += f"\n\n目标岗位：{position}"
        
        if requirements:
            prompt += f"\n\n岗位要求：\n{requirements}"
        
        return prompt
    
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
        
        prompt = f"""
请对以下简历进行快速评分（0-100分）。

简历内容：
{resume_content}

请只返回一个0-100的数字分数，以及一句话简短评价（不超过50字）。

格式：
分数: XX
评价: XXXXX
"""
        
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
        
        prompt = f"""
请对以下简历提出具体的改进建议。

简历内容：
{resume_content}

请从以下几个方面提出建议：
1. 内容完整性（缺少哪些重要信息）
2. 表达方式（如何更好地描述经验和技能）
3. 格式排版（如何提升专业度）
4. 重点突出（如何突出核心竞争力）
5. 针对性优化（针对不同岗位如何调整）

每条建议要具体、可操作。
"""
        
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
            }
        }
