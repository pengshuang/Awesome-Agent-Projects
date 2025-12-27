"""
评估结果数据模型
使用 Pydantic 进行数据验证和序列化
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


class ScoreDetails(BaseModel):
    """
    评分详情
    
    各维度评分范围：0-10分
    
    Attributes:
        basic_info: 基本信息完整性
        work_experience: 工作经验相关性
        project_quality: 项目经验质量
        skill_match: 技能匹配度
        education: 教育背景
        overall_impression: 整体印象
    """
    
    basic_info: float = Field(..., description="基本信息完整性", ge=0, le=10)
    work_experience: float = Field(..., description="工作经验相关性", ge=0, le=10)
    project_quality: float = Field(..., description="项目经验质量", ge=0, le=10)
    skill_match: float = Field(..., description="技能匹配度", ge=0, le=10)
    education: float = Field(..., description="教育背景", ge=0, le=10)
    overall_impression: float = Field(..., description="整体印象", ge=0, le=10)
    
    def get_total_score(self) -> float:
        """总分（满分100）"""
        return round(
            (
                self.basic_info
                + self.work_experience
                + self.project_quality
                + self.skill_match
                + self.education
                + self.overall_impression
            )
            * 10
            / 6,
            2,
        )
    
    def get_grade(self) -> str:
        """评级：优秀/良好/中等/待改进"""
        total_score = self.get_total_score()
        if total_score >= 85:
            return "优秀"
        elif total_score >= 70:
            return "良好"
        elif total_score >= 60:
            return "中等"
        else:
            return "待改进"
    
    model_config = {
        "json_schema_mode": "validation",
        "json_schema_extra": {
            "example": {
                "basic_info": 8.5,
                "work_experience": 7.0,
                "project_quality": 8.0,
                "skill_match": 7.5,
                "education": 9.0,
                "overall_impression": 8.0,
            }
        },
    }


class EvaluationResult(BaseModel):
    """
    评估结果
    
    Attributes:
        evaluation_text: 完整评估文本（Markdown格式）
        position: 目标岗位
        requirements: 岗位要求
        strengths: 优点列表
        weaknesses: 不足列表
        suggestions: 改进建议列表
        score_details: 评分详情
        model: 使用的LLM模型
        elapsed_time: 评估耗时（秒）
        evaluated_at: 评估时间戳
    """
    
    evaluation_text: str = Field(..., description="完整评估文本", min_length=1)
    position: Optional[str] = Field(None, description="目标岗位")
    requirements: Optional[str] = Field(None, description="岗位要求")
    strengths: List[str] = Field(default_factory=list, description="优点列表")
    weaknesses: List[str] = Field(default_factory=list, description="不足列表")
    suggestions: List[str] = Field(default_factory=list, description="改进建议列表")
    score_details: Optional[ScoreDetails] = Field(None, description="评分详情")
    model: str = Field(default="", description="使用的模型")
    elapsed_time: float = Field(default=0.0, description="评估耗时（秒）", ge=0)
    evaluated_at: datetime = Field(
        default_factory=datetime.now, description="评估时间"
    )
    
    @field_validator("strengths", "weaknesses", "suggestions")
    @classmethod
    def validate_lists(cls, v: List[str]) -> List[str]:
        """验证列表项不为空字符串"""
        return [item.strip() for item in v if item.strip()]
    
    def get_summary(self) -> str:
        """生成评估摘要"""
        if self.score_details:
            return f"总分: {self.score_details.get_total_score()}/100 ({self.score_details.get_grade()})"
        return "暂无评分"
    
    model_config = {
        "json_schema_mode": "validation",
        "json_schema_extra": {
            "example": {
                "evaluation_text": "## 评估结果\n...",
                "position": "Python后端工程师",
                "requirements": "3年以上经验...",
                "strengths": ["技术栈匹配", "项目经验丰富"],
                "weaknesses": ["缺少量化指标"],
                "suggestions": ["添加具体数据"],
                "model": "gpt-3.5-turbo",
                "elapsed_time": 5.23,
            }
        },
    }
