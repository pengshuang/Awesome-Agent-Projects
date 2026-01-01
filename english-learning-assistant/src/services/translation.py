"""翻译服务模块"""

from typing import Optional
from config.prompts import PROMPTS
from src.api.llm_client import llm_client
from src.utils.logger import app_logger


class TranslationService:
    """翻译服务"""
    
    def __init__(self):
        self.llm = llm_client
    
    def translate(self, text: str, task_type: str = "general") -> str:
        """通用翻译
        
        Args:
            text: 要翻译的文本
            task_type: 任务类型（general/word/sentence）
            
        Returns:
            翻译结果
        """
        try:
            if task_type == "word":
                return self.analyze_word(text)
            elif task_type == "sentence":
                return self.analyze_sentence(text)
            else:
                return self.translate_general(text)
        
        except Exception as e:
            app_logger.error(f"翻译失败: {str(e)}")
            return f"❌ 翻译失败: {str(e)}"
    
    def translate_general(self, text: str) -> str:
        """通用翻译（带详细解析）
        
        Args:
            text: 要翻译的文本
            
        Returns:
            翻译结果（markdown格式）
        """
        try:
            prompt = PROMPTS.TRANSLATION_PROMPT.format(text=text)
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            result = self.llm.chat_complete(messages)
            return result
        
        except Exception as e:
            app_logger.error(f"通用翻译失败: {str(e)}")
            return f"❌ 翻译失败: {str(e)}"
    
    def analyze_word(self, word: str) -> str:
        """单词深度解析
        
        Args:
            word: 要解析的单词或短语
            
        Returns:
            解析结果
        """
        try:
            prompt = PROMPTS.WORD_ANALYSIS_PROMPT.format(word=word)
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            result = self.llm.chat_complete(messages)
            return result
        
        except Exception as e:
            app_logger.error(f"单词解析失败: {str(e)}")
            return f"❌ 单词解析失败: {str(e)}"
    
    def analyze_sentence(self, sentence: str) -> str:
        """长难句解析
        
        Args:
            sentence: 要解析的句子
            
        Returns:
            解析结果
        """
        try:
            prompt = PROMPTS.SENTENCE_ANALYSIS_PROMPT.format(sentence=sentence)
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            result = self.llm.chat_complete(messages)
            return result
        
        except Exception as e:
            app_logger.error(f"句子解析失败: {str(e)}")
            return f"❌ 句子解析失败: {str(e)}"


# 全局翻译服务实例
translation_service = TranslationService()
