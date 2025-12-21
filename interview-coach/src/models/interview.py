"""
面试会话数据模型
使用 Pydantic 进行数据验证和序列化
"""

from datetime import datetime
from typing import List, Optional, Literal
from enum import Enum

from pydantic import BaseModel, Field, field_validator, computed_field


class MessageRole(str, Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class InterviewType(str, Enum):
    """面试类型枚举"""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    COMPREHENSIVE = "comprehensive"


class InterviewMessage(BaseModel):
    """
    面试消息
    
    Attributes:
        role: 消息角色（user/assistant/system）
        content: 消息内容
        timestamp: 消息时间戳
        tokens: 消息token数（可选，用于统计）
    """
    
    role: MessageRole = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容", min_length=1)
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    tokens: Optional[int] = Field(None, description="Token数量", ge=0)
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """验证内容不为空"""
        if not v.strip():
            raise ValueError("消息内容不能为空")
        return v.strip()
    
    @computed_field
    @property
    def content_length(self) -> int:
        """内容长度"""
        return len(self.content)
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "我有3年的Python开发经验...",
                "timestamp": "2025-12-21T10:00:00",
                "tokens": 150,
            }
        }


class InterviewSession(BaseModel):
    """
    面试会话
    
    Attributes:
        interview_type: 面试类型
        resume_content: 候选人简历内容
        messages: 消息列表
        started_at: 开始时间
        ended_at: 结束时间
        enable_web_search: 是否启用联网搜索
        max_history_turns: 最大历史轮数
    """
    
    interview_type: InterviewType = Field(..., description="面试类型")
    resume_content: str = Field(..., description="简历内容", min_length=1)
    messages: List[InterviewMessage] = Field(
        default_factory=list, description="消息列表"
    )
    started_at: datetime = Field(default_factory=datetime.now, description="开始时间")
    ended_at: Optional[datetime] = Field(None, description="结束时间")
    enable_web_search: bool = Field(default=False, description="是否启用联网搜索")
    max_history_turns: int = Field(default=20, description="最大历史轮数", ge=1)
    
    def add_message(
        self, role: MessageRole, content: str, tokens: Optional[int] = None
    ) -> InterviewMessage:
        """
        添加消息
        
        Args:
            role: 消息角色
            content: 消息内容
            tokens: Token数量（可选）
            
        Returns:
            创建的消息对象
        """
        message = InterviewMessage(role=role, content=content, tokens=tokens)
        self.messages.append(message)
        return message
    
    def get_history(self, max_turns: Optional[int] = None) -> List[dict]:
        """
        获取对话历史
        
        Args:
            max_turns: 最大轮数，None表示返回所有
            
        Returns:
            对话历史列表（字典格式，适用于LLM API）
        """
        messages = self.messages
        if max_turns:
            messages = messages[-max_turns * 2 :]  # 每轮包含用户和助手消息
        
        return [{"role": msg.role.value, "content": msg.content} for msg in messages]
    
    @computed_field
    @property
    def total_turns(self) -> int:
        """总轮数（用户-助手对话对数）"""
        return sum(1 for msg in self.messages if msg.role == MessageRole.USER)
    
    @computed_field
    @property
    def duration(self) -> float:
        """面试时长（秒）"""
        end_time = self.ended_at or datetime.now()
        return (end_time - self.started_at).total_seconds()
    
    @computed_field
    @property
    def duration_minutes(self) -> float:
        """面试时长（分钟）"""
        return round(self.duration / 60, 2)
    
    @computed_field
    @property
    def total_tokens(self) -> int:
        """总Token数"""
        return sum(msg.tokens or 0 for msg in self.messages)
    
    @computed_field
    @property
    def is_active(self) -> bool:
        """会话是否仍在进行"""
        return self.ended_at is None
    
    def end_session(self) -> None:
        """结束会话"""
        if self.is_active:
            self.ended_at = datetime.now()
    
    @computed_field
    @property
    def summary(self) -> str:
        """生成会话摘要"""
        status = "进行中" if self.is_active else "已结束"
        return (
            f"面试类型: {self.interview_type.value} | "
            f"对话轮数: {self.total_turns} | "
            f"时长: {self.duration_minutes}分钟 | "
            f"状态: {status}"
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "interview_type": "technical",
                "resume_content": "个人简历内容...",
                "messages": [],
                "started_at": "2025-12-21T10:00:00",
                "enable_web_search": True,
                "max_history_turns": 20,
            }
        }
