"""
Prompt 配置管理模块
统一管理所有访问第三方大模型 API 的 Prompt 模板
"""

from typing import Dict, Optional


class PromptTemplates:
    """
    Prompt 模板集合
    所有访问第三方大模型 API 的 Prompt 都在这里统一管理
    """
    
    # ====================================================================
    # 系统提示词 (System Prompts)
    # ====================================================================
    
    SYSTEM_DEFAULT = """你是一位专业的数据分析助手，擅长从多种数据源获取数据并进行深入分析。
你的能力包括：
1. 连接和查询业务数据库（SQLite等）
2. 读取和分析本地文件（CSV、Excel、JSON等）
3. 从知识库中检索相关信息
4. 通过网络搜索获取最新数据
5. 将自然语言转换为SQL查询（NL2SQL）
6. 融合多个数据源进行综合分析
7. 生成专业的数据分析报告
8. 提供基于数据的决策建议

要求：
- 保持回答的准确性和专业性
- 使用清晰的结构组织答案
- 必要时提供数据可视化建议
- 明确标注数据来源
- 如果数据不足，请明确说明"""
    
    # ====================================================================
    # NL2SQL 相关 Prompts
    # ====================================================================
    
    NL2SQL_TEMPLATE = """你是一位SQL专家，请将用户的自然语言问题转换为SQL查询语句。

数据库信息：
{database_schema}

用户问题：{question}

要求：
1. 只返回**一条**SQL查询语句，不要有其他解释
2. 不要使用分号结尾
3. 不要生成多条SQL语句
4. SQL语句必须符合 {dialect} 语法
5. 使用表和列的正确名称
6. 如果需要JOIN，请使用正确的JOIN条件
7. 对于复杂查询，使用子查询或CTE
8. 考虑数据类型和约束条件

SQL查询："""
    
    NL2SQL_WITH_CONTEXT = """你是一位SQL专家，请基于对话上下文将用户的问题转换为SQL查询语句。

数据库信息：
{database_schema}

对话历史：
{chat_history}

当前问题：{question}

要求：
1. 结合对话历史理解当前问题的上下文
2. 只返回**一条**SQL查询语句，不要有其他解释
3. 不要使用分号结尾
4. 不要生成多条SQL语句
5. SQL语句必须符合 {dialect} 语法
6. 如果问题涉及之前的查询结果，请适当调整SQL

SQL查询："""
    
    SQL_CORRECTION = """请检查并修正以下SQL语句的语法错误。

原始SQL：
{sql}

错误信息：
{error}

数据库信息：
{database_schema}

要求：
1. 修正语法错误
2. 保持原有查询意图
3. 只返回修正后的SQL语句

修正后的SQL："""
    
    # ====================================================================
    # 数据分析相关 Prompts
    # ====================================================================
    
    DATA_ANALYSIS_TEMPLATE = """请基于以下数据进行分析，并回答用户的问题。

数据来源：{data_source}

数据内容：
{data_content}

用户问题：{question}

要求：
1. 提供清晰的数据分析结果
2. 使用Markdown格式组织答案
3. 必要时使用表格展示数据
4. 提炼关键洞察和发现
5. 给出基于数据的结论"""
    
    MULTI_SOURCE_ANALYSIS = """请融合多个数据源的信息进行综合分析。

数据源1（{source1_name}）：
{source1_data}

数据源2（{source2_name}）：
{source2_data}

{additional_sources}

用户问题：{question}

要求：
1. 综合分析多个数据源的信息
2. 发现数据间的关联和矛盾
3. 提供全面的分析结论
4. 明确标注每个结论的数据来源
5. 使用Markdown格式，结构清晰"""
    
    REPORT_GENERATION = """请基于以下分析结果生成专业的数据分析报告。

分析内容：
{analysis_content}

用户需求：{question}

要求：
1. 使用专业的报告格式
2. 包含：摘要、详细分析、结论、建议
3. 使用Markdown格式
4. 适当使用图表说明（描述性）
5. 语言简洁专业"""
    
    DECISION_SUPPORT = """请基于以下数据和分析，提供决策建议。

数据分析：
{analysis}

业务背景：{context}

决策问题：{question}

要求：
1. 提供明确的决策建议
2. 列出支持该建议的关键数据
3. 分析潜在风险和机会
4. 给出可执行的行动计划
5. 使用Markdown格式组织"""
    
    # ====================================================================
    # 知识库检索相关 Prompts
    # ====================================================================
    
    KNOWLEDGE_BASE_QUERY = """请基于知识库中检索到的信息回答用户问题。

检索到的知识：
{retrieved_knowledge}

用户问题：{question}

要求：
1. 优先使用检索到的知识回答
2. 如果知识不足，请明确指出
3. 提供准确的引用来源
4. 使用Markdown格式"""
    
    # ====================================================================
    # Web搜索增强 Prompts
    # ====================================================================
    
    WEB_SEARCH_ENHANCED = """请结合网络搜索结果和其他数据源，回答用户问题。

网络搜索结果：
{web_results}

其他数据：
{other_data}

用户问题：{question}

要求：
1. 综合多个信息源
2. 标注信息来源
3. 区分实时数据和历史数据
4. 使用Markdown格式"""
    
    # ====================================================================
    # 对话历史相关 Prompts
    # ====================================================================
    
    CHAT_WITH_HISTORY = """根据对话历史和当前问题，继续对话。

对话历史：
{chat_history}

当前数据/上下文：
{context}

当前问题：{question}

要求：
1. 结合对话历史理解当前问题
2. 保持对话的连贯性
3. 如果需要补充信息，主动询问
4. 使用Markdown格式"""


class PromptBuilder:
    """Prompt 构建器，用于动态生成 Prompt"""
    
    @staticmethod
    def build_nl2sql_prompt(
        question: str,
        database_schema: str,
        dialect: str = "sqlite",
        chat_history: Optional[str] = None,
    ) -> str:
        """构建 NL2SQL Prompt"""
        if chat_history:
            return PromptTemplates.NL2SQL_WITH_CONTEXT.format(
                database_schema=database_schema,
                chat_history=chat_history,
                question=question,
                dialect=dialect,
            )
        else:
            return PromptTemplates.NL2SQL_TEMPLATE.format(
                database_schema=database_schema,
                question=question,
                dialect=dialect,
            )
    
    @staticmethod
    def build_data_analysis_prompt(
        question: str,
        data_source: str,
        data_content: str,
    ) -> str:
        """构建数据分析 Prompt"""
        return PromptTemplates.DATA_ANALYSIS_TEMPLATE.format(
            data_source=data_source,
            data_content=data_content,
            question=question,
        )
    
    @staticmethod
    def build_multi_source_prompt(
        question: str,
        sources: Dict[str, str],
    ) -> str:
        """构建多数据源分析 Prompt"""
        source_names = list(sources.keys())
        
        # 处理额外的数据源
        additional = ""
        if len(sources) > 2:
            for i, (name, data) in enumerate(list(sources.items())[2:], start=3):
                additional += f"\n数据源{i}（{name}）：\n{data}\n"
        
        return PromptTemplates.MULTI_SOURCE_ANALYSIS.format(
            source1_name=source_names[0] if len(source_names) > 0 else "",
            source1_data=sources[source_names[0]] if len(source_names) > 0 else "",
            source2_name=source_names[1] if len(source_names) > 1 else "",
            source2_data=sources[source_names[1]] if len(source_names) > 1 else "",
            additional_sources=additional,
            question=question,
        )
    
    @staticmethod
    def format_chat_history(history: list) -> str:
        """格式化对话历史"""
        formatted = []
        for msg in history:
            role = "用户" if msg["role"] == "user" else "助手"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)
