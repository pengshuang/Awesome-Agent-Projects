"""
Pydantic 配置使用示例

展示如何使用新的 Pydantic 配置系统
"""

from config.models import get_config, reload_config, AppConfig
from config import SystemConfig  # 向后兼容的访问方式


def example_1_basic_usage():
    """示例 1: 基本用法 - 获取配置"""
    print("=" * 60)
    print("示例 1: 基本用法")
    print("=" * 60)
    
    # 获取全局配置实例（单例模式）
    config = get_config()
    
    # 访问各个配置模块
    print(f"LLM 模型: {config.llm.model}")
    print(f"LLM API Base: {config.llm.api_base}")
    print(f"LLM 温度: {config.llm.temperature}")
    print()
    
    print(f"Embedding 提供商: {config.embedding.provider}")
    print(f"Embedding 模型: {config.embedding.model_name}")
    print()
    
    print(f"Chunk Size: {config.rag.chunk_size}")
    print(f"Chunk Overlap: {config.rag.chunk_overlap}")
    print(f"Top-K: {config.rag.retrieval_top_k}")
    print()
    
    print(f"向量存储类型: {config.vector_store.store}")
    print(f"Chroma 集合名: {config.vector_store.chroma_collection_name}")
    print()


def example_2_path_access():
    """示例 2: 路径访问"""
    print("=" * 60)
    print("示例 2: 路径访问")
    print("=" * 60)
    
    config = get_config()
    
    # 访问系统路径
    print(f"项目根目录: {config.system.base_dir}")
    print(f"数据目录: {config.system.data_dir}")
    print(f"文档目录: {config.system.documents_dir}")
    print(f"向量存储目录: {config.system.vector_store_dir}")
    print(f"日志目录: {config.system.logs_dir}")
    print()


def example_3_validation():
    """示例 3: 数据验证"""
    print("=" * 60)
    print("示例 3: 数据验证示例")
    print("=" * 60)
    
    from pydantic import ValidationError
    from config.models import RAGConfig
    
    # 正确的配置
    try:
        valid_config = RAGConfig(
            chunk_size=512,
            chunk_overlap=50,
            retrieval_top_k=5,
        )
        print(f"✅ 有效配置: chunk_size={valid_config.chunk_size}")
    except ValidationError as e:
        print(f"❌ 验证失败: {e}")
    
    # 错误的配置（chunk_overlap >= chunk_size）
    try:
        invalid_config = RAGConfig(
            chunk_size=512,
            chunk_overlap=512,  # 不能 >= chunk_size
        )
    except ValidationError as e:
        print(f"❌ 预期的验证错误: chunk_overlap 必须小于 chunk_size")
        print(f"   错误详情: {e.errors()[0]['msg']}")
    
    print()


def example_4_backward_compatibility():
    """示例 4: 向后兼容性"""
    print("=" * 60)
    print("示例 4: 向后兼容性")
    print("=" * 60)
    
    # 旧的访问方式仍然有效（通过 SystemConfig 包装器）
    print(f"文档目录 (旧方式): {SystemConfig.DOCUMENTS_DIR}")
    print(f"Chunk Size (旧方式): {SystemConfig.CHUNK_SIZE}")
    print(f"Top-K (旧方式): {SystemConfig.RETRIEVAL_TOP_K}")
    print()
    
    # 新的访问方式（推荐）
    config = get_config()
    print(f"文档目录 (新方式): {config.system.documents_dir}")
    print(f"Chunk Size (新方式): {config.rag.chunk_size}")
    print(f"Top-K (新方式): {config.rag.retrieval_top_k}")
    print()


def example_5_custom_config():
    """示例 5: 自定义配置"""
    print("=" * 60)
    print("示例 5: 自定义配置实例")
    print("=" * 60)
    
    from config.models import LLMConfig, EmbeddingConfig
    
    # 创建自定义 LLM 配置
    custom_llm = LLMConfig(
        api_key="custom-api-key",
        api_base="https://api.custom.com/v1",
        model="custom-model",
        temperature=0.5,
        max_tokens=2000,
    )
    
    print(f"自定义 LLM 模型: {custom_llm.model}")
    print(f"自定义 LLM 温度: {custom_llm.temperature}")
    print()
    
    # 创建自定义 Embedding 配置
    custom_embedding = EmbeddingConfig(
        provider="huggingface",
        model_name="BAAI/bge-large-zh-v1.5",
        batch_size=20,
    )
    
    print(f"自定义 Embedding 模型: {custom_embedding.model_name}")
    print(f"自定义批处理大小: {custom_embedding.batch_size}")
    print()


def example_6_type_safety():
    """示例 6: 类型安全"""
    print("=" * 60)
    print("示例 6: 类型安全和自动补全")
    print("=" * 60)
    
    config = get_config()
    
    # IDE 会提供自动补全和类型检查
    # config.llm.          # 自动显示所有 LLM 配置选项
    # config.rag.          # 自动显示所有 RAG 配置选项
    # config.embedding.    # 自动显示所有 Embedding 配置选项
    
    # 类型注解清晰
    model_name: str = config.llm.model
    temperature: float = config.llm.temperature
    top_k: int = config.rag.retrieval_top_k
    
    print(f"模型名称 (str): {model_name}")
    print(f"温度 (float): {temperature}")
    print(f"Top-K (int): {top_k}")
    print()


def example_7_web_search_config():
    """示例 7: Web 搜索配置"""
    print("=" * 60)
    print("示例 7: Web 搜索配置")
    print("=" * 60)
    
    config = get_config()
    
    print(f"启用 Web 搜索: {config.web_search.enable_web_search}")
    print(f"搜索引擎: {config.web_search.search_engine}")
    print(f"最大结果数: {config.web_search.max_results}")
    print(f"SearXNG URL: {config.web_search.searxng_url}")
    print()


def example_8_reload_config():
    """示例 8: 重新加载配置"""
    print("=" * 60)
    print("示例 8: 重新加载配置")
    print("=" * 60)
    
    # 获取当前配置
    config1 = get_config()
    print(f"初始 LLM 模型: {config1.llm.model}")
    
    # 如果环境变量发生变化，可以重新加载配置
    # 注意：这会创建一个新的配置实例
    config2 = reload_config()
    print(f"重新加载后的 LLM 模型: {config2.llm.model}")
    
    # 再次调用 get_config() 会返回新的配置实例
    config3 = get_config()
    print(f"Get_config 返回的 LLM 模型: {config3.llm.model}")
    print()


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("Pydantic 配置系统使用示例")
    print("=" * 60 + "\n")
    
    try:
        example_1_basic_usage()
        example_2_path_access()
        example_3_validation()
        example_4_backward_compatibility()
        example_5_custom_config()
        example_6_type_safety()
        example_7_web_search_config()
        example_8_reload_config()
        
        print("=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
