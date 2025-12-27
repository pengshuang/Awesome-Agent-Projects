"""
常量定义模块

集中管理项目中使用的常量，避免魔法数字和硬编码字符串
"""

# ==================== 日志相关 ====================

# 日志分隔符
LOG_SEPARATOR_FULL = "=" * 70
LOG_SEPARATOR_HALF = "-" * 70

# ==================== 默认值 ====================

# 文本预览长度（用于日志和结果展示）
DEFAULT_PREVIEW_LENGTH = 150

# Web 搜索默认结果数
DEFAULT_WEB_SEARCH_RESULTS = 3

# 检索默认 Top-K
DEFAULT_RETRIEVAL_TOP_K = 5

# 默认相似度阈值
DEFAULT_SIMILARITY_THRESHOLD = 0.7

# ==================== 文件相关 ====================

# 索引文件名
INDEX_FILE_NAMES = ['docstore.json', 'index_store.json', 'vector_store.json']

# 支持的文档扩展名
SUPPORTED_EXTENSIONS = {
    'pdf': ['.pdf'],
    'docx': ['.docx', '.doc'],
    'markdown': ['.md', '.markdown'],
    'text': ['.txt'],
}

# ==================== 错误消息 ====================

# 文档相关错误
ERROR_NO_DOCUMENTS = "未找到任何文档！请检查目录: {}"
ERROR_FILE_NOT_FOUND = "文件不存在: {}"
ERROR_DIRECTORY_NOT_FOUND = "目录不存在: {}"
ERROR_UNSUPPORTED_FILE_TYPE = "不支持的文件格式: {}"

# 索引相关错误
ERROR_INDEX_NOT_INITIALIZED = "索引未初始化，无法创建查询引擎"
ERROR_INDEX_LOAD_FAILED = "索引加载失败: {}"
ERROR_INDEX_BUILD_FAILED = "索引构建失败: {}"

# API 相关错误
ERROR_API_KEY_NOT_SET = (
    "{} 未设置，请在 .env 文件中配置\n"
    "详细配置请参考: .env.example"
)

# 查询相关错误
ERROR_QUERY_ENGINE_NOT_READY = "查询引擎未初始化，请先加载或构建索引"
ERROR_QUERY_FAILED = "查询失败: {}"

# 向量存储相关错误
ERROR_UNSUPPORTED_VECTOR_STORE = "不支持的向量库类型: {}"

# ==================== 提示消息 ====================

# 成功消息
SUCCESS_INDEX_LOADED = "✓ 索引加载成功！耗时: {:.2f} 秒"
SUCCESS_INDEX_BUILT = "✓ 索引构建完成！总耗时: {:.2f} 秒"
SUCCESS_DOCUMENTS_LOADED = "✓ 文档加载完成"
SUCCESS_QUERY_COMPLETED = "✓ 查询完成！耗时: {:.2f} 秒"

# 警告消息
WARNING_NO_DOCUMENTS_FOUND = "⚠ 未在目录中找到任何文档: {}"
WARNING_NO_RELEVANT_DOCUMENTS = "⚠ 未找到相关文档"
WARNING_WEB_SEARCH_FAILED = "联网搜索失败: {}"
WARNING_FORCE_REBUILD = "⚠ 强制重建模式：将重新构建索引"

# 信息消息
INFO_LOADING_FROM_DISK = "从磁盘加载索引: {}"
INFO_BUILDING_NEW_INDEX = "未检测到索引，将构建新索引..."
INFO_WEB_SEARCH_ENABLED = "🌐 正在进行联网搜索..."
INFO_WEB_SEARCH_RESULTS = "✓ 找到 {} 个网络资源"

# ==================== 文本清洗相关 ====================

# 正则表达式模式
PATTERN_CONTROL_CHARS = r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]'
PATTERN_MULTIPLE_NEWLINES = r'\n{3,}'
PATTERN_MULTIPLE_SPACES = r' {2,}'
PATTERN_CHINESE_PUNCTUATION_SPACE = r'([，。！？；：])\s+'
PATTERN_ENGLISH_PUNCTUATION_SPACE = r'([,\.!?;:])\s{2,}'

# ==================== 嵌入模型相关 ====================

# 默认嵌入模型
DEFAULT_EMBEDDING_MODEL_OPENAI = "text-embedding-3-small"
DEFAULT_EMBEDDING_MODEL_HUGGINGFACE = "BAAI/bge-small-zh-v1.5"

# 嵌入批处理大小
DEFAULT_EMBED_BATCH_SIZE = 32

# ==================== LLM 相关 ====================

# 默认 LLM 模型
DEFAULT_LLM_MODEL = "gpt-3.5-turbo"

# 默认温度
DEFAULT_TEMPERATURE = 0.1

# 默认 API Base
DEFAULT_OPENAI_API_BASE = "https://api.openai.com/v1"

# ==================== 响应模式 ====================

# RAG 响应模式
RESPONSE_MODE_COMPACT = "compact"
RESPONSE_MODE_TREE_SUMMARIZE = "tree_summarize"
RESPONSE_MODE_REFINE = "refine"

# ==================== 统计相关 ====================

# 文件大小单位
FILE_SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB']

# 单位换算
BYTES_PER_KB = 1024
BYTES_PER_MB = 1024 * 1024
BYTES_PER_GB = 1024 * 1024 * 1024

__all__ = [
    # 日志相关
    'LOG_SEPARATOR_FULL',
    'LOG_SEPARATOR_HALF',
    
    # 默认值
    'DEFAULT_PREVIEW_LENGTH',
    'DEFAULT_WEB_SEARCH_RESULTS',
    'DEFAULT_RETRIEVAL_TOP_K',
    'DEFAULT_SIMILARITY_THRESHOLD',
    
    # 文件相关
    'INDEX_FILE_NAMES',
    'SUPPORTED_EXTENSIONS',
    
    # 错误消息
    'ERROR_NO_DOCUMENTS',
    'ERROR_FILE_NOT_FOUND',
    'ERROR_DIRECTORY_NOT_FOUND',
    'ERROR_UNSUPPORTED_FILE_TYPE',
    'ERROR_INDEX_NOT_INITIALIZED',
    'ERROR_INDEX_LOAD_FAILED',
    'ERROR_INDEX_BUILD_FAILED',
    'ERROR_API_KEY_NOT_SET',
    'ERROR_QUERY_ENGINE_NOT_READY',
    'ERROR_QUERY_FAILED',
    'ERROR_UNSUPPORTED_VECTOR_STORE',
    
    # 提示消息
    'SUCCESS_INDEX_LOADED',
    'SUCCESS_INDEX_BUILT',
    'SUCCESS_DOCUMENTS_LOADED',
    'SUCCESS_QUERY_COMPLETED',
    'WARNING_NO_DOCUMENTS_FOUND',
    'WARNING_NO_RELEVANT_DOCUMENTS',
    'WARNING_WEB_SEARCH_FAILED',
    'WARNING_FORCE_REBUILD',
    'INFO_LOADING_FROM_DISK',
    'INFO_BUILDING_NEW_INDEX',
    'INFO_WEB_SEARCH_ENABLED',
    'INFO_WEB_SEARCH_RESULTS',
    
    # 文本清洗相关
    'PATTERN_CONTROL_CHARS',
    'PATTERN_MULTIPLE_NEWLINES',
    'PATTERN_MULTIPLE_SPACES',
    'PATTERN_CHINESE_PUNCTUATION_SPACE',
    'PATTERN_ENGLISH_PUNCTUATION_SPACE',
    
    # 嵌入模型相关
    'DEFAULT_EMBEDDING_MODEL_OPENAI',
    'DEFAULT_EMBEDDING_MODEL_HUGGINGFACE',
    'DEFAULT_EMBED_BATCH_SIZE',
    
    # LLM 相关
    'DEFAULT_LLM_MODEL',
    'DEFAULT_TEMPERATURE',
    'DEFAULT_OPENAI_API_BASE',
    
    # 响应模式
    'RESPONSE_MODE_COMPACT',
    'RESPONSE_MODE_TREE_SUMMARIZE',
    'RESPONSE_MODE_REFINE',
    
    # 统计相关
    'FILE_SIZE_UNITS',
    'BYTES_PER_KB',
    'BYTES_PER_MB',
    'BYTES_PER_GB',
]
