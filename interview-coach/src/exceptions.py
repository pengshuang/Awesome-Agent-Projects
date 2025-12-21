"""
自定义异常模块
统一管理所有业务异常
"""


class InterviewCoachException(Exception):
    """面试辅导系统基础异常类"""
    
    def __init__(self, message: str, error_code: str = "UNKNOWN"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


# ============================================================================
# 简历加载相关异常
# ============================================================================

class ResumeLoadError(InterviewCoachException):
    """简历加载异常"""
    
    def __init__(self, message: str):
        super().__init__(message, error_code="RESUME_LOAD_ERROR")


class FileNotFoundError(ResumeLoadError):
    """文件不存在异常"""
    
    def __init__(self, file_path: str):
        super().__init__(f"文件不存在: {file_path}")
        self.file_path = file_path


class UnsupportedFileFormatError(ResumeLoadError):
    """不支持的文件格式异常"""
    
    def __init__(self, file_format: str, supported_formats: list):
        super().__init__(
            f"不支持的文件格式: {file_format}，支持的格式: {', '.join(supported_formats)}"
        )
        self.file_format = file_format
        self.supported_formats = supported_formats


class EmptyResumeError(ResumeLoadError):
    """简历内容为空异常"""
    
    def __init__(self):
        super().__init__("简历内容为空或无法解析")


# ============================================================================
# LLM 相关异常
# ============================================================================

class LLMError(InterviewCoachException):
    """LLM 调用异常"""
    
    def __init__(self, message: str):
        super().__init__(message, error_code="LLM_ERROR")


class LLMConfigError(LLMError):
    """LLM 配置异常"""
    
    def __init__(self, message: str):
        super().__init__(f"LLM 配置错误: {message}")


class LLMAPIError(LLMError):
    """LLM API 调用异常"""
    
    def __init__(self, message: str, api_error: Exception = None):
        super().__init__(f"LLM API 调用失败: {message}")
        self.api_error = api_error


# ============================================================================
# 评估相关异常
# ============================================================================

class EvaluationError(InterviewCoachException):
    """简历评估异常"""
    
    def __init__(self, message: str):
        super().__init__(message, error_code="EVALUATION_ERROR")


# ============================================================================
# 面试相关异常
# ============================================================================

class InterviewError(InterviewCoachException):
    """面试异常"""
    
    def __init__(self, message: str):
        super().__init__(message, error_code="INTERVIEW_ERROR")


class InvalidInterviewTypeError(InterviewError):
    """无效的面试类型异常"""
    
    def __init__(self, interview_type: str, valid_types: list):
        super().__init__(
            f"无效的面试类型: {interview_type}，有效类型: {', '.join(valid_types)}"
        )
        self.interview_type = interview_type
        self.valid_types = valid_types


# ============================================================================
# Web 搜索相关异常
# ============================================================================

class WebSearchError(InterviewCoachException):
    """Web 搜索异常"""
    
    def __init__(self, message: str):
        super().__init__(message, error_code="WEB_SEARCH_ERROR")
