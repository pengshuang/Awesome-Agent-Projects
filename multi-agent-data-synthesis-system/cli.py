"""Command-line interface for data synthesis."""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from loguru import logger

from config import settings
from src.graph import DataSynthesisGraph
from src.models import TaskType
from src.utils import ensure_directories, save_qa_pairs, read_document_file


def setup_cli_logging():
    """Setup logging for CLI."""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
        colorize=True,
    )
    
    log_file = Path(settings.log_dir) / f"cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger.add(
        str(log_file),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="DEBUG",
    )


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent 数据合成系统 - 命令行版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从文件生成逻辑推理类问答对
  python cli.py --input data/example_document.md --task-type logical --iterations 10
  
  # 从标准输入读取文档
  cat document.txt | python cli.py --task-type numerical --iterations 5
  
  # 指定输出文件
  python cli.py --input doc.md --task-type query --output results.json
        """
    )
    
    # Input options
    parser.add_argument(
        '-i', '--input',
        type=str,
        help='输入文档文件路径（不指定则从标准输入读取）'
    )
    
    parser.add_argument(
        '-t', '--task-type',
        type=str,
        required=True,
        choices=['logical', 'numerical', 'query', 'summary'],
        help='任务类型: logical(逻辑推理), numerical(数值计算), query(信息查询), summary(总结摘要)'
    )
    
    parser.add_argument(
        '-n', '--iterations',
        type=int,
        default=10,
        help='最大迭代次数（默认: 10）'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='输出文件路径（不指定则自动生成）'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细日志'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_cli_logging()
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG", colorize=True)
    
    # Initialize
    ensure_directories()
    
    # Read document
    logger.info("读取文档内容...")
    if args.input:
        try:
            document = read_document_file(args.input)
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            sys.exit(1)
    else:
        logger.info("从标准输入读取...")
        document = sys.stdin.read()
    
    if len(document) < 10:
        logger.error("文档内容过短（至少10个字符）")
        sys.exit(1)
    
    logger.success(f"文档读取成功（{len(document)} 字符）")
    
    # Map task type
    task_type_map = {
        'logical': TaskType.LOGICAL_REASONING,
        'numerical': TaskType.NUMERICAL_CALCULATION,
        'query': TaskType.INFORMATION_QUERY,
        'summary': TaskType.SUMMARIZATION,
    }
    task_type = task_type_map[args.task_type]
    
    # Create state
    logger.info(f"开始数据合成 - 任务类型: {task_type.value}, 迭代次数: {args.iterations}")
    state = {
        "document": document,
        "task_type": task_type.value,
        "max_iterations": args.iterations,
    }
    
    # Run synthesis
    try:
        graph = DataSynthesisGraph()
        final_state = graph.run(state)
        
        valid_pairs = final_state.get("valid_pairs", [])
        
        if not valid_pairs:
            logger.warning("未生成有效的问答对")
            sys.exit(0)
        
        logger.success(f"成功生成 {len(valid_pairs)} 个问答对")
        
        # Save results
        if args.output:
            output_file = args.output
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(valid_pairs, f, ensure_ascii=False, indent=2, default=str)
        else:
            output_file = save_qa_pairs(valid_pairs, args.task_type)
        
        logger.success(f"结果已保存到: {output_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("数据合成完成")
        print("="*60)
        print(f"总迭代次数: {final_state.get('current_iteration', 0)}")
        print(f"有效问答对: {len(valid_pairs)}")
        print(f"验证失败: {final_state.get('failed_attempts', 0)}")
        print(f"输出文件: {output_file}")
        print("="*60 + "\n")
        
        # Print first QA pair as preview
        if valid_pairs:
            print("预览第一个问答对:")
            print("-"*60)
            qa = valid_pairs[0]
            print(f"问题: {qa['question']}")
            print(f"答案: {qa['answer'][:200]}..." if len(qa['answer']) > 200 else f"答案: {qa['answer']}")
            print("-"*60 + "\n")
        
    except KeyboardInterrupt:
        logger.warning("用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"合成失败: {e}")
        if args.verbose:
            logger.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
