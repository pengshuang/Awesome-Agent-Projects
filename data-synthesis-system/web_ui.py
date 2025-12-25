"""Gradio Web UI for data synthesis system."""

import gradio as gr
import time
from pathlib import Path
from loguru import logger

from config import settings, PROMPTS
from src.models import TaskType, SynthesisRequest
from src.graph import DataSynthesisGraph
from src.utils import (
    ensure_directories,
    save_qa_pairs,
    format_qa_for_display,
    format_iteration_status,
    read_document_file,
)


# Initialize
ensure_directories()

# Global stop flag
stop_flag = {"should_stop": False}


def format_iteration_detail(detail: dict, iteration: int) -> str:
    """Format iteration detail for display."""
    md = f"""
---
## 🔄 迭代 {iteration}

<div class="proposer-block">

### 📝 提议者 (Proposer)

"""
    
    if detail.get("proposer_output"):
        prop = detail["proposer_output"]
        md += f"""
**生成的问题：**
{prop.get('question', 'N/A')}

**参考答案：**
{prop.get('answer', 'N/A')}

**生成理由：**
{prop.get('reasoning', 'N/A')}

"""
    else:
        md += "_未生成_\n\n"
    
    md += """</div>

<div class="solver-block">

### 🔍 求解者 (Solver)

"""
    
    if detail.get("solver_output"):
        solver = detail["solver_output"]
        md += """
**推理步骤：**

"""
        reasoning_steps = solver.get("reasoning_steps", [])
        for i, step in enumerate(reasoning_steps, 1):
            # Clean up the step text and format it nicely
            step_text = str(step).strip()
            # Remove leading number and dot if present (e.g., "1. " or "1) ")
            import re
            step_text = re.sub(r'^\d+[\.\)]\s*', '', step_text)
            # Add indentation for better readability
            md += f"{i}. {step_text}\n\n"
        
        md += f"""**最终答案：**

{solver.get('final_answer', 'N/A')}

"""
    else:
        md += "_未生成_\n\n"
    
    md += """</div>

<div class="validator-block">

### ✅ 验证者 (Validator)

"""
    
    if detail.get("validator_output"):
        validator = detail["validator_output"]
        score = validator.get("score", 0)
        is_valid = validator.get("is_valid", False)
        status_emoji = f"✅ 通过 ({score}/10)" if is_valid else f"❌ 未通过 ({score}/10)"
        
        md += f"""
**验证结果：** {status_emoji}

**评估理由：**
{validator.get('reasoning', 'N/A')}

"""
        
        if validator.get('feedback'):
            md += f"""
**详细反馈：**
{validator['feedback']}

"""
    else:
        md += "_未验证_\n\n"
    
    md += """</div>
"""
    
    return md


def synthesis_workflow_generator(
    document_text: str,
    uploaded_file,
    task_type: str,
    max_iterations: int,
    temperature: float,
    score_threshold: float,
    proposer_system_prompt: str,
    proposer_user_first_prompt: str,
    proposer_user_iterative_prompt: str,
    solver_system_prompt: str,
    solver_user_prompt: str,
    validator_system_prompt: str,
    validator_user_prompt: str,
):
    """
    Run the data synthesis workflow with real-time updates.
    
    Yields status updates for each iteration.
    
    Args:
        document_text: Text input from user
        uploaded_file: Uploaded file
        task_type: Selected task type
        max_iterations: Maximum iterations
        temperature: Temperature for LLM generation
        score_threshold: Minimum score to accept QA pair
        proposer_system_prompt: Proposer system prompt
        proposer_user_first_prompt: Proposer user first prompt
        proposer_user_iterative_prompt: Proposer user iterative prompt
        solver_system_prompt: Solver system prompt
        solver_user_prompt: Solver user prompt
        validator_system_prompt: Validator system prompt
        validator_user_prompt: Validator user prompt
    
    Yields:
        Tuple of (status, iteration_display, results_display, download_file)
    """
    try:
        # Get document content
        if uploaded_file is not None:
            document = read_document_file(uploaded_file.name)
            logger.info("Using uploaded file")
        elif document_text.strip():
            document = document_text.strip()
            logger.info("Using text input")
        else:
            yield (
                "❌ 错误：请输入文档内容或上传文件",
                "",
                "",
                None
            )
            return
        
        # Validate input
        if len(document) < 10:
            yield (
                "❌ 错误：文档内容过短（至少10个字符）",
                "",
                "",
                None
            )
            return
        
        # Create synthesis request
        logger.info("Starting synthesis - Task: {}, Iterations: {}", task_type, max_iterations)
        
        # Update prompts in PROMPTS dict temporarily for this run
        original_prompts = {
            "proposer": PROMPTS["proposer"].copy(),
            "solver": PROMPTS["solver"].copy(),
            "validator": PROMPTS["validator"].copy(),
        }
        
        PROMPTS["proposer"]["system"] = proposer_system_prompt
        PROMPTS["proposer"]["user_first"] = proposer_user_first_prompt
        PROMPTS["proposer"]["user_iterative"] = proposer_user_iterative_prompt
        PROMPTS["solver"]["system"] = solver_system_prompt
        PROMPTS["solver"]["user"] = solver_user_prompt
        PROMPTS["validator"]["system"] = validator_system_prompt
        PROMPTS["validator"]["user"] = validator_user_prompt
        
        # Update settings temporarily
        original_temp = settings.temperature
        original_threshold = settings.score_threshold
        settings.temperature = temperature
        settings.score_threshold = score_threshold
        
        # Reset stop flag at the start
        stop_flag["should_stop"] = False
        
        # Initial yield
        yield (
            "🚀 正在启动数据合成流程...",
            "",
            "",
            None
        )
        
        # Initialize state
        state = {
            "document": document,
            "task_type": task_type,
            "max_iterations": max_iterations,
            "current_iteration": 0,
            "history_buffer": [],
            "valid_pairs": [],
            "failed_attempts": 0,
            "is_complete": False,
            "iteration_details": [],
            "score_threshold": score_threshold,
        }
        
        # Create graph
        graph = DataSynthesisGraph()
        start_time = time.time()
        
        # Use LangGraph's stream API to get real-time updates
        try:
            current_iteration = 0
            current_status_log = ""
            
            # Stream the graph execution
            for output in graph.stream(state):
                # Check stop flag
                if stop_flag["should_stop"]:
                    logger.warning("User requested stop. Terminating synthesis...")
                    state["is_complete"] = True
                    yield (
                        f"⚠️ **用户手动停止**\n\n已生成 {len(state.get('valid_pairs', []))} 个有效问答对",
                        "",
                        "",
                        None
                    )
                    break
                
                # output is a dict with node name as key
                for node_name, node_state in output.items():
                    # Update state
                    state = node_state
                    
                    # Get current iteration info
                    iteration_details = state.get("iteration_details", [])
                    valid_pairs = state.get("valid_pairs", [])
                    failed_attempts = state.get("failed_attempts", 0)
                    current_iter = state.get("current_iteration", 0)
                    elapsed_time = time.time() - start_time
                    
                    # Add real-time log messages
                    if node_name == "propose":
                        current_iteration = current_iter + 1
                        current_status_log += f"\n<small>🔄 **第 {current_iteration} 轮迭代**</small>\n"
                        current_status_log += f"<small>📝 [Proposer] 正在生成问题...</small>\n"
                        
                    elif node_name == "solve":
                        current_status_log += f"<small>🔍 [Solver] 正在求解问题...</small>\n"
                        
                    elif node_name == "validate":
                        current_status_log += f"<small>✅ [Validator] 正在验证答案...</small>\n"
                        
                    elif node_name == "update":
                        # Check if validation passed
                        if iteration_details and len(iteration_details) > 0:
                            last_detail = iteration_details[-1]
                            if last_detail.get("is_valid"):
                                current_status_log += f"<small>✅ 验证通过！已添加到有效问答对</small>\n"
                            else:
                                current_status_log += f"<small>❌ 验证未通过，继续下一轮</small>\n"
                        current_status_log += f"<small>---</small>\n"
                    
                    # Format iteration display
                    iteration_display = ""
                    for detail in iteration_details:
                        iteration_display += format_iteration_detail(detail, detail["iteration"])
                    
                    # Format main status with progress and log
                    status = (
                        f"**进度:** {current_iter} / {max_iterations} 迭代\n\n"
                        f"**有效问答对:** {len(valid_pairs)}\n"
                        f"**验证失败:** {failed_attempts}\n"
                        f"**执行时间:** {elapsed_time:.1f} 秒\n\n"
                        f"### 📋 实时日志\n\n"
                        f"{current_status_log}"
                    )
                    
                    # Format results
                    results_display = ""
                    if valid_pairs:
                        results_display = "## ✅ 通过验证的问答对\n\n"
                        for i, qa in enumerate(valid_pairs, 1):
                            results_display += format_qa_for_display(qa, i)
                    
                    # Yield current state after each node
                    yield (
                        status,
                        iteration_display,
                        results_display,
                        None
                    )
            
            # Final results
            valid_pairs = state.get("valid_pairs", [])
            failed_attempts = state.get("failed_attempts", 0)
            total_iterations = state.get("current_iteration", 0)
            execution_time = time.time() - start_time
            
            # Check if stopped early
            if stop_flag["should_stop"]:
                final_status = (
                    "## ⚠️ 数据合成已停止\n\n"
                    f"**已完成迭代:** {total_iterations}\n"
                    f"**有效问答对:** {len(valid_pairs)}\n"
                    f"**验证失败:** {failed_attempts}\n"
                    f"**执行时间:** {execution_time:.2f} 秒\n"
                )
            else:
                # Build final status
                final_status = (
                    "## ✅ 数据合成完成！\n\n"
                    f"**总迭代次数:** {total_iterations}\n"
                    f"**有效问答对:** {len(valid_pairs)}\n"
                    f"**验证失败:** {failed_attempts}\n"
                    f"**执行时间:** {execution_time:.2f} 秒\n"
                )
            
            # Save results
            output_file = None
            if valid_pairs:
                output_file = save_qa_pairs(valid_pairs, task_type)
                final_status += f"\n**结果已保存到:** `{output_file}`"
            else:
                final_status += "\n⚠️ 未生成有效的问答对"
            
            # Format final iteration display
            iteration_details = state.get("iteration_details", [])
            final_iteration_display = ""
            for detail in iteration_details:
                final_iteration_display += format_iteration_detail(detail, detail["iteration"])
            
            # Format final results
            final_results = ""
            if valid_pairs:
                final_results = "## ✅ 最终生成的问答对\n\n"
                for i, qa in enumerate(valid_pairs, 1):
                    final_results += format_qa_for_display(qa, i)
            
            yield (
                final_status,
                final_iteration_display,
                final_results,
                output_file
            )
            
        except Exception as e:
            logger.error("Synthesis failed: {}", str(e))
            yield (
                f"❌ 合成过程出错：{str(e)}",
                "",
                "",
                None
            )
        finally:
            # Restore original prompts and settings
            PROMPTS["proposer"] = original_prompts["proposer"]
            PROMPTS["solver"] = original_prompts["solver"]
            PROMPTS["validator"] = original_prompts["validator"]
            settings.temperature = original_temp
            settings.score_threshold = original_threshold
    
    except Exception as e:
        logger.error("Workflow error: {}", str(e))
        yield (
            f"❌ 错误：{str(e)}",
            "",
            "",
            None
        )


def create_ui():
    """Create and configure Gradio UI."""
    
    with gr.Blocks(
        title="Multi-Agent 数据合成系统",
        theme=gr.themes.Soft(),
        css=r"""
        .main-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .info-box {
            background-color: #f0f7ff;
            border-left: 4px solid #1890ff;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
        }
        .iteration-box {
            max-height: 600px;
            overflow-y: auto;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1rem;
            background-color: #fafafa;
            margin-top: 1rem;
        }
        .iteration-box::-webkit-scrollbar {
            width: 8px;
        }
        .iteration-box::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        .iteration-box::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }
        .iteration-box::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        .proposer-block {
            background: linear-gradient(to right, #fff5f5, #ffffff);
            border-left: 4px solid #ff6b6b;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 6px;
        }
        .solver-block {
            background: linear-gradient(to right, #f0f9ff, #ffffff);
            border-left: 4px solid #4dabf7;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 6px;
        }
        .validator-block {
            background: linear-gradient(to right, #f4fce3, #ffffff);
            border-left: 4px solid #82c91e;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 6px;
        }
        """
    ) as app:
        
        # Header
        gr.Markdown(
            """
            # 🤖 Multi-Agent 数据合成系统
            
            通过多智能体协作生成高质量、高难度的训练数据
            
            <div class="info-box">
            <strong>核心特性：</strong>
            <ul>
            <li>🎯 <strong>Iterative Curriculum：</strong>问题难度递增，生成更具挑战性的数据</li>
            <li>🤝 <strong>三智能体协作：</strong>提议者 → 求解者 → 验证者</li>
            <li>📈 <strong>质量保证：</strong>只保留通过验证的高质量问答对</li>
            <li>🔄 <strong>实时可视化：</strong>查看每次迭代中各Agent的详细输出</li>
            </ul>
            </div>
            """,
            elem_classes=["main-header"]
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 📝 输入配置")
                
                # Document input
                gr.Markdown("### 1. 文档内容")
                document_text = gr.Textbox(
                    label="输入文档内容",
                    placeholder="在此处粘贴您的文档内容...",
                    lines=10,
                    max_lines=20,
                )
                
                uploaded_file = gr.File(
                    label="或上传文档文件 (.txt, .md)",
                    file_types=[".txt", ".md"],
                )
                
                gr.Markdown("### 2. 任务配置")
                
                task_type = gr.Radio(
                    choices=[t.value for t in TaskType],
                    label="任务类型",
                    value=TaskType.LOGICAL_REASONING.value,
                    info="选择要合成的数据类型"
                )
                
                max_iterations = gr.Slider(
                    minimum=1,
                    maximum=20,
                    value=10,
                    step=1,
                    label="最大迭代次数",
                    info="生成问答对的最大尝试次数"
                )
                
                temperature = gr.Slider(
                    minimum=0.0,
                    maximum=2.0,
                    value=settings.temperature,
                    step=0.1,
                    label="Temperature",
                    info="控制生成的随机性，越高越随机"
                )
                
                score_threshold = gr.Slider(
                    minimum=1.0,
                    maximum=10.0,
                    value=settings.score_threshold,
                    step=0.5,
                    label="评分阈值",
                    info="只保留评分达到此阈值的问答对"
                )
                
                # Action buttons
                gr.Markdown("### 3. 执行")
                with gr.Row():
                    start_btn = gr.Button(
                        "🚀 开始合成",
                        variant="primary",
                        size="lg",
                    )
                    stop_btn = gr.Button(
                        "⏹️ 停止",
                        variant="stop",
                        size="lg",
                    )
                    clear_btn = gr.Button(
                        "🔄 清除",
                        variant="secondary",
                    )
            
            with gr.Column(scale=2):
                gr.Markdown("## 📊 执行结果")
                
                # Status display
                status_output = gr.Markdown(
                    label="状态",
                    value="点击\"开始合成\"按钮开始生成数据...",
                )
                
                # Tabs for different views
                with gr.Tabs():
                    with gr.Tab("🔄 实时迭代过程"):
                        iteration_output = gr.Markdown(
                            label="迭代详情",
                            value="等待开始...",
                            elem_classes=["iteration-box"],
                        )
                    
                    with gr.Tab("✅ 通过验证的问答对"):
                        results_output = gr.Markdown(
                            label="生成的问答对",
                            value="等待生成...",
                        )
                    
                    with gr.Tab("⚙️ Prompts 配置"):
                        gr.Markdown("### 配置各Agent的系统提示词和用户提示词")
                        
                        with gr.Accordion("📝 Proposer (提议者)", open=False):
                            proposer_system_prompt = gr.Textbox(
                                label="System Prompt",
                                value=PROMPTS["proposer"]["system"],
                                lines=10,
                                max_lines=20,
                            )
                            proposer_user_first_prompt = gr.Textbox(
                                label="User Prompt (首次)",
                                value=PROMPTS["proposer"]["user_first"],
                                lines=10,
                                max_lines=20,
                            )
                            proposer_user_iterative_prompt = gr.Textbox(
                                label="User Prompt (迭代)",
                                value=PROMPTS["proposer"]["user_iterative"],
                                lines=10,
                                max_lines=20,
                            )
                        
                        with gr.Accordion("🔍 Solver (求解者)", open=False):
                            solver_system_prompt = gr.Textbox(
                                label="System Prompt",
                                value=PROMPTS["solver"]["system"],
                                lines=8,
                                max_lines=20,
                            )
                            solver_user_prompt = gr.Textbox(
                                label="User Prompt",
                                value=PROMPTS["solver"]["user"],
                                lines=8,
                                max_lines=20,
                            )
                        
                        with gr.Accordion("✅ Validator (验证者)", open=False):
                            validator_system_prompt = gr.Textbox(
                                label="System Prompt",
                                value=PROMPTS["validator"]["system"],
                                lines=12,
                                max_lines=25,
                            )
                            validator_user_prompt = gr.Textbox(
                                label="User Prompt",
                                value=PROMPTS["validator"]["user"],
                                lines=10,
                                max_lines=20,
                            )
                
                # Download
                download_file = gr.File(
                    label="下载结果（JSON格式）",
                    interactive=False,
                )
        
        # Footer
        gr.Markdown(
            """
            ---
            ### 💡 使用说明
            
            1. **输入文档：** 粘贴文本或上传文件（支持 .txt, .md）
            2. **选择任务类型：** 根据需求选择数据类型（逻辑推理、数值计算、信息查询、总结摘要）
            3. **设置迭代次数：** 建议 5-15 次，次数越多生成的数据越多但耗时更长
            4. **开始合成：** 系统将自动运行三个智能体协作生成数据
            5. **实时查看：** 
               - **🔄 实时迭代过程** 标签页：查看每次迭代中提议者、求解者、验证者的详细输出
               - **✅ 通过验证的问答对** 标签页：查看最终通过验证的高质量问答对
            6. **下载结果：** 下载 JSON 文件用于训练
            
            ### ⚙️ 三智能体协作流程
            
            每次迭代都会经历以下步骤，您可以在"实时迭代过程"中看到详细输出：
            
            1. **📝 提议者 (Proposer)**：基于文档和历史问答对生成新问题
            2. **🔍 求解者 (Solver)**：尝试回答问题，展示推理步骤
            3. **✅ 验证者 (Validator)**：检查答案质量，决定是否通过
            4. **🔄 更新**：通过则加入历史，继续下一轮（问题更难）
            
            **Iterative Curriculum 机制：** 每轮生成的问题都会参考历史问答对，确保新问题更难、更多样。
            """
        )
        
        # Event handlers
        def stop_synthesis():
            """Stop the current synthesis process."""
            stop_flag["should_stop"] = True
            logger.info("Stop button clicked by user")
            return "⏹️ 正在停止合成..."
        
        start_btn.click(
            fn=synthesis_workflow_generator,
            inputs=[
                document_text,
                uploaded_file,
                task_type,
                max_iterations,
                temperature,
                score_threshold,
                proposer_system_prompt,
                proposer_user_first_prompt,
                proposer_user_iterative_prompt,
                solver_system_prompt,
                solver_user_prompt,
                validator_system_prompt,
                validator_user_prompt,
            ],
            outputs=[
                status_output,
                iteration_output,
                results_output,
                download_file,
            ],
        )
        
        stop_btn.click(
            fn=stop_synthesis,
            inputs=[],
            outputs=[status_output],
        )
        
        clear_btn.click(
            fn=lambda: (
                "", 
                None, 
                TaskType.LOGICAL_REASONING.value, 
                10,
                settings.temperature,
                settings.score_threshold,
                PROMPTS["proposer"]["system"],
                PROMPTS["proposer"]["user_first"],
                PROMPTS["proposer"]["user_iterative"],
                PROMPTS["solver"]["system"],
                PROMPTS["solver"]["user"],
                PROMPTS["validator"]["system"],
                PROMPTS["validator"]["user"],
                "点击\"开始合成\"按钮开始生成数据...", 
                "等待开始...", 
                "等待生成...", 
                None
            ),
            inputs=[],
            outputs=[
                document_text,
                uploaded_file,
                task_type,
                max_iterations,
                temperature,
                score_threshold,
                proposer_system_prompt,
                proposer_user_first_prompt,
                proposer_user_iterative_prompt,
                solver_system_prompt,
                solver_user_prompt,
                validator_system_prompt,
                validator_user_prompt,
                status_output,
                iteration_output,
                results_output,
                download_file,
            ],
        )
    
    return app


if __name__ == "__main__":
    # Configure logging
    logger.add(
        f"{settings.log_dir}/web_ui_{{time}}.log",
        rotation="100 MB",
        retention="7 days",
        level="INFO",
    )
    
    logger.info("Starting Gradio Web UI...")
    
    # Create and launch app
    app = create_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
