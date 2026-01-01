"""数据模型定义"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class TaskType(str, Enum):
    """任务类型枚举"""
    IMAGE_DESCRIPTION = "图片描述类"
    IMAGE_QA = "图片问答类"
    MULTI_IMAGE_COMPARISON = "多图比较类"
    VISUAL_REASONING = "视觉推理类"
    DETAIL_RECOGNITION = "细节识别类"
    SCENE_UNDERSTANDING = "场景理解类"
    TEXT_RECOGNITION = "文字识别类"
    COUNTING = "计数统计类"
    CUSTOM = "自定义"


class ImageInfo(BaseModel):
    """图片信息"""
    path: str = Field(..., description="图片路径")
    filename: str = Field(..., description="图片文件名")
    uploaded_at: datetime = Field(default_factory=datetime.now, description="上传时间")


class QAPair(BaseModel):
    """问答对"""
    question: str = Field(..., description="问题")
    answer: str = Field(..., description="答案")
    difficulty: float = Field(..., ge=0.0, le=1.0, description="难度等级")
    iteration: int = Field(..., ge=1, description="所属迭代轮次")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ValidationResult(BaseModel):
    """验证结果"""
    is_valid: bool = Field(..., description="是否通过验证")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="语义相似度分数")
    reason: str = Field(..., description="验证理由")


class ProposerOutput(BaseModel):
    """提议者输出"""
    question: str = Field(..., description="生成的问题")
    answer: str = Field(..., description="参考答案")


class SolverOutput(BaseModel):
    """求解者输出"""
    answer: str = Field(..., description="预测答案")


class IterationState(BaseModel):
    """迭代状态"""
    iteration: int = Field(..., description="当前迭代轮次")
    difficulty: float = Field(..., description="当前难度等级")
    proposed_qa: Optional[ProposerOutput] = Field(None, description="提议的问答对")
    solved_answer: Optional[str] = Field(None, description="求解的答案")
    validation: Optional[ValidationResult] = Field(None, description="验证结果")
    status: str = Field(default="pending", description="状态：pending/proposing/solving/validating/completed/failed")
    error: Optional[str] = Field(None, description="错误信息")


class SynthesisTask(BaseModel):
    """数据合成任务"""
    task_id: str = Field(..., description="任务ID")
    task_type: str = Field(..., description="任务类型")
    task_description: Optional[str] = Field(None, description="任务描述")
    images: List[ImageInfo] = Field(..., description="图片列表")
    max_iterations: int = Field(default=10, description="最大迭代次数")
    initial_difficulty: float = Field(default=0.3, description="初始难度")
    difficulty_increment: float = Field(default=0.1, description="难度递增")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SynthesisResult(BaseModel):
    """合成结果"""
    task_id: str = Field(..., description="任务ID")
    task_type: str = Field(..., description="任务类型")
    images: List[ImageInfo] = Field(..., description="图片列表")
    qa_pairs: List[QAPair] = Field(default_factory=list, description="生成的问答对")
    iterations: List[IterationState] = Field(default_factory=list, description="迭代状态")
    total_iterations: int = Field(default=0, description="总迭代次数")
    valid_qa_count: int = Field(default=0, description="有效问答对数量")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentState(BaseModel):
    """Agent 状态（用于 LangGraph）"""
    # 任务信息
    task: SynthesisTask
    
    # 图片路径列表
    image_paths: List[str]
    
    # 历史问答对（已验证通过的）
    history_qa_pairs: List[QAPair] = Field(default_factory=list)
    
    # 当前迭代
    current_iteration: int = Field(default=0)
    
    # 当前难度
    current_difficulty: float = Field(default=0.3)
    
    # 当前迭代状态
    current_state: Optional[IterationState] = None
    
    # 所有迭代状态
    all_iterations: List[IterationState] = Field(default_factory=list)
    
    # 是否完成
    is_finished: bool = Field(default=False)
    
    # 错误信息
    error: Optional[str] = Field(None)
    
    class Config:
        arbitrary_types_allowed = True
