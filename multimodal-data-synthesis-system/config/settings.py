"""系统设置配置"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class SystemSettings(BaseModel):
    """系统设置"""
    
    # 项目根目录
    PROJECT_ROOT: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent,
        description="项目根目录"
    )
    
    # 数据目录
    DATA_DIR: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent / "data",
        description="数据目录"
    )
    
    # 上传目录
    UPLOAD_DIR: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent / "data" / "uploads",
        description="图片上传目录"
    )
    
    # 输出目录
    OUTPUT_DIR: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent / "data" / "outputs",
        description="合成数据输出目录"
    )
    
    # 日志目录
    LOG_DIR: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent / "logs",
        description="日志目录"
    )
    
    # 日志级别
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    
    # 最大迭代次数
    MAX_ITERATIONS: int = Field(default=10, description="最大迭代次数")
    
    # 温度参数（每次迭代增加的难度）
    DIFFICULTY_INCREMENT: float = Field(default=0.1, description="难度递增步长")
    
    # 初始难度
    INITIAL_DIFFICULTY: float = Field(default=0.3, description="初始难度等级（0-1）")
    
    # 最大难度
    MAX_DIFFICULTY: float = Field(default=1.0, description="最大难度等级")
    
    # 验证通过阈值
    VALIDATION_THRESHOLD: float = Field(default=0.8, description="验证通过的语义相似度阈值")
    
    def __init__(self, **data):
        super().__init__(**data)
        # 创建必要的目录
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    class Config:
        arbitrary_types_allowed = True


# 全局设置实例
settings = SystemSettings()
