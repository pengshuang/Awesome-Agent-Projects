#!/usr/bin/env python3
"""
学术论文问答系统 - 多轮对话命令行工具
支持对话历史管理的增强版
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from init_system import initialize_system
from src.agent import AcademicAgent
from src.utils.logger import logger

# 初始化系统（LlamaIndex Settings）
initialize_system()


class Colors:
    """终端颜色代码"""
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_separator(char="-", length=70):
    """打印分隔线"""
    print(f"{Colors.CYAN}{char * length}{Colors.END}")


def display_welcome():
    """显示欢迎信息"""
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'':^20}学术论文智能问答系统 - 多轮对话版{'':^20}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}✨ 支持多轮对话，记忆上下文{Colors.END}")
    print(f"{Colors.CYAN}✨ 基于 RAG 技术，智能检索学术文献{Colors.END}")
    print(f"{Colors.CYAN}✨ 支持联网搜索，获取最新信息{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'='*70}{Colors.END}\n")


def display_chat_history(agent: AcademicAgent):
    """显示对话历史"""
    history = agent.get_chat_history()
    
    if not history:
        print(f"\n{Colors.YELLOW}📝 暂无对话历史{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}📜 对话历史（共 {len(history) // 2} 轮）:{Colors.END}")
    print_separator("=", 70)
    
    for i, msg in enumerate(history):
        role_icon = "👤" if msg["role"] == "user" else "🤖"
        role_name = "用户" if msg["role"] == "user" else "助手"
        role_color = Colors.YELLOW if msg["role"] == "user" else Colors.GREEN
        
        print(f"\n{role_color}{Colors.BOLD}{role_icon} {role_name}:{Colors.END}")
        content = msg["content"]
        # 限制显示长度
        if len(content) > 200:
            content = content[:200] + "..."
        print(f"  {content}")
    
    print_separator("=", 70)


def rag_chat_mode(agent: AcademicAgent):
    """
    RAG 问答模式（支持多轮对话）
    """
    print(f"\n{Colors.BOLD}{Colors.GREEN}🚀 进入多轮对话模式（RAG 增强）{Colors.END}")
    print(f"\n{Colors.YELLOW}💡 命令说明:{Colors.END}")
    print(f"  • {Colors.CYAN}'clear'{Colors.END}  - 清除对话历史")
    print(f"  • {Colors.CYAN}'history'{Colors.END} - 查看对话历史")
    print(f"  • {Colors.CYAN}'toggle'{Colors.END} - 切换对话历史开关")
    print(f"  • {Colors.CYAN}'quit'{Colors.END}   - 退出对话\n")
    
    question_count = 0
    use_history = True  # 默认启用对话历史
    
    while True:
        # 显示对话状态
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
        history_info = f"对话轮数: {len(agent.chat_history) // 2}" if agent.chat_history else "新对话"
        history_status = "✅" if use_history else "❌"
        print(f"{Colors.BOLD}{Colors.PURPLE}💬 问答 #{question_count + 1} | {history_info} | 历史: {history_status}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
        
        # 获取用户问题
        print(f"\n{Colors.YELLOW}请输入问题: {Colors.END}", end="")
        question = input().strip()
        
        if not question:
            print(f"{Colors.RED}⚠ 问题不能为空{Colors.END}")
            continue
        
        # 处理特殊命令
        if question.lower() in ['quit', 'exit', 'q', '退出']:
            print(f"\n{Colors.GREEN}👋 退出对话模式{Colors.END}")
            break
        
        if question.lower() in ['clear', '清除']:
            agent.clear_chat_history()
            question_count = 0
            print(f"\n{Colors.GREEN}✅ 对话历史已清除{Colors.END}")
            continue
        
        if question.lower() in ['history', '历史']:
            display_chat_history(agent)
            continue
        
        if question.lower() in ['toggle', '切换']:
            use_history = not use_history
            status = "启用" if use_history else "禁用"
            print(f"\n{Colors.GREEN}✅ 对话历史已{status}{Colors.END}")
            continue
        
        # 询问是否联网搜索
        print(f"\n{Colors.YELLOW}启用联网搜索? (y/n，默认n): {Colors.END}", end="")
        web_choice = input().strip().lower()
        enable_web = web_choice in ['y', 'yes', '是']
        
        # 执行查询
        print(f"\n{Colors.CYAN}🤔 正在思考...{Colors.END}", end="", flush=True)
        
        try:
            start_time = datetime.now()
            result = agent.query(
                question,
                verbose=False,
                enable_web_search=enable_web,
                use_history=use_history
            )
            elapsed = (datetime.now() - start_time).total_seconds()
            
            print(f"\r{' ' * 50}\r", end="")  # 清除"正在思考..."
            
            question_count += 1
            
            # 显示网络搜索结果
            if result.get('web_sources'):
                print(f"\n{Colors.BOLD}{Colors.BLUE}🌐 网络搜索结果:{Colors.END}")
                print_separator("-", 70)
                for i, source in enumerate(result['web_sources'][:3], 1):
                    print(f"{Colors.CYAN}[{i}]{Colors.END} {Colors.BOLD}{source['title']}{Colors.END}")
                    print(f"    🔗 {source['url']}")
                    snippet = source['snippet'][:120] + "..." if len(source['snippet']) > 120 else source['snippet']
                    print(f"    {snippet}\n")
            
            # 显示答案
            print(f"\n{Colors.BOLD}{Colors.GREEN}🤖 助手回答:{Colors.END}")
            print_separator("=", 70)
            print(f"{result['answer']}")
            print_separator("=", 70)
            
            # 显示统计信息
            metadata = result['metadata']
            print(f"\n{Colors.CYAN}📊 查询统计:{Colors.END}")
            print(f"  • 耗时: {elapsed:.2f} 秒")
            print(f"  • 参考文档: {metadata['num_sources']} 个")
            if metadata.get('num_web_sources', 0) > 0:
                print(f"  • 网络资源: {metadata['num_web_sources']} 个")
            if metadata.get('use_history'):
                print(f"  • 对话轮数: {metadata['history_turns']} 轮")
            print(f"  • 答案长度: {len(result['answer'])} 字符")
            
            # 显示参考来源
            if result['source_nodes']:
                print(f"\n{Colors.CYAN}📚 主要参考来源:{Colors.END}")
                for i, node in enumerate(result['source_nodes'][:3], 1):
                    file_name = node.metadata.get('file_name', 'Unknown')
                    score = node.score if hasattr(node, 'score') else 0
                    
                    print(f"  {Colors.BOLD}[{i}] {file_name}{Colors.END} {Colors.YELLOW}(相似度: {score:.3f}){Colors.END}")
                    
                    if hasattr(node, 'text') and node.text:
                        snippet = node.text[:150].replace('\n', ' ')
                        print(f"      {Colors.PURPLE}» {snippet}...{Colors.END}")
        
        except Exception as e:
            print(f"\n{Colors.RED}❌ 查询失败: {e}{Colors.END}")
            logger.error(f"查询出错: {e}", exc_info=True)


def direct_llm_mode(agent: AcademicAgent):
    """
    直接 LLM 对话模式（不使用 RAG，支持多轮对话）
    """
    print(f"\n{Colors.BOLD}{Colors.GREEN}💬 进入直接对话模式（纯 LLM）{Colors.END}")
    print(f"\n{Colors.YELLOW}💡 命令说明:{Colors.END}")
    print(f"  • {Colors.CYAN}'clear'{Colors.END}  - 清除对话历史")
    print(f"  • {Colors.CYAN}'history'{Colors.END} - 查看对话历史")
    print(f"  • {Colors.CYAN}'quit'{Colors.END}   - 退出对话\n")
    
    # 为 LLM 模式创建独立的历史
    llm_history = []
    question_count = 0
    
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
        history_info = f"对话轮数: {len(llm_history) // 2}" if llm_history else "新对话"
        print(f"{Colors.BOLD}{Colors.PURPLE}💬 对话 #{question_count + 1} | {history_info}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
        
        print(f"\n{Colors.YELLOW}请输入问题: {Colors.END}", end="")
        question = input().strip()
        
        if not question:
            print(f"{Colors.RED}⚠ 问题不能为空{Colors.END}")
            continue
        
        if question.lower() in ['quit', 'exit', 'q', '退出']:
            print(f"\n{Colors.GREEN}👋 退出对话模式{Colors.END}")
            break
        
        if question.lower() in ['clear', '清除']:
            llm_history = []
            question_count = 0
            print(f"\n{Colors.GREEN}✅ 对话历史已清除{Colors.END}")
            continue
        
        if question.lower() in ['history', '历史']:
            if not llm_history:
                print(f"\n{Colors.YELLOW}📝 暂无对话历史{Colors.END}")
            else:
                print(f"\n{Colors.BOLD}{Colors.GREEN}📜 对话历史:{Colors.END}")
                print_separator("=", 70)
                for msg in llm_history:
                    role_icon = "👤" if msg["role"] == "user" else "🤖"
                    role_name = "用户" if msg["role"] == "user" else "助手"
                    role_color = Colors.YELLOW if msg["role"] == "user" else Colors.GREEN
                    print(f"\n{role_color}{Colors.BOLD}{role_icon} {role_name}:{Colors.END}")
                    print(f"  {msg['content'][:200]}...")
                print_separator("=", 70)
            continue
        
        # 构建带历史的上下文
        context = ""
        if llm_history:
            context = "对话历史:\n"
            for msg in llm_history[-(10*2):]:  # 最近10轮
                role_name = "用户" if msg["role"] == "user" else "助手"
                context += f"{role_name}: {msg['content']}\n"
            context += f"\n当前问题: {question}"
        else:
            context = question
        
        print(f"\n{Colors.CYAN}🤔 正在思考...{Colors.END}", end="", flush=True)
        
        try:
            start_time = datetime.now()
            result = agent.query_direct(context, enable_web_search=False)
            elapsed = (datetime.now() - start_time).total_seconds()
            
            print(f"\r{' ' * 50}\r", end="")
            
            question_count += 1
            answer = result['answer']
            
            # 更新历史
            llm_history.append({"role": "user", "content": question})
            llm_history.append({"role": "assistant", "content": answer})
            
            # 显示答案
            print(f"\n{Colors.BOLD}{Colors.GREEN}🤖 助手回答:{Colors.END}")
            print_separator("=", 70)
            print(f"{answer}")
            print_separator("=", 70)
            
            print(f"\n{Colors.CYAN}📊 耗时: {elapsed:.2f} 秒{Colors.END}")
        
        except Exception as e:
            print(f"\n{Colors.RED}❌ 查询失败: {e}{Colors.END}")
            logger.error(f"查询出错: {e}", exc_info=True)


def display_menu():
    """显示主菜单"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'':^25}主菜单{'':^25}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"\n{Colors.CYAN}[1]{Colors.END} 🔍 RAG 多轮问答（基于学术文献）")
    print(f"{Colors.CYAN}[2]{Colors.END} 💬 直接对话（纯 LLM）")
    print(f"{Colors.CYAN}[3]{Colors.END} 🔄 重建索引")
    print(f"{Colors.CYAN}[4]{Colors.END} 📊 查看系统信息")
    print(f"{Colors.CYAN}[5]{Colors.END} ❌ 退出系统")
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")


def display_system_info(agent: AcademicAgent):
    """显示系统信息"""
    print(f"\n{Colors.BOLD}{Colors.GREEN}📊 系统信息:{Colors.END}")
    print_separator("=", 70)
    print(f"  • 文档目录: {agent.documents_dir}")
    print(f"  • 索引目录: {agent.index_dir}")
    print(f"  • 已加载文档: {len(agent.documents)} 个")
    print(f"  • 索引状态: {'✅ 已就绪' if agent.index else '❌ 未构建'}")
    print(f"  • 当前对话轮数: {len(agent.chat_history) // 2}")
    print(f"  • 最大历史轮数: {agent.max_history_turns}")
    print_separator("=", 70)


def main():
    """主函数"""
    display_welcome()
    
    # 初始化 Agent
    print(f"{Colors.CYAN}🔧 正在初始化系统...{Colors.END}")
    try:
        agent = AcademicAgent(auto_load=True)
        print(f"{Colors.GREEN}✅ 系统初始化成功{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ 系统初始化失败: {e}{Colors.END}")
        logger.error(f"初始化失败: {e}", exc_info=True)
        return
    
    # 主循环
    while True:
        display_menu()
        
        print(f"\n{Colors.YELLOW}请选择功能 (1-5): {Colors.END}", end="")
        choice = input().strip()
        
        if choice == '1':
            rag_chat_mode(agent)
        elif choice == '2':
            direct_llm_mode(agent)
        elif choice == '3':
            print(f"\n{Colors.YELLOW}⚠ 确认重建索引？这将清除现有索引 (y/n): {Colors.END}", end="")
            confirm = input().strip().lower()
            if confirm in ['y', 'yes', '是']:
                try:
                    print(f"\n{Colors.CYAN}🔄 正在重建索引...{Colors.END}")
                    agent.rebuild_index()
                    print(f"{Colors.GREEN}✅ 索引重建成功{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}❌ 索引重建失败: {e}{Colors.END}")
        elif choice == '4':
            display_system_info(agent)
        elif choice == '5':
            print(f"\n{Colors.GREEN}👋 感谢使用，再见！{Colors.END}\n")
            break
        else:
            print(f"{Colors.RED}❌ 无效选择，请输入 1-5{Colors.END}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠ 用户中断{Colors.END}")
        print(f"{Colors.GREEN}👋 再见！{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.RED}❌ 程序异常: {e}{Colors.END}")
        logger.error(f"程序异常: {e}", exc_info=True)
