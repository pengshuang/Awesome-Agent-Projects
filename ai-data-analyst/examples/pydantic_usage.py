"""
Pydantic 模型使用示例
展示如何使用新的 Pydantic 数据验证模型
"""

from pathlib import Path
from src.models.config import SystemSettings, LLMConfig, EmbeddingConfig
from src.models.datasource import (
    SQLiteConfig,
    FileConfig,
    QueryRequest,
    QueryResponse,
)
from src.models.analysis import (
    AnalysisRequest,
    ChartConfig,
    VisualizationType,
    ChatSession,
)


def example_1_system_settings():
    """示例 1: 使用系统设置（从环境变量加载）"""
    print("=" * 60)
    print("示例 1: 系统设置")
    print("=" * 60)
    
    # 自动从 .env 文件加载配置
    settings = SystemSettings()
    
    print(f"项目根目录: {settings.project_root}")
    print(f"LLM 模型: {settings.llm_model}")
    print(f"温度: {settings.temperature}")
    print(f"Embedding 提供商: {settings.embedding_provider}")
    
    # 确保目录存在
    settings.ensure_directories()
    print("✅ 所有必要目录已创建")
    
    # 获取 LLM 配置对象
    if settings.llm_api_key:
        llm_config = settings.get_llm_config()
        print(f"\nLLM 配置: {llm_config.model_dump()}")


def example_2_llm_config_validation():
    """示例 2: LLM 配置验证"""
    print("\n" + "=" * 60)
    print("示例 2: LLM 配置验证")
    print("=" * 60)
    
    # 正确的配置
    try:
        config = LLMConfig(
            api_key="sk-test-key",
            api_base="https://api.openai.com/v1",
            model="gpt-3.5-turbo",
            temperature=0.7,
        )
        print("✅ 配置验证成功:")
        print(f"  模型: {config.model}")
        print(f"  温度: {config.temperature}")
        print(f"  API Base: {config.api_base}")
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
    
    # 错误的配置（温度超出范围）
    print("\n尝试错误配置（温度超出范围）:")
    try:
        config = LLMConfig(
            api_key="sk-test-key",
            api_base="https://api.openai.com/v1",
            model="gpt-3.5-turbo",
            temperature=3.0,  # 超出范围
        )
    except Exception as e:
        print(f"✅ 成功捕获错误: {e}")


def example_3_datasource_config():
    """示例 3: 数据源配置"""
    print("\n" + "=" * 60)
    print("示例 3: 数据源配置")
    print("=" * 60)
    
    # SQLite 配置
    try:
        # 注意：这里假设数据库文件存在
        db_path = Path("data/databases/example.db")
        if db_path.exists():
            sqlite_config = SQLiteConfig(
                name="test_db",
                db_path=db_path,
                read_only=True,
            )
            print("✅ SQLite 配置验证成功:")
            print(f"  名称: {sqlite_config.name}")
            print(f"  路径: {sqlite_config.db_path}")
            print(f"  只读: {sqlite_config.read_only}")
        else:
            print("⚠️ 数据库文件不存在，跳过 SQLite 配置示例")
    except Exception as e:
        print(f"❌ SQLite 配置验证失败: {e}")
    
    # 文件配置（自动检测格式）
    print("\n文件配置:")
    try:
        file_path = Path("data/files/example.csv")
        if file_path.exists():
            file_config = FileConfig(
                name="test_file",
                file_path=file_path,
                # file_format 会自动从扩展名检测
            )
            print("✅ 文件配置验证成功:")
            print(f"  名称: {file_config.name}")
            print(f"  路径: {file_config.file_path}")
            print(f"  格式: {file_config.file_format}")
            print(f"  编码: {file_config.encoding}")
        else:
            print("⚠️ 文件不存在，跳过文件配置示例")
    except Exception as e:
        print(f"❌ 文件配置验证失败: {e}")


def example_4_query_request_response():
    """示例 4: 查询请求和响应"""
    print("\n" + "=" * 60)
    print("示例 4: 查询请求和响应")
    print("=" * 60)
    
    # 创建查询请求
    request = QueryRequest(
        query="SELECT * FROM users WHERE age > 18",
        data_source="test_db",
        limit=10,
        user_id="user_123",
        session_id="session_456",
    )
    print("查询请求:")
    print(f"  查询: {request.query}")
    print(f"  数据源: {request.data_source}")
    print(f"  限制: {request.limit}")
    
    # 模拟查询响应
    from datetime import datetime
    from src.models.datasource import QueryMetadata
    
    response = QueryResponse(
        success=True,
        data=[
            {"id": 1, "name": "Alice", "age": 25},
            {"id": 2, "name": "Bob", "age": 30},
        ],
        metadata=QueryMetadata(
            row_count=2,
            total_rows=100,
            columns=["id", "name", "age"],
            execution_time=0.15,
            data_source_type="sqlite",
            sql_query=request.query,
        ),
        warnings=["这是一个示例警告"],
    )
    
    print("\n查询响应:")
    print(f"  成功: {response.success}")
    print(f"  返回行数: {response.metadata.row_count}")
    print(f"  总行数: {response.metadata.total_rows}")
    print(f"  执行时间: {response.metadata.execution_time}s")
    print(f"  有数据: {response.has_data()}")
    print(f"  列名: {response.get_column_names()}")


def example_5_analysis_request():
    """示例 5: 分析请求配置"""
    print("\n" + "=" * 60)
    print("示例 5: 分析请求配置")
    print("=" * 60)
    
    # 创建图表配置
    chart_config = ChartConfig(
        chart_type=VisualizationType.BAR,
        title="销售额趋势",
        x_column="month",
        y_column="sales",
        width=1000,
        height=600,
        theme="plotly_white",
    )
    
    print("图表配置:")
    print(f"  类型: {chart_config.chart_type.value}")
    print(f"  标题: {chart_config.title}")
    print(f"  X轴: {chart_config.x_column}")
    print(f"  Y轴: {chart_config.y_column}")
    
    # 创建分析请求
    analysis_request = AnalysisRequest(
        question="过去6个月的销售趋势如何？",
        data_sources=["sales_db", "customer_file"],
        analysis_type="descriptive",
        enable_visualization=True,
        chart_configs=[chart_config],
        max_charts=3,
    )
    
    print("\n分析请求:")
    print(f"  问题: {analysis_request.question}")
    print(f"  数据源: {analysis_request.data_sources}")
    print(f"  分析类型: {analysis_request.analysis_type}")
    print(f"  图表数量: {len(analysis_request.chart_configs or [])}")


def example_6_chat_session():
    """示例 6: 聊天会话管理"""
    print("\n" + "=" * 60)
    print("示例 6: 聊天会话管理")
    print("=" * 60)
    
    # 创建会话
    session = ChatSession(
        session_id="session_789",
        user_id="user_123",
        max_history=5,
    )
    
    # 添加消息
    session.add_message("user", "你好，请帮我分析销售数据")
    session.add_message("assistant", "好的，我可以帮您分析销售数据。请问您想了解哪些方面？")
    session.add_message("user", "我想看看最近三个月的销售趋势")
    
    print(f"会话 ID: {session.session_id}")
    print(f"消息数量: {len(session.messages)}")
    print(f"最大历史: {session.max_history}")
    
    print("\n消息历史:")
    for msg in session.messages:
        print(f"  [{msg.role}] {msg.content}")
    
    # 获取 LLM 格式的历史
    llm_history = session.get_history_for_llm()
    print("\nLLM 格式历史:")
    for msg in llm_history:
        print(f"  {msg}")


def example_7_model_serialization():
    """示例 7: 模型序列化"""
    print("\n" + "=" * 60)
    print("示例 7: 模型序列化")
    print("=" * 60)
    
    # 创建模型
    config = LLMConfig(
        api_key="sk-test-key",
        api_base="https://api.openai.com/v1",
        model="gpt-4",
        temperature=0.5,
    )
    
    # 转换为字典
    config_dict = config.model_dump()
    print("字典格式:")
    print(config_dict)
    
    # 转换为 JSON
    config_json = config.model_dump_json(indent=2)
    print("\nJSON 格式:")
    print(config_json)
    
    # 从字典重建
    config_restored = LLMConfig.model_validate(config_dict)
    print(f"\n从字典恢复: {config_restored.model == config.model}")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("Pydantic 模型使用示例")
    print("=" * 60)
    
    try:
        example_1_system_settings()
        example_2_llm_config_validation()
        example_3_datasource_config()
        example_4_query_request_response()
        example_5_analysis_request()
        example_6_chat_session()
        example_7_model_serialization()
        
        print("\n" + "=" * 60)
        print("✅ 所有示例运行完成")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
