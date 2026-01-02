"""
对话管理模块
负责对话历史管理和场景检测
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class ConversationManager:
    """对话历史管理器"""
    
    # 场景关键词映射
    SCENARIO_KEYWORDS = {
        "亲子游": ["亲子", "孩子", "小孩", "儿童", "宝宝", "带娃"],
        "老年游": ["老人", "父母", "长辈", "爸妈", "老年"],
        "学生穷游": ["学生", "穷游", "预算少", "省钱", "便宜"],
        "情侣游": ["情侣", "蜜月", "浪漫", "两个人"],
        "轻奢游": ["轻奢", "高端", "奢华", "五星", "品质"],
        "境外游": ["国外", "出国", "境外", "国际"]
    }
    
    def __init__(self):
        """初始化对话管理器"""
        self.history: List[Dict[str, str]] = []
        self.current_scenario: Optional[str] = None
        self.user_requirements: Dict[str, any] = {}
        
        logger.info("💬 对话管理器初始化完成")
    
    def add_message(self, role: str, content: str) -> None:
        """
        添加消息到历史
        
        Args:
            role: 角色（user/assistant）
            content: 消息内容
        """
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        logger.debug(f"📝 添加消息 | 角色: {role} | 长度: {len(content)}")
    
    def get_context(self, last_n: int = 5) -> str:
        """
        获取最近 N 轮对话上下文
        
        Args:
            last_n: 获取最近几轮对话
        
        Returns:
            格式化的对话上下文
        """
        recent = (
            self.history[-last_n*2:] 
            if len(self.history) > last_n*2 
            else self.history
        )
        
        context = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in recent
        ])
        
        return context
    
    def clear(self) -> None:
        """清空历史"""
        self.history = []
        self.current_scenario = None
        self.user_requirements = {}
        
        logger.info("🗑️  对话历史已清空")
    
    def detect_scenario(self, user_input: str) -> Optional[str]:
        """
        检测用户需求场景
        
        Args:
            user_input: 用户输入文本
        
        Returns:
            检测到的场景名称，如果没有检测到返回 None
        """
        for scenario, keywords in self.SCENARIO_KEYWORDS.items():
            if any(keyword in user_input for keyword in keywords):
                self.current_scenario = scenario
                logger.info(f"🎯 检测到场景: {scenario}")
                return scenario
        
        return None
    
    def get_history_count(self) -> int:
        """获取历史消息数量"""
        return len(self.history)
    
    def get_last_user_message(self) -> Optional[str]:
        """获取最后一条用户消息"""
        for msg in reversed(self.history):
            if msg["role"] == "user":
                return msg["content"]
        return None
    
    def get_last_assistant_message(self) -> Optional[str]:
        """获取最后一条助手消息"""
        for msg in reversed(self.history):
            if msg["role"] == "assistant":
                return msg["content"]
        return None
