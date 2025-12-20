"""
面试 Agent 核心模块
基于 LLM 实现多轮对话模拟面试
"""

import time
from typing import List, Dict, Any, Optional

from openai import OpenAI
from loguru import logger

from config import get_llm_client, SystemConfig
from src.constants import (
    SUCCESS_INTERVIEW_STARTED,
    INFO_STARTING_INTERVIEW,
    DEFAULT_INTERVIEW_SYSTEM_PROMPT,
    INTERVIEW_TYPES,
    INFO_WEB_SEARCH_ENABLED,
)
from src.tools import WebSearchTool


class InterviewAgent:
    """
    面试 Agent
    
    功能：
    1. 多轮对话模拟面试
    2. 基于简历提问
    3. 支持联网搜索（验证回答、获取最新信息）
    4. 支持不同面试类型（技术、行为、综合）
    """
    
    def __init__(
        self,
        resume_content: Optional[str] = None,
        interview_type: str = "technical",
        max_history_turns: int = 20,
        enable_web_search: bool = True,
        custom_system_prompt: Optional[str] = None,
    ):
        """
        初始化面试 Agent
        
        Args:
            resume_content: 简历内容
            interview_type: 面试类型（technical, behavioral, comprehensive）
            max_history_turns: 最大保留历史轮数
            enable_web_search: 是否启用联网搜索
            custom_system_prompt: 自定义系统提示词
        """
        self.resume_content = resume_content
        self.interview_type = interview_type
        self.max_history_turns = max_history_turns
        self.enable_web_search = enable_web_search
        
        # 获取 LLM 客户端
        self.client, self.model, self.temperature = get_llm_client()
        
        # 对话历史
        self.chat_history: List[Dict[str, str]] = []
        
        # Web 搜索工具
        self.web_search_tool = None
        if enable_web_search:
            try:
                self.web_search_tool = WebSearchTool(
                    max_results=SystemConfig.MAX_SEARCH_RESULTS,
                    engine=SystemConfig.WEB_SEARCH_ENGINE,
                )
                logger.info(INFO_WEB_SEARCH_ENABLED)
            except Exception as e:
                logger.warning(f"Web 搜索工具初始化失败: {e}")
                self.enable_web_search = False
        
        # 系统提示词
        self.system_prompt = self._build_system_prompt(custom_system_prompt)
        
        logger.info(f"面试 Agent 已初始化 | 类型: {INTERVIEW_TYPES.get(interview_type, interview_type)}")
    
    def _build_system_prompt(self, custom_prompt: Optional[str] = None) -> str:
        """
        构建系统提示词
        
        Args:
            custom_prompt: 自定义提示词
            
        Returns:
            系统提示词
        """
        if custom_prompt:
            return custom_prompt
        
        # 生成简历摘要（用于提示词）
        resume_summary = ""
        if self.resume_content:
            # 截取前1000字符作为摘要
            resume_summary = self.resume_content[:1000]
            if len(self.resume_content) > 1000:
                resume_summary += "...\n（简历内容较长，已截取部分）"
        else:
            resume_summary = "（未提供简历）"
        
        # 获取面试类型名称
        interview_type_name = INTERVIEW_TYPES.get(self.interview_type, "面试")
        
        # 使用默认模板
        prompt = DEFAULT_INTERVIEW_SYSTEM_PROMPT.format(
            interview_type=interview_type_name,
            resume_summary=resume_summary,
        )
        
        return prompt
    
    def start_interview(self) -> Dict[str, Any]:
        """
        开始面试（生成开场白）
        
        Returns:
            开场白信息
        """
        logger.info(f"{INFO_STARTING_INTERVIEW}")
        start_time = time.time()
        
        # 构建开场白提示
        prompt = f"{self.system_prompt}\n\n请作为面试官，给出一个友好的开场白，并提出第一个问题。"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            opening = response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise
        
        # 添加到历史记录
        self.chat_history.append({
            "role": "assistant",
            "content": opening,
        })
        
        elapsed_time = time.time() - start_time
        
        logger.info(f"{SUCCESS_INTERVIEW_STARTED} | 耗时: {elapsed_time:.2f}秒")
        
        return {
            "opening": opening,
            "metadata": {
                "elapsed_time": elapsed_time,
            }
        }
    
    def chat(
        self,
        user_message: str,
        use_web_search: bool = False,
    ) -> Dict[str, Any]:
        """
        进行一轮对话
        
        Args:
            user_message: 用户消息（候选人回答）
            use_web_search: 是否使用联网搜索
            
        Returns:
            面试官回复和元数据
        """
        logger.info(f"收到候选人回答: {user_message[:50]}...")
        start_time = time.time()
        
        # 添加用户消息到历史
        self.chat_history.append({
            "role": "user",
            "content": user_message,
        })
        
        # 构建完整的对话上下文
        messages = self._build_messages()
        
        # Web 搜索（如果启用）
        web_results = []
        if use_web_search and self.enable_web_search and self.web_search_tool:
            try:
                # 提取搜索关键词（简化版，直接使用用户消息的关键部分）
                search_query = user_message[:100]
                web_results = self.web_search_tool.search(search_query, max_results=3)
                
                if web_results:
                    # 将搜索结果添加到上下文
                    web_context = "\n\n【参考资料（来自网络搜索）】\n"
                    for idx, result in enumerate(web_results, 1):
                        web_context += f"{idx}. {result['title']}\n"
                        web_context += f"   {result['snippet'][:200]}...\n"
                        web_context += f"   来源: {result['url']}\n\n"
                    
                    # 添加到最后一条消息
                    messages[-1]["content"] += web_context
                    logger.info(f"已添加 {len(web_results)} 条网络搜索结果到上下文")
            
            except Exception as e:
                logger.warning(f"Web 搜索失败: {e}")
        
        # 调用 LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )
            assistant_message = response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise
        
        # 添加助手消息到历史
        self.chat_history.append({
            "role": "assistant",
            "content": assistant_message,
        })
        
        # 管理历史记录（保持在限制内）
        self._manage_history()
        
        elapsed_time = time.time() - start_time
        
        logger.info(f"面试官回复生成完成 | 耗时: {elapsed_time:.2f}秒")
        
        return {
            "response": assistant_message,
            "web_results": web_results,
            "metadata": {
                "elapsed_time": elapsed_time,
                "history_length": len(self.chat_history),
                "used_web_search": len(web_results) > 0,
            }
        }
    
    def _build_messages(self) -> List[Dict[str, str]]:
        """
        构建消息列表（包含系统提示词和历史记录）
        
        Returns:
            消息列表
        """
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # 添加历史记录
        messages.extend(self.chat_history)
        
        return messages
    
    def _manage_history(self):
        """管理对话历史，保持在限制内"""
        # 每一轮对话包含 user 和 assistant 两条消息
        # max_history_turns 表示最多保留多少轮对话
        max_messages = self.max_history_turns * 2
        
        if len(self.chat_history) > max_messages:
            # 保留最近的消息
            self.chat_history = self.chat_history[-max_messages:]
            logger.info(f"历史记录已截断，保留最近 {self.max_history_turns} 轮对话")
    
    def clear_history(self):
        """清空对话历史"""
        self.chat_history = []
        logger.info("对话历史已清空")
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.chat_history.copy()
    
    def set_resume(self, resume_content: str):
        """
        设置或更新简历内容
        
        Args:
            resume_content: 简历内容
        """
        self.resume_content = resume_content
        # 重新构建系统提示词
        self.system_prompt = self._build_system_prompt()
        logger.info("简历内容已更新")
    
    def get_interview_summary(self) -> Dict[str, Any]:
        """
        获取面试总结
        
        Returns:
            面试总结信息
        """
        return {
            "interview_type": INTERVIEW_TYPES.get(self.interview_type, self.interview_type),
            "total_turns": len(self.chat_history) // 2,
            "history_length": len(self.chat_history),
            "has_resume": bool(self.resume_content),
            "web_search_enabled": self.enable_web_search,
        }
