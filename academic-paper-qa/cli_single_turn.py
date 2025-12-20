#!/usr/bin/env python3
"""
学术论文问答系统 - 主程序

提供命令行交互界面，支持智能问答、论文管理等功能
"""

import os
import sys
from pathlib import Path
from datetime import datetime

from loguru import logger

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from init_system import initialize_system
from src.agent import AcademicAgent, create_agent


# 颜色和样式定义（ANSI 转义码）
class Colors:
    """终端颜色定义"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")


def print_success(text: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """打印错误信息"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text: str):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_separator(char="=", length=70):
    """打印分隔线"""
    print(f"{Colors.CYAN}{char * length}{Colors.END}")


def display_welcome():
    """显示欢迎界面"""
    print_separator("=")
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║          📚 学术论文智能问答系统 v1.0                    ║
    ║                                                          ║
    ║          Academic Paper Q&A System                       ║
    ║          Powered by LlamaIndex & LLM                     ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    print(Colors.END)
    print_separator("=")


def display_menu():
    """显示主菜单"""
    print(f"\n{Colors.BOLD}📋 主菜单{Colors.END}")
    print_separator("-")
    print(f"{Colors.CYAN}[1]{Colors.END} 💬 问答模式 (RAG) - 基于本地文档知识库")
    print(f"{Colors.CYAN}[2]{Colors.END} 🤖 对话模式 (LLM) - 基于大模型通用知识")
    print(f"{Colors.CYAN}[3]{Colors.END} 📄 列出论文 - 查看已加载的论文")
    print(f"{Colors.CYAN}[4]{Colors.END} 🔄 重建索引 - 重新构建向量索引")
    print(f"{Colors.CYAN}[5]{Colors.END} ℹ️  查看统计 - 显示系统统计信息")
    print(f"{Colors.CYAN}[6]{Colors.END} 🚪 退出程序")
    print_separator("-")


def display_chat_examples():
    """显示问答示例"""
    print(f"\n{Colors.BOLD}💡 提问示例：{Colors.END}")
    examples = [
        "这篇论文的主要贡献是什么？",
        "论文中提出了什么新方法？",
        "实验结果如何？有什么发现？",
        "论文的研究背景是什么？",
        "有哪些局限性和未来工作？",
    ]
    for i, example in enumerate(examples, 1):
        print(f"  {Colors.YELLOW}{i}.{Colors.END} {example}")
    print()


def chat_mode(agent: AcademicAgent):
    """
    问答模式 (RAG)
    
    Args:
        agent: AcademicAgent 实例
    """
    print_header("💬 问答模式 (RAG) - 基于本地文档")
    print_separator("-")
    print(f"{Colors.GREEN}提示：{Colors.END}")
    print(f"  • 输入问题，系统将从已加载的论文中检索相关内容回答")
    print(f"  • 每次提问可选择是否联网搜索增强答案")
    print(f"  • 输入 {Colors.YELLOW}'exit'{Colors.END} 或 {Colors.YELLOW}'quit'{Colors.END} 返回主菜单")
    print(f"  • 输入 {Colors.YELLOW}'examples'{Colors.END} 查看提问示例")
    print_separator("-")
    
    # 显示示例
    display_chat_examples()
    
    question_count = 0
    
    while True:
        try:
            # 获取用户输入
            print(f"{Colors.BOLD}{Colors.BLUE}您的问题:{Colors.END} ", end="")
            question = input().strip()
            
            # 检查退出命令
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit', 'q', '退出', '返回']:
                print_success("退出问答模式")
                break
            
            # 显示示例
            if question.lower() in ['examples', 'example', '示例']:
                display_chat_examples()
                continue
            
            # 询问是否联网搜索
            print(f"\n{Colors.YELLOW}是否启用联网搜索增强? (y/n，直接回车默认不启用): {Colors.END}", end="")
            web_choice = input().strip().lower()
            enable_web = web_choice in ['y', 'yes', '是']
            
            # 执行查询
            if enable_web:
                print(f"\n{Colors.CYAN}🤔 正在思考（联网搜索已启用）...{Colors.END}")
            else:
                print(f"\n{Colors.CYAN}🤔 正在思考...{Colors.END}")
            
            start_time = datetime.now()
            result = agent.query(question, verbose=False, enable_web_search=enable_web)
            elapsed = (datetime.now() - start_time).total_seconds()
            
            question_count += 1
            
            # 显示网络搜索结果（如果启用）
            if result.get('web_sources'):
                print(f"\n{Colors.BOLD}{Colors.BLUE}🌐 网络搜索结果:{Colors.END}")
                print_separator("-", 70)
                for i, source in enumerate(result['web_sources'], 1):
                    print(f"{Colors.CYAN}[{i}]{Colors.END} {Colors.BOLD}{source['title']}{Colors.END}")
                    print(f"    🔗 {source['url']}")
                    print(f"    {source['snippet'][:150]}...")
                    print()
            
            # 显示答案
            print(f"\n{Colors.BOLD}{Colors.GREEN}📝 回答:{Colors.END}")
            print_separator("-", 70)
            print(f"{result['answer']}")
            print_separator("-", 70)
            
            # 显示统计信息
            print(f"\n{Colors.CYAN}📊 查询统计:{Colors.END}")
            print(f"  • 耗时: {elapsed:.2f} 秒")
            print(f"  • 参考文档数: {result['metadata']['num_sources']}")
            if result['metadata'].get('num_web_sources', 0) > 0:
                print(f"  • 网络资源数: {result['metadata']['num_web_sources']}")
            print(f"  • 答案长度: {len(result['answer'])} 字符")
            
            # 显示源文档片段（不仅仅是文件名）
            if result['source_nodes']:
                print(f"\n{Colors.CYAN}📚 参考来源（RAG检索片段）:{Colors.END}")
                for i, node in enumerate(result['source_nodes'][:3], 1):  # 只显示前3个
                    file_name = node.metadata.get('file_name', 'Unknown')
                    score = node.score if hasattr(node, 'score') else 'N/A'
                    
                    # 显示文件名和相似度
                    print(f"\n  {Colors.BOLD}[{i}] {file_name}{Colors.END} {Colors.YELLOW}(相似度: {score:.3f}){Colors.END}")
                    
                    # 显示原文片段
                    if hasattr(node, 'text') and node.text:
                        # 截取前300个字符并清理换行
                        text_preview = node.text[:300].replace('\n', ' ').strip()
                        print(f"      {Colors.GREEN}📝 原文:{Colors.END} {text_preview}...")
            
            print()
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}检测到中断信号{Colors.END}")
            break
        except Exception as e:
            print_error(f"查询出错: {e}")
            logger.exception("查询异常")
    
    if question_count > 0:
        print_success(f"本次会话共提问 {question_count} 个问题")


def direct_llm_mode(agent: AcademicAgent):
    """
    对话模式 (LLM) - 基于大模型通用知识
    
    Args:
        agent: AcademicAgent 实例
    """
    print_header("🤖 对话模式 (LLM) - 基于大模型通用知识")
    print_separator("-")
    print(f"{Colors.GREEN}提示：{Colors.END}")
    print(f"  • 输入问题，系统将直接使用大模型的通用知识回答")
    print(f"  • 不依赖本地文档，适合一般性问题")
    print(f"  • 每次提问可选择是否联网搜索增强答案")
    print(f"  • 输入 {Colors.YELLOW}'exit'{Colors.END} 或 {Colors.YELLOW}'quit'{Colors.END} 返回主菜单")
    print_separator("-")
    print()
    
    question_count = 0
    
    while True:
        try:
            # 获取用户问题
            print(f"{Colors.BOLD}{Colors.BLUE}您的问题:{Colors.END} ", end="")
            question = input().strip()
            
            # 检查退出命令
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit', 'q', '退出', '返回']:
                print_success("退出对话模式")
                break
            
            # 询问是否联网搜索
            print(f"\n{Colors.YELLOW}是否启用联网搜索增强? (y/n，直接回车默认不启用): {Colors.END}", end="")
            web_choice = input().strip().lower()
            enable_web = web_choice in ['y', 'yes', '是']
            
            # 执行查询
            if enable_web:
                print(f"\n{Colors.CYAN}🤔 正在思考（联网搜索已启用）...{Colors.END}")
            else:
                print(f"\n{Colors.CYAN}🤔 正在思考...{Colors.END}")
            
            start_time = datetime.now()
            result = agent.query_direct(question, context=None, enable_web_search=enable_web)
            elapsed = (datetime.now() - start_time).total_seconds()
            
            question_count += 1
            
            # 显示网络搜索结果（如果启用）
            if result.get('web_sources'):
                print(f"\n{Colors.BOLD}{Colors.BLUE}🌐 网络搜索结果:{Colors.END}")
                print_separator("-", 70)
                for i, source in enumerate(result['web_sources'], 1):
                    print(f"{Colors.CYAN}[{i}]{Colors.END} {Colors.BOLD}{source['title']}{Colors.END}")
                    print(f"    🔗 {source['url']}")
                    print(f"    {source['snippet'][:150]}...")
                    print()
            
            # 显示答案
            print(f"\n{Colors.BOLD}{Colors.GREEN}📝 回答:{Colors.END}")
            print_separator("-", 70)
            print(f"{result['answer']}")
            print_separator("-", 70)
            
            # 显示统计信息
            print(f"\n{Colors.CYAN}📊 查询统计:{Colors.END}")
            print(f"  • 模式: 对话模式（基于大模型通用知识）")
            print(f"  • 耗时: {elapsed:.2f} 秒")
            if result['metadata'].get('num_web_sources', 0) > 0:
                print(f"  • 网络资源数: {result['metadata']['num_web_sources']}")
            print(f"  • 答案长度: {len(result['answer'])} 字符")
            print()
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}检测到中断信号{Colors.END}")
            break
        except Exception as e:
            print_error(f"查询出错: {e}")
            logger.exception("查询异常")
    
    if question_count > 0:
        print_success(f"本次会话共提问 {question_count} 个问题")


def list_papers_mode(agent: AcademicAgent):
    """
    列出论文模式
    
    Args:
        agent: AcademicAgent 实例
    """
    print_header("📄 已加载的论文列表")
    print_separator("-")
    
    try:
        papers = agent.list_papers(detailed=False)
        
        if not papers:
            print_warning("未找到任何论文")
            return
        
        print(f"\n{Colors.BOLD}总计: {len(papers)} 篇论文{Colors.END}\n")
        
        # 显示论文列表
        for i, paper in enumerate(papers, 1):
            print(f"{Colors.CYAN}[{i}]{Colors.END} {Colors.BOLD}{paper['file_name']}{Colors.END}")
            print(f"    类型: {paper['file_type'].upper()}")
            print(f"    大小: {paper['file_size_mb']:.2f} MB")
            
            if paper['file_type'] == 'pdf' and 'page_count' in paper:
                print(f"    页数: {paper['page_count']}")
            
            print(f"    字符数: {paper['total_chars']:,}")
            print()
        
        # 统计信息
        print_separator("-")
        total_size = sum(p['file_size_mb'] for p in papers)
        total_chars = sum(p['total_chars'] for p in papers)
        
        from collections import Counter
        file_types = Counter(p['file_type'] for p in papers)
        
        print(f"\n{Colors.BOLD}统计信息:{Colors.END}")
        print(f"  • 总大小: {total_size:.2f} MB")
        print(f"  • 总字符数: {total_chars:,}")
        print(f"  • 文件类型: {dict(file_types)}")
        print()
        
    except Exception as e:
        print_error(f"列出论文失败: {e}")
        logger.exception("列出论文异常")


def rebuild_index_mode(agent: AcademicAgent):
    """
    重建索引模式
    
    Args:
        agent: AcademicAgent 实例
    """
    print_header("🔄 重建向量索引")
    print_separator("-")
    
    print_warning("警告: 重建索引将删除现有索引并重新构建")
    print(f"      这可能需要几分钟时间，具体取决于文档数量\n")
    
    # 确认
    print(f"{Colors.YELLOW}确定要继续吗? (yes/no): {Colors.END}", end="")
    confirm = input().strip().lower()
    
    if confirm not in ['yes', 'y', '是', 'ok']:
        print_warning("已取消重建索引")
        return
    
    try:
        print(f"\n{Colors.CYAN}开始重建索引...{Colors.END}\n")
        
        # 重建索引
        start_time = datetime.now()
        agent.rebuild_index()
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print()
        print_success(f"索引重建完成！耗时: {elapsed:.2f} 秒")
        
        # 显示统计
        stats = agent.get_stats()
        if 'index_doc_count' in stats:
            print(f"  • 索引包含 {stats['index_doc_count']} 个文档块")
        
    except Exception as e:
        print_error(f"重建索引失败: {e}")
        logger.exception("重建索引异常")


def show_stats_mode(agent: AcademicAgent):
    """
    显示统计信息模式
    
    Args:
        agent: AcademicAgent 实例
    """
    print_header("ℹ️  系统统计信息")
    print_separator("-")
    
    try:
        stats = agent.get_stats()
        
        print(f"\n{Colors.BOLD}Agent 状态:{Colors.END}")
        print(f"  • 文档目录: {stats['documents_dir']}")
        print(f"  • 索引目录: {stats['index_dir']}")
        print(f"  • 索引存在: {Colors.GREEN if stats['index_exists'] else Colors.RED}{stats['index_exists']}{Colors.END}")
        print(f"  • 已加载文档: {stats['documents_loaded']}")
        print(f"  • 查询引擎就绪: {Colors.GREEN if stats['query_engine_ready'] else Colors.RED}{stats['query_engine_ready']}{Colors.END}")
        
        if 'index_doc_count' in stats and stats['index_doc_count'] != 'N/A':
            print(f"  • 索引文档块数: {stats['index_doc_count']}")
        
        # 从配置获取更多信息
        from config import SystemConfig
        print(f"\n{Colors.BOLD}配置信息:{Colors.END}")
        print(f"  • LLM 模型: {os.getenv('LLM_MODEL', 'N/A')}")
        print(f"  • Embedding 提供商: {os.getenv('EMBEDDING_PROVIDER', 'huggingface')}")
        print(f"  • Embedding 模型: {os.getenv('EMBEDDING_MODEL_NAME', 'BAAI/bge-small-zh-v1.5')}")
        print(f"  • Chunk 大小: {SystemConfig.CHUNK_SIZE}")
        print(f"  • Top-K: {SystemConfig.RETRIEVAL_TOP_K}")
        print()
        
    except Exception as e:
        print_error(f"获取统计信息失败: {e}")
        logger.exception("获取统计信息异常")


def initialize_agent() -> AcademicAgent:
    """
    初始化 Agent
    
    Returns:
        AcademicAgent 实例
    """
    print_header("🚀 系统初始化")
    print_separator("-")
    
    try:
        # 初始化系统配置
        print(f"{Colors.CYAN}1. 初始化系统配置...{Colors.END}")
        initialize_system()
        print_success("系统配置初始化完成")
        
        # 创建 Agent
        print(f"\n{Colors.CYAN}2. 创建 Agent...{Colors.END}")
        agent = AcademicAgent()
        print_success("Agent 创建完成")
        
        # 显示已加载的论文
        print(f"\n{Colors.CYAN}3. 已加载的论文:{Colors.END}")
        papers = agent.list_papers(detailed=False)
        if papers:
            for i, paper in enumerate(papers[:5], 1):  # 只显示前5个
                print(f"   {i}. {paper['file_name']} ({paper['file_size_mb']:.2f} MB)")
            if len(papers) > 5:
                print(f"   ... 还有 {len(papers) - 5} 篇论文")
        else:
            print_warning("   未找到任何论文")
        
        print()
        print_separator("=")
        print_success("系统初始化完成，可以开始使用！")
        
        return agent
        
    except Exception as e:
        print_error(f"初始化失败: {e}")
        logger.exception("系统初始化异常")
        print(f"\n{Colors.YELLOW}提示:{Colors.END}")
        print("  1. 请检查是否已安装所有依赖: pip install -r requirements.txt")
        print("  2. 请检查 .env 文件配置是否正确")
        print("  3. 请确保 data/documents 目录下有论文文件")
        sys.exit(1)


def main():
    """主函数"""
    # 配置日志（只显示重要信息）
    logger.remove()
    logger.add(
        sys.stderr,
        level="SUCCESS",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )
    
    # 显示欢迎界面
    display_welcome()
    
    # 初始化 Agent
    agent = initialize_agent()
    
    # 主循环
    while True:
        try:
            # 显示菜单
            display_menu()
            
            # 获取用户选择
            print(f"{Colors.BOLD}请选择功能 (1-6): {Colors.END}", end="")
            choice = input().strip()
            
            if choice == '1':
                # RAG问答模式
                chat_mode(agent)
            
            elif choice == '2':
                # 直接LLM模式
                direct_llm_mode(agent)
            
            elif choice == '3':
                # 列出论文
                list_papers_mode(agent)
                input(f"\n{Colors.CYAN}按 Enter 键继续...{Colors.END}")
            
            elif choice == '4':
                # 重建索引
                rebuild_index_mode(agent)
                input(f"\n{Colors.CYAN}按 Enter 键继续...{Colors.END}")
            
            elif choice == '5':
                # 查看统计
                show_stats_mode(agent)
                input(f"\n{Colors.CYAN}按 Enter 键继续...{Colors.END}")
            
            elif choice == '6':
                # 退出程序
                print_header("👋 感谢使用")
                print_separator("-")
                print(f"{Colors.GREEN}再见！{Colors.END}\n")
                break
            
            else:
                print_error(f"无效的选项: {choice}")
                print(f"{Colors.YELLOW}请输入 1-5 之间的数字{Colors.END}")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}检测到中断信号{Colors.END}")
            print_header("👋 感谢使用")
            print(f"{Colors.GREEN}再见！{Colors.END}\n")
            break
        
        except Exception as e:
            print_error(f"发生错误: {e}")
            logger.exception("主循环异常")


if __name__ == "__main__":
    main()
