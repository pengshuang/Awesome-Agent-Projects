#!/usr/bin/env python3
"""
Academic Paper Q&A System - 简单可用版本
使用最基础的 Gradio Interface，保证可用性
"""

import os
import gradio as gr
from pathlib import Path
from collections import defaultdict

# 导入项目模块
from src.agent import create_agent
from src.loaders.document_loader import DocumentLoader
from init_system import initialize_system

# 全局状态
AGENT = None
INDEX_BUILT = False
INITIALIZED = False
INDEX_PATH = "./data/index"
VECTOR_STORE_PATH = "./data/vector_store"  # 实际的向量存储路径
DOCUMENTS_PATH = "./data/documents"

DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", "1024"))
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "3"))


def check_existing_index() -> str:
    """启动时检查是否存在已构建的索引"""
    global AGENT, INDEX_BUILT, INITIALIZED
    
    # 检查向量存储目录
    vector_store_dir = Path(VECTOR_STORE_PATH)
    
    # 检查是否存在向量存储文件（排除 .gitkeep）
    has_vector_store = False
    if vector_store_dir.exists():
        # 获取所有文件（排除 .gitkeep 和隐藏文件）
        vector_files = [f for f in vector_store_dir.glob("*") 
                       if f.is_file() and f.name != '.gitkeep' and not f.name.startswith('.')]
        has_vector_store = len(vector_files) > 0
    
    if not has_vector_store:
        return "ℹ️ 未发现已有索引\n💡 系统将在首次查询时自动构建索引，或前往「构建索引」标签页手动构建"
    
    try:
        if not INITIALIZED:
            initialize_system()
            INITIALIZED = True
        
        # 尝试加载已有索引
        AGENT = create_agent(
            documents_dir=DOCUMENTS_PATH,
            force_rebuild=False  # 不强制重建
        )
        INDEX_BUILT = True
        
        # 获取文档统计信息
        try:
            papers = AGENT.list_papers(detailed=False)
            doc_count = len(papers)
            return f"""✅ 已自动加载现有索引！

📊 索引信息:
- 向量存储: {VECTOR_STORE_PATH}
- 已索引文档: {doc_count} 个
- 状态: 可直接使用

💡 提示:
- RAG 模式已就绪，可直接开始提问
- 如需重新构建索引，请前往「构建索引」标签页
"""
        except:
            return f"""✅ 已自动加载现有索引！

📊 索引信息:
- 向量存储: {VECTOR_STORE_PATH}
- 状态: 可直接使用

💡 提示:
- RAG 模式已就绪，可直接开始提问
- 如需重新构建索引，请前往「构建索引」标签页
"""
        
    except Exception as e:
        return f"""⚠️ 索引加载失败: {str(e)}

💡 建议:
1. 前往「构建索引」标签页重新构建
2. 检查文档目录是否存在: {DOCUMENTS_PATH}
3. 查看系统日志获取详细错误信息
"""


def build_index(input_dir: str, force_rebuild: bool = True) -> str:
    """构建索引 - 返回字符串状态"""
    global AGENT, INDEX_BUILT, INITIALIZED
    
    try:
        if not INITIALIZED:
            initialize_system()
            INITIALIZED = True
        
        loader = DocumentLoader(
            input_dir=input_dir,
            recursive=True,
            clean_text=True,
            preserve_formatting=True
        )
        
        documents = loader.load_documents()
        
        if not documents:
            return f"❌ 未找到文档，请检查路径: {input_dir}"
        
        # 统计每个文件的文档数量
        file_doc_count = defaultdict(int)
        for doc in documents:
            file_name = doc.metadata.get('file_name', '未知文件')
            file_doc_count[file_name] += 1
        
        # 创建 agent 并构建索引（可能耗时较长）
        try:
            AGENT = create_agent(
                documents_dir=input_dir,
                force_rebuild=force_rebuild
            )
        except BrokenPipeError:
            return """❌ 构建索引失败: 连接中断 (Broken pipe)

🔧 可能原因:
1. 浏览器页面已关闭或刷新
2. 构建时间过长导致连接超时
3. 网络连接不稳定

💡 解决方案:
1. 保持浏览器页面打开
2. 检查网络连接
3. 如果文档很多，请耐心等待（不要刷新页面）
4. 尝试减少文档数量后重试
5. 或使用命令行工具: python main.py build

ℹ️ 提示: 索引可能已部分构建，下次构建时可以不勾选"强制重建"以继续
"""
        except Exception as build_error:
            return f"""❌ 构建索引过程出错: {str(build_error)}

💡 建议:
1. 检查文档格式是否正确
2. 确保有足够的磁盘空间
3. 查看系统日志: logs/app.log
4. 尝试使用命令行: python main.py build
"""
        
        INDEX_BUILT = True
        
        # 构建详细的统计信息
        result = f"""✅ 索引构建成功！

📊 总体统计:
- 总文档数量: {len(documents)} 个文本块
- 源文件数量: {len(file_doc_count)} 个
- 文档路径: {input_dir}

📄 各文件详情:
"""
        # 按文档数量排序显示
        for file_name, count in sorted(file_doc_count.items(), key=lambda x: x[1], reverse=True):
            result += f"  • {file_name}: {count} 个文本块\n"
        
        result += "\n💡 现在可以在「问答」标签页开始提问了！"
        
        return result
        
    except KeyboardInterrupt:
        return """⚠️ 构建已取消

用户主动中断了构建过程。
"""
    except Exception as e:
        error_msg = str(e)
        
        # 特殊错误处理
        if "Broken pipe" in error_msg or "BrokenPipeError" in error_msg:
            return """❌ 构建索引失败: 连接中断

🔧 可能原因:
1. 浏览器页面关闭或刷新
2. 网络连接中断
3. 构建时间过长

💡 解决方案:
1. 保持页面打开，不要刷新
2. 使用命令行构建: python main.py build
3. 检查网络连接
"""
        elif "Permission denied" in error_msg:
            return f"""❌ 构建索引失败: 权限不足

错误: {error_msg}

💡 解决方案:
1. 检查文档目录的读取权限
2. 检查索引目录的写入权限
3. 尝试使用管理员权限运行
"""
        elif "No space left" in error_msg:
            return """❌ 构建索引失败: 磁盘空间不足

💡 解决方案:
1. 清理磁盘空间
2. 减少文档数量
3. 更改索引存储位置
"""
        else:
            return f"""❌ 构建索引失败: {error_msg}

💡 建议:
1. 检查文档路径是否正确: {input_dir}
2. 确认文档格式支持 (PDF, DOCX, TXT, MD)
3. 查看详细日志: logs/app.log
4. 尝试使用命令行: python main.py build
"""


def get_available_documents():
    """获取可用文档列表"""
    global AGENT, INITIALIZED
    
    try:
        # 确保有 agent 实例（即使没有构建索引也可以列出文档）
        if not INITIALIZED:
            initialize_system()
            INITIALIZED = True
        
        if AGENT is None:
            from src.agent import AcademicAgent
            AGENT = AcademicAgent(documents_dir=DOCUMENTS_PATH, auto_load=False)
        
        return AGENT.list_available_documents()
    except Exception as e:
        print(f"获取文档列表失败: {e}")
        return []


def query_question(question: str, mode: str, enable_web_search: bool, top_k: int, selected_docs: list) -> str:
    """
    查询问题 - 支持 RAG 和 LLM 两种模式
    
    Args:
        question: 用户问题
        mode: 查询模式（"RAG 模式" 或 "LLM 模式"）
        enable_web_search: 是否启用联网搜索
        top_k: 检索文档数量（仅 RAG 模式）
        selected_docs: 选中的文档列表（仅 LLM 模式使用）
    """
    global AGENT, INDEX_BUILT, INITIALIZED
    
    if not question or not question.strip():
        return "⚠️ 请输入问题"
    
    # LLM 模式不需要索引
    if mode == "LLM 模式":
        try:
            # 初始化系统
            if not INITIALIZED:
                initialize_system()
                INITIALIZED = True
            
            # 确保 AGENT 存在（即使没有索引）
            if AGENT is None:
                from src.agent import AcademicAgent
                AGENT = AcademicAgent(documents_dir=DOCUMENTS_PATH, auto_load=False)
            
            # 使用 query_direct 方法（支持文档附件）
            result = AGENT.query_direct(
                question=question,
                enable_web_search=enable_web_search,
                document_files=selected_docs if selected_docs else None
            )
            
            # 提取答案
            if isinstance(result, dict):
                answer = result.get('answer', str(result))
                web_sources = result.get('web_sources', [])
                document_sources = result.get('document_sources', [])
                metadata = result.get('metadata', {})
            else:
                answer = str(result)
                web_sources = []
                document_sources = []
                metadata = {}
            
            # 添加模式标识
            response = f"🤖 **LLM 直接对话模式**\n"
            if enable_web_search:
                response += "🌐 **已启用联网搜索**\n"
            if document_sources:
                response += f"📎 **已附加 {len(document_sources)} 个文档**\n"
            response += "\n" + "=" * 70 + "\n\n"
            response += answer
            
            # 添加文档附件信息
            if document_sources:
                response += "\n\n" + "=" * 70
                response += "\n📎 使用的文档附件:\n" + "=" * 70 + "\n"
                for i, doc in enumerate(document_sources, 1):
                    response += f"\n【文档 {i}】\n"
                    response += f"📄 文件: {doc}\n"
            
            # 添加网络来源信息
            if web_sources:
                response += "\n\n" + "=" * 70
                response += "\n🌐 网络参考来源:\n" + "=" * 70 + "\n"
                for i, source in enumerate(web_sources[:3], 1):
                    response += f"\n【网络来源 {i}】\n"
                    response += f"🔗 URL: {source.get('url', 'N/A')}\n"
                    response += f"📌 标题: {source.get('title', 'N/A')}\n"
                    snippet = source.get('snippet', '')
                    if snippet:
                        response += f"📝 摘要: {snippet[:200]}...\n"
                    response += "\n"
            
            return response
            
        except Exception as e:
            return f"❌ LLM 查询出错: {str(e)}\n\n请检查:\n1. API 配置是否正确\n2. 网络连接是否正常\n3. API 密钥是否有效"
    
    # RAG 模式需要索引
    else:  # RAG 模式
        if not INDEX_BUILT or AGENT is None:
            return "⚠️ RAG 模式需要先构建索引！\n\n步骤:\n1. 切换到「构建索引」标签页\n2. 输入文档目录路径\n3. 点击「提交」按钮\n4. 等待构建完成\n5. 返回「问答」标签页并选择 RAG 模式"
        
        try:
            result = AGENT.query(
                question=question,
                top_k=top_k,
                enable_web_search=enable_web_search
            )
            
            # 提取答案（字典格式）
            if isinstance(result, dict):
                answer = result.get('answer', str(result))
                source_nodes = result.get('source_nodes', [])
                web_sources = result.get('web_sources', [])
            else:
                # 兼容旧格式
                answer = str(result)
                source_nodes = []
                web_sources = []
            
            # 构建响应
            response = f"📚 **RAG 检索增强模式**\n"
            if enable_web_search:
                response += "🌐 **已启用联网搜索**\n"
            response += f"🎯 检索文档数: {top_k}\n"
            response += "\n" + "=" * 70 + "\n\n"
            response += answer
            
            # 添加文档来源信息
            if source_nodes:
                response += "\n\n" + "=" * 70
                response += "\n📚 文档参考来源:\n" + "=" * 70 + "\n"
                
                for i, node in enumerate(source_nodes[:3], 1):
                    file_name = node.metadata.get('file_name', '未知文档')
                    score = node.score if hasattr(node, 'score') else 0
                    
                    # 获取文本片段
                    text_snippet = ""
                    if hasattr(node, 'text') and node.text:
                        text_snippet = node.text.strip().replace('\n', ' ')
                        if len(text_snippet) > 200:
                            text_snippet = text_snippet[:200] + "..."
                    
                    response += f"\n【文档来源 {i}】\n"
                    response += f"📄 文件: {file_name}\n"
                    response += f"🎯 相似度: {score:.4f}\n"
                    if text_snippet:
                        response += f"📝 片段: {text_snippet}\n"
                    response += "\n"
            
            # 添加网络来源信息
            if web_sources:
                response += "\n" + "=" * 70
                response += "\n🌐 网络参考来源:\n" + "=" * 70 + "\n"
                for i, source in enumerate(web_sources[:3], 1):
                    response += f"\n【网络来源 {i}】\n"
                    response += f"🔗 URL: {source.get('url', 'N/A')}\n"
                    response += f"📌 标题: {source.get('title', 'N/A')}\n"
                    snippet = source.get('snippet', '')
                    if snippet:
                        response += f"📝 摘要: {snippet[:200]}...\n"
                    response += "\n"
            
            return response
            
        except Exception as e:
            return f"❌ RAG 查询出错: {str(e)}\n\n请尝试:\n1. 重新表述问题\n2. 检查索引是否正确构建\n3. 调整检索参数\n4. 查看系统日志"


# 创建问答界面
interface_qa = gr.Interface(
    fn=query_question,
    inputs=[
        gr.Textbox(
            lines=3,
            placeholder="在这里输入您的问题...\n例如: 请总结这篇论文的主要贡献",
            label="❓ 输入问题"
        ),
        gr.Radio(
            choices=["RAG 模式", "LLM 模式"],
            value="RAG 模式",
            label="🔧 查询模式",
            info="RAG: 基于文档检索增强 | LLM: 直接对话"
        ),
        gr.Checkbox(
            value=False,
            label="🌐 启用联网搜索",
            info="联网获取最新信息（两种模式均可用）"
        ),
        gr.Slider(
            minimum=1,
            maximum=10,
            value=DEFAULT_TOP_K,
            step=1,
            label="📊 检索文档数量 (Top-K)",
            info="仅 RAG 模式有效，控制返回的相关文档数量"
        ),
        gr.CheckboxGroup(
            choices=get_available_documents(),
            label="📎 附加文档 (仅 LLM 模式)",
            info="选择要作为附件发送给 LLM 的文档"
        )
    ],
    outputs=gr.Textbox(
        lines=25,
        label="💬 回答"
    ),
    title="💬 智能问答",
    description="""
    **功能说明:**
    - **RAG 模式**: 基于已构建的知识库检索相关文档后生成答案
      * 系统启动时会自动检测并加载已有索引
      * 如显示「✅ 已自动加载」则可直接使用，无需手动构建
      * 如显示「ℹ️ 未发现已有索引」则需先在「构建索引」标签页构建
    - **LLM 模式**: 直接与大语言模型对话，无需构建索引
      * 支持附加文档：可选择 data/documents 目录下的文档作为附件发送给 LLM
      * 文档会通过 Moonshot API 上传并提取内容，供 LLM 分析
    - **联网搜索**: 可选功能，两种模式均支持，获取实时网络信息
    """,
    examples=[
        ["请总结这篇论文的主要贡献", "RAG 模式", False, 3, []],
        ["这篇论文使用了什么研究方法？", "RAG 模式", False, 3, []],
        ["什么是大语言模型？", "LLM 模式", False, 3, []],
        ["最新的 AI 技术趋势是什么？", "LLM 模式", True, 3, []],
        ["解释一下 Transformer 架构", "RAG 模式", True, 5, []]
    ],
    cache_examples=False
)

interface_build = gr.Interface(
    fn=build_index,
    inputs=[
        gr.Textbox(
            value="./data/documents",
            placeholder="输入文档所在目录的路径",
            label="📁 文档目录路径"
        ),
        gr.Checkbox(
            value=True,
            label="强制重建索引",
            info="勾选将删除旧索引并重新构建，不勾选则尝试增量更新"
        )
    ],
    outputs=gr.Textbox(
        lines=20,
        label="📊 构建状态"
    ),
    title="📚 构建知识库索引",
    description="""
    **ℹ️ 重要提示:**
    - 如果启动时显示「✅ 已自动加载现有索引」，说明索引已就绪
    - **无需重复构建**，可直接使用 RAG 模式问答
    - 仅在以下情况需要重新构建:
      * 添加了新的文档
      * 删除或修改了现有文档
      * 想要调整索引参数
    
    **构建步骤:**
    1. 将论文文档放入指定目录（支持 PDF, DOCX, Markdown, TXT）
    2. 输入文档目录路径（默认: ./data/documents）
    3. 勾选「强制重建索引」（推荐）
    4. 点击「提交」按钮开始构建
    5. 查看详细的文件统计信息
    6. 构建成功后，前往「问答」标签页使用 RAG 模式
    """
)

# 组合两个标签页
demo = gr.TabbedInterface(
    [interface_qa, interface_build],
    tab_names=["💬 问答", "📚 构建索引"],
    title="📑 学术论文问答系统"
)


if __name__ == "__main__":
    print("=" * 70)
    print("Academic Paper Q&A System - Web UI")
    print("=" * 70)
    print("\n🚀 正在启动 Web 服务...\n")
    
    # 启动时检查已有索引
    print("🔍 检查已有索引...")
    status = check_existing_index()
    print(status)
    print()
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )
    
    print("\n" + "=" * 70)
    print("✅ Web UI 已启动！")
    print("=" * 70)
    print("\n📱 访问地址: http://127.0.0.1:7860")
    print("\n⌨️  按 Ctrl+C 停止服务")
    print("=" * 70)
    
    print("\n" + "=" * 70)
    print("✅ Web UI 已启动！")
    print("=" * 70)
    print("\n📱 访问地址: http://127.0.0.1:7860")
    print("\n⌨️  按 Ctrl+C 停止服务")
    print("=" * 70)
