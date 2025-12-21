"""
数据分析相关的 Pydantic 模型
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class VisualizationType(str, Enum):
    """可视化图表类型"""
    
    BAR = "bar"  # 柱状图
    LINE = "line"  # 折线图
    PIE = "pie"  # 饼图
    SCATTER = "scatter"  # 散点图
    HISTOGRAM = "histogram"  # 直方图
    BOX = "box"  # 箱线图
    HEATMAP = "heatmap"  # 热力图
    TABLE = "table"  # 表格
    FUNNEL = "funnel"  # 漏斗图
    GAUGE = "gauge"  # 仪表盘
    TREEMAP = "treemap"  # 树状图


class ChartConfig(BaseModel):
    """图表配置模型"""
    
    chart_type: VisualizationType = Field(..., description="图表类型")
    title: str = Field(..., min_length=1, description="图表标题")
    
    # 数据映射
    x_column: Optional[str] = Field(default=None, description="X 轴列名")
    y_column: Optional[str] = Field(default=None, description="Y 轴列名")
    color_column: Optional[str] = Field(default=None, description="颜色分组列")
    size_column: Optional[str] = Field(default=None, description="大小列（用于散点图）")
    
    # 样式配置
    width: int = Field(default=800, gt=0, description="图表宽度")
    height: int = Field(default=600, gt=0, description="图表高度")
    theme: Literal["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"] = Field(
        default="plotly",
        description="图表主题"
    )
    
    # 标签配置
    x_label: Optional[str] = Field(default=None, description="X 轴标签")
    y_label: Optional[str] = Field(default=None, description="Y 轴标签")
    show_legend: bool = Field(default=True, description="是否显示图例")
    
    # 数据配置
    sort_by: Optional[str] = Field(default=None, description="排序列")
    sort_ascending: bool = Field(default=True, description="是否升序")
    top_n: Optional[int] = Field(default=None, gt=0, description="只显示前 N 个")
    
    @field_validator("x_column", "y_column")
    @classmethod
    def validate_required_columns(cls, v: Optional[str], info) -> Optional[str]:
        """验证必需的列"""
        chart_type = info.data.get("chart_type")
        field_name = info.field_name
        
        # 某些图表类型需要特定的列
        if chart_type in [VisualizationType.BAR, VisualizationType.LINE, VisualizationType.SCATTER]:
            if field_name in ["x_column", "y_column"] and not v:
                raise ValueError(f"{chart_type.value} 图表需要指定 {field_name}")
        
        return v


class AnalysisRequest(BaseModel):
    """数据分析请求模型"""
    
    question: str = Field(..., min_length=1, description="分析问题")
    data_sources: List[str] = Field(
        ...,
        min_length=1,
        description="数据源名称列表"
    )
    
    # 分析类型
    analysis_type: Literal[
        "descriptive",  # 描述性分析
        "diagnostic",  # 诊断性分析
        "predictive",  # 预测性分析
        "prescriptive",  # 规范性分析
    ] = Field(default="descriptive", description="分析类型")
    
    # 分析选项
    enable_visualization: bool = Field(default=True, description="是否生成可视化")
    enable_summary: bool = Field(default=True, description="是否生成摘要")
    enable_insights: bool = Field(default=True, description="是否生成洞察")
    
    # 可视化配置
    chart_configs: Optional[List[ChartConfig]] = Field(
        default=None,
        description="指定的图表配置列表"
    )
    auto_chart: bool = Field(default=True, description="自动选择合适的图表")
    max_charts: int = Field(default=3, ge=1, le=10, description="最大图表数量")
    
    # 上下文
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="额外的上下文信息"
    )
    user_id: Optional[str] = Field(default=None, description="用户ID")
    session_id: Optional[str] = Field(default=None, description="会话ID")
    
    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """验证问题不为空"""
        if not v.strip():
            raise ValueError("分析问题不能为空")
        return v.strip()


class InsightItem(BaseModel):
    """洞察项"""
    
    title: str = Field(..., description="洞察标题")
    description: str = Field(..., description="洞察描述")
    insight_type: Literal["trend", "anomaly", "correlation", "pattern", "recommendation"] = Field(
        ...,
        description="洞察类型"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="置信度"
    )
    importance: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="重要程度"
    )
    supporting_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="支持数据"
    )


class ChartData(BaseModel):
    """图表数据"""
    
    chart_id: str = Field(..., description="图表唯一标识")
    config: ChartConfig = Field(..., description="图表配置")
    data: List[Dict[str, Any]] = Field(..., description="图表数据")
    plotly_json: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Plotly JSON 格式"
    )
    image_base64: Optional[str] = Field(
        default=None,
        description="图表 Base64 编码图片"
    )


class AnalysisResponse(BaseModel):
    """数据分析响应模型"""
    
    success: bool = Field(..., description="是否成功")
    question: str = Field(..., description="原始问题")
    
    # 分析结果
    summary: Optional[str] = Field(default=None, description="分析摘要")
    insights: List[InsightItem] = Field(default_factory=list, description="洞察列表")
    charts: List[ChartData] = Field(default_factory=list, description="图表列表")
    
    # 数据查询结果
    query_results: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="查询结果数据"
    )
    
    # 错误和警告
    error: Optional[str] = Field(default=None, description="错误信息")
    warnings: List[str] = Field(default_factory=list, description="警告信息")
    
    # 元数据
    execution_time: float = Field(ge=0, description="执行时间（秒）")
    data_sources_used: List[str] = Field(
        default_factory=list,
        description="使用的数据源"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="分析时间戳"
    )
    
    # 分析过程追踪（用于调试）
    reasoning_steps: Optional[List[str]] = Field(
        default=None,
        description="推理步骤"
    )
    
    @field_validator("error")
    @classmethod
    def validate_error(cls, v: Optional[str], info) -> Optional[str]:
        """验证失败时必须有错误信息"""
        if not info.data.get("success") and not v:
            raise ValueError("分析失败时必须提供错误信息")
        return v
    
    def has_insights(self) -> bool:
        """检查是否有洞察"""
        return len(self.insights) > 0
    
    def has_charts(self) -> bool:
        """检查是否有图表"""
        return len(self.charts) > 0
    
    def get_high_priority_insights(self) -> List[InsightItem]:
        """获取高优先级洞察"""
        return [insight for insight in self.insights if insight.importance == "high"]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()


class ChatMessage(BaseModel):
    """聊天消息模型"""
    
    role: Literal["user", "assistant", "system"] = Field(..., description="角色")
    content: str = Field(..., min_length=1, description="消息内容")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="消息时间戳"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="消息元数据"
    )


class ChatSession(BaseModel):
    """聊天会话模型"""
    
    session_id: str = Field(..., description="会话ID")
    user_id: Optional[str] = Field(default=None, description="用户ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="消息历史")
    max_history: int = Field(default=10, ge=1, description="最大历史记录数")
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="更新时间"
    )
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """添加消息"""
        message = ChatMessage(role=role, content=content, metadata=metadata)
        self.messages.append(message)
        
        # 限制历史记录数量
        if len(self.messages) > self.max_history * 2:  # 用户和助手各算一条
            self.messages = self.messages[-(self.max_history * 2):]
        
        self.updated_at = datetime.now()
    
    def get_history_for_llm(self) -> List[Dict[str, str]]:
        """获取用于 LLM 的历史记录格式"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]
    
    def clear_history(self) -> None:
        """清空历史记录"""
        self.messages = []
        self.updated_at = datetime.now()
