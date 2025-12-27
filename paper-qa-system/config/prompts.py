"""
Prompt 配置管理模块
统一管理所有访问第三方大模型 API 的 Prompt 模板
"""

from typing import Dict


class PromptTemplates:
    """
    Prompt 模板集合
    所有访问第三方大模型 API 的 Prompt 都在这里统一管理
    """
    
    # ====================================================================
    # 系统提示词 (System Prompts)
    # ====================================================================
    
    SYSTEM_DEFAULT = """你是一位专业的学术研究助手，专门帮助用户理解和分析学术论文。
你需要：
1. 提供准确、专业的回答
2. 基于提供的文档内容进行分析
3. 如果文档中没有相关信息，请明确说明
4. 使用清晰的结构化格式组织答案
5. 必要时引用文档中的具体内容"""
    
    SYSTEM_KIMI = """你是 Kimi，由 Moonshot AI 提供的人工智能助手。
你会为用户提供安全、有帮助、准确的回答。
同时，你会拒绝一切涉及恐怖主义、种族歧视、黄色暴力等问题的回答。"""
    
    SYSTEM_KIMI_WITH_FILES = """你是 Kimi，由 Moonshot AI 提供的人工智能助手。
你会为用户提供安全、有帮助、准确的回答。
同时，你会拒绝一切涉及恐怖主义、种族歧视、黄色暴力等问题的回答。
请基于用户上传的文档内容进行分析和回答。"""
    
    # ====================================================================
    # RAG 问答相关 Prompts
    # ====================================================================
    
    RAG_QUERY_TEMPLATE = """请基于以下检索到的文档内容，回答用户的问题。

检索到的文档内容：
{context}

用户问题：{question}

要求：
1. 优先使用检索到的文档内容回答
2. 如果文档内容不足以回答问题，请明确指出
3. 保持回答的准确性和专业性
4. 使用清晰的结构组织答案
5. 适当引用文档中的关键信息"""
    
    RAG_WITH_HISTORY_TEMPLATE = """根据以下对话历史和检索到的文档内容，回答当前问题。

对话历史：
{history}

检索到的文档内容：
{context}

当前问题：{question}

要求：
1. 结合对话历史理解当前问题的上下文
2. 优先使用检索到的文档内容回答
3. 保持回答的连贯性和一致性
4. 如果问题与之前的对话相关，请结合历史信息回答"""
    
    # ====================================================================
    # 直接对话相关 Prompts
    # ====================================================================
    
    DIRECT_CHAT_TEMPLATE = """问题：{question}

请提供清晰、准确的回答。"""
    
    DIRECT_CHAT_WITH_HISTORY = """根据以下对话历史和当前问题，提供准确的回答。

对话历史：
{history}

当前问题：{question}

请基于上下文回答当前问题，如果问题与之前的对话相关，请结合历史信息回答。"""
    
    DIRECT_CHAT_WITH_CONTEXT = """补充上下文：
{context}

问题：{question}

请基于上述上下文回答问题。"""
    
    # ====================================================================
    # 网络搜索增强 Prompts
    # ====================================================================
    
    WEB_SEARCH_ENHANCED_TEMPLATE = """网络搜索结果：
{web_results}

问题：{question}

请结合网络搜索结果回答问题，确保信息的时效性和准确性。"""
    
    COMBINED_CONTEXT_TEMPLATE = """补充上下文：
{context}

{"网络搜索结果：\n" + web_results if web_results else ""}

问题：{question}

请综合以上所有信息，提供全面准确的回答。"""
    
    # ====================================================================
    # 文档分析相关 Prompts
    # ====================================================================
    
    DOCUMENT_SUMMARY = """请对以下文档进行总结：

文档内容：
{document}

要求：
1. 概括文档的主要内容和核心观点
2. 提取关键信息和重要结论
3. 保持客观性和准确性
4. 使用清晰的结构组织总结"""
    
    DOCUMENT_COMPARISON = """请比较以下几个文档的内容：

{documents}

要求：
1. 识别文档之间的相同点和不同点
2. 分析各文档的特色和优势
3. 提供综合性的对比分析
4. 使用表格或列表形式呈现对比结果"""
    
    DOCUMENT_QA = """基于以下文档内容回答问题：

文档内容：
{document}

问题：{question}

要求：
1. 从文档中找到相关信息
2. 提供准确的回答
3. 引用文档中的具体内容支持答案
4. 如果文档中没有相关信息，请明确说明"""
    
    # ====================================================================
    # 辅助功能 Prompts
    # ====================================================================
    
    QUERY_REWRITE = """请将以下用户问题改写得更清晰、更具体：

原始问题：{question}

改写要求：
1. 保持原意不变
2. 使问题更加明确和具体
3. 便于检索和理解"""
    
    EXTRACT_KEYWORDS = """请从以下问题中提取关键词：

问题：{question}

要求：
1. 提取3-5个最重要的关键词
2. 关键词应该有助于文档检索
3. 按重要性排序"""


class PromptBuilder:
    """
    Prompt 构建器
    提供便捷的方法来构建各种 Prompt
    """
    
    @staticmethod
    def build_rag_prompt(question: str, context: str, history: str = None) -> str:
        """
        构建 RAG 查询的 Prompt
        
        Args:
            question: 用户问题
            context: 检索到的文档内容
            history: 对话历史（可选）
            
        Returns:
            构建好的 Prompt
        """
        if history:
            return PromptTemplates.RAG_WITH_HISTORY_TEMPLATE.format(
                history=history,
                context=context,
                question=question
            )
        else:
            return PromptTemplates.RAG_QUERY_TEMPLATE.format(
                context=context,
                question=question
            )
    
    @staticmethod
    def build_direct_prompt(question: str, history: str = None, context: str = None) -> str:
        """
        构建直接对话的 Prompt
        
        Args:
            question: 用户问题
            history: 对话历史（可选）
            context: 补充上下文（可选）
            
        Returns:
            构建好的 Prompt
        """
        if history and context:
            prompt = f"{context}\n\n{history}\n\n当前问题: {question}"
        elif history:
            return PromptTemplates.DIRECT_CHAT_WITH_HISTORY.format(
                history=history,
                question=question
            )
        elif context:
            return PromptTemplates.DIRECT_CHAT_WITH_CONTEXT.format(
                context=context,
                question=question
            )
        else:
            return PromptTemplates.DIRECT_CHAT_TEMPLATE.format(question=question)
        
        return prompt
    
    @staticmethod
    def build_context_prompt(question: str, chat_history: list, max_turns: int = 10) -> str:
        """
        构建带历史上下文的提示词
        
        Args:
            question: 当前问题
            chat_history: 对话历史列表 [{"role": "user/assistant", "content": "..."}]
            max_turns: 最大保留轮数
            
        Returns:
            包含历史对话的增强提示词
        """
        # 获取最近的历史（按配置的最大轮数）
        recent_history = chat_history[-(max_turns * 2):]
        
        # 构建对话历史字符串
        history_text = ""
        for msg in recent_history:
            role_name = "用户" if msg["role"] == "user" else "助手"
            history_text += f"\n{role_name}: {msg['content']}"
        
        # 构建最终提示词
        return PromptTemplates.DIRECT_CHAT_WITH_HISTORY.format(
            history=history_text,
            question=question
        )
    
    @staticmethod
    def build_web_enhanced_prompt(question: str, web_results: str, context: str = None) -> str:
        """
        构建包含网络搜索结果的 Prompt
        
        Args:
            question: 用户问题
            web_results: 网络搜索结果
            context: 补充上下文（可选）
            
        Returns:
            构建好的 Prompt
        """
        if context:
            return PromptTemplates.COMBINED_CONTEXT_TEMPLATE.format(
                context=context,
                web_results=web_results,
                question=question
            )
        else:
            return PromptTemplates.WEB_SEARCH_ENHANCED_TEMPLATE.format(
                web_results=web_results,
                question=question
            )
    
    @staticmethod
    def get_system_prompt(provider: str = "default", has_files: bool = False) -> str:
        """
        获取系统提示词
        
        Args:
            provider: 模型提供商 (default, kimi, etc.)
            has_files: 是否包含文件上传
            
        Returns:
            系统提示词
        """
        if provider.lower() == "kimi" or "moonshot" in provider.lower():
            if has_files:
                return PromptTemplates.SYSTEM_KIMI_WITH_FILES
            else:
                return PromptTemplates.SYSTEM_KIMI
        else:
            return PromptTemplates.SYSTEM_DEFAULT


# 方便直接导入使用
def get_system_prompt(provider: str = "default", has_files: bool = False) -> str:
    """获取系统提示词的便捷函数"""
    return PromptBuilder.get_system_prompt(provider, has_files)


def build_rag_prompt(question: str, context: str, history: str = None) -> str:
    """构建 RAG Prompt 的便捷函数"""
    return PromptBuilder.build_rag_prompt(question, context, history)


def build_direct_prompt(question: str, history: str = None, context: str = None) -> str:
    """构建直接对话 Prompt 的便捷函数"""
    return PromptBuilder.build_direct_prompt(question, history, context)
