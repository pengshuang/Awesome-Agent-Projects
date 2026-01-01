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


def generate_stats_html(current: int = 0, total: int = 0, success: int = 0, failed: int = 0, rate: float = 0.0, difficulty: float = 1.0, elapsed_time: float = 0.0) -> str:
    """Generate statistics panel HTML."""
    progress = (current / total * 100) if total > 0 else 0
    
    # Format elapsed time
    if elapsed_time < 60:
        time_str = f"{elapsed_time:.1f}秒"
    elif elapsed_time < 3600:
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_str = f"{minutes}分{seconds}秒"
    else:
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        time_str = f"{hours}小时{minutes}分"
    
    # Show spinner if running and not complete
    is_running = current < total and current > 0
    spinner_html = '<span class="spinner">🔄</span> ' if is_running else ''
    
    return f"""
    <div class="stats-container">
        <div class="stats-title">📊 实时统计 <span style="font-size: 0.9rem; font-weight: 400; margin-left: auto;">{spinner_html} 已运行: {time_str}</span></div>
        <div class="progress-section">
            <div class="progress-text">{current}/{total} 轮 ({progress:.0f}%)</div>
            <div class="progress-bar-wrapper">
                <div class="progress-bar-fill" style="width: {progress:.1f}%"></div>
            </div>
        </div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">✅ 成功生成</div>
                <p class="stat-value success">{success}</p>
            </div>
            <div class="stat-card">
                <div class="stat-label">❌ 失败次数</div>
                <p class="stat-value error">{failed}</p>
            </div>
            <div class="stat-card">
                <div class="stat-label">📈 成功率</div>
                <p class="stat-value rate">{rate:.1f}%</p>
            </div>
            <div class="stat-card">
                <div class="stat-label">⭐ 平均难度</div>
                <p class="stat-value difficulty">{difficulty:.1f}/5</p>
            </div>
        </div>
    </div>
    """

# Example documents for quick start
EXAMPLE_DOCUMENTS = {
    "学术报告": """
# 量子计算研究进展报告

## 摘要

量子计算作为下一代计算技术的核心，利用量子力学原理实现超越经典计算机的计算能力。本报告综述了量子计算的基本原理、技术进展以及应用前景。

## 1. 量子计算基本原理

### 1.1 量子比特（Qubit）
与经典计算机使用的比特（0或1）不同，量子比特可以同时处于0和1的叠加态。这种特性使得量子计算机能够并行处理大量信息。

### 1.2 量子纠缠
量子纠缠是两个或多个量子比特之间的特殊关联，即使相距遥远，改变其中一个量子比特的状态也会瞬间影响另一个。这种特性为量子通信和量子计算提供了基础。

### 1.3 量子门操作
量子门是量子计算的基本操作单元，类似于经典计算机中的逻辑门。常见的量子门包括：Hadamard门、CNOT门、Pauli门等。

## 2. 技术进展

### 2.1 硬件平台
- **超导量子比特**：IBM、Google等公司采用的主流技术路线
- **离子阱**：IonQ等公司使用的高精度平台
- **光量子**：中国科学技术大学的"九章"量子计算机
- **拓扑量子比特**：微软研究的容错性更强的方案

### 2.2 里程碑事件
- 2019年：Google宣布实现"量子优越性"，用53个量子比特在200秒内完成经典超级计算机需要1万年的计算
- 2021年：中国"祖冲之号"量子计算机实现66个量子比特
- 2023年：IBM推出433量子比特的Osprey处理器

## 3. 应用前景

### 3.1 密码学
量子计算机能够破解现有的RSA等加密算法，同时也催生了量子密钥分发（QKD）等新型加密技术。

### 3.2 药物研发
量子计算可以模拟分子和化学反应，加速新药研发过程，降低研发成本。

### 3.3 优化问题
在物流调度、金融投资组合、交通规划等领域，量子计算能够快速找到最优解决方案。

### 3.4 人工智能
量子机器学习结合量子计算和机器学习算法，有望实现更强大的AI系统。

## 4. 挑战与展望

当前量子计算仍面临诸多挑战：
- 量子比特的相干时间短，易受环境干扰
- 量子纠错技术尚未成熟
- 大规模量子计算机的工程实现困难
- 量子算法的开发还处于早期阶段

尽管如此，随着技术的不断进步，预计在未来10-20年内，量子计算将在特定领域展现出实用价值，并最终改变我们的计算范式。
""",
    "理科试题": """
# 高中物理试题集

## 第一题：牛顿运动定律

一个质量为2kg的物体放在光滑的水平面上，受到一个水平向右、大小为10N的恒力作用。求：

1. 物体的加速度
2. 从静止开始，3秒后物体的速度
3. 3秒内物体的位移

**解析：**
根据牛顿第二定律 F = ma
1. 加速度 a = F/m = 10N/2kg = 5m/s²
2. 速度 v = v₀ + at = 0 + 5×3 = 15m/s
3. 位移 s = v₀t + ½at² = 0 + ½×5×3² = 22.5m

## 第二题：圆周运动

一个小球用长为0.5m的细绳悬挂，在竖直平面内做圆周运动。小球通过最高点时的最小速度是多少？（g取10m/s²）

**解析：**
小球在最高点时，重力提供向心力的临界条件：
mg = mv²/r
v = √(gr) = √(10×0.5) = √5 ≈ 2.24m/s

## 第三题：动量守恒

在光滑水平面上，质量为3kg的物体A以6m/s的速度向右运动，与静止的质量为2kg的物体B发生正碰。碰后A的速度变为2m/s，方向仍向右。求碰后B的速度。

**解析：**
根据动量守恒定律：
m₁v₁ + m₂v₂ = m₁v₁' + m₂v₂'
3×6 + 2×0 = 3×2 + 2×v₂'
18 = 6 + 2v₂'
v₂' = 6m/s（向右）

## 第四题：电磁感应

一个矩形线圈，面积为0.2m²，有100匝，放在磁感应强度为0.5T的匀强磁场中。线圈平面与磁场方向垂直。若在0.1s内将线圈从磁场中匀速抽出，求：

1. 磁通量的变化
2. 感应电动势的平均值

**解析：**
1. 磁通量变化 ΔΦ = BS = 0.5×0.2 = 0.1Wb
2. 感应电动势 ε = nΔΦ/Δt = 100×0.1/0.1 = 100V

## 第五题：光的干涉

在双缝干涉实验中，两缝间距为0.5mm，屏幕距双缝2m，使用波长为500nm的单色光。求相邻亮条纹之间的距离。

**解析：**
条纹间距 Δx = λL/d
= (500×10⁻⁹×2)/(0.5×10⁻³)
= 2×10⁻³m = 2mm
""",
    "时事新闻": """
# 科技新闻快报

## 人工智能领域重大突破

**发布时间：2024年1月15日**

### OpenAI发布GPT-5，多模态能力再升级

本周一，OpenAI正式发布了最新一代大语言模型GPT-5。据官方介绍，GPT-5在理解能力、推理能力和创造力方面都有显著提升，并且首次实现了真正的多模态统一处理。

**主要特性：**
- 参数规模达到10万亿，是GPT-4的20倍
- 支持文本、图像、音频、视频的统一输入输出
- 推理能力大幅提升，在数学和科学问题上的准确率超过95%
- 支持更长的上下文窗口，达到100万token
- 推理速度提升3倍，成本降低50%

业内专家认为，GPT-5的发布标志着人工智能进入了新的发展阶段，将对教育、医疗、科研等领域产生深远影响。

### 量子计算商业化加速

IBM宣布其量子计算云服务已向全球100多家企业客户开放。这些客户来自金融、制药、材料科学等行业，正在利用量子计算解决复杂的优化和模拟问题。

IBM量子计算副总裁表示："我们正在见证量子计算从实验室走向实际应用的历史性转变。虽然通用量子计算机还需要时间，但在特定领域，量子优势已经开始显现。"

### 新能源汽车销量创新高

根据中国汽车工业协会发布的数据，2023年中国新能源汽车销量达到950万辆，同比增长37.9%，渗透率达到31.6%。

**市场亮点：**
- 比亚迪年销量突破300万辆，成为全球新能源汽车销量冠军
- 理想汽车首次实现年度盈利
- 小鹏汽车推出飞行汽车概念产品
- 特斯拉在上海工厂启动新一轮产能扩张

分析师预测，2024年中国新能源汽车销量将突破1200万辆，渗透率有望达到40%。

### 脑机接口技术获重大进展

Neuralink公司宣布，其脑机接口设备已成功帮助一名瘫痪患者恢复了部分运动能力。这是该技术首次在人体试验中取得实质性成功。

患者通过思维控制机械臂完成了喝水、写字等日常动作。马斯克表示，这一突破为数百万残障人士带来了希望，未来脑机接口技术还将用于治疗阿尔茨海默症、帕金森病等神经系统疾病。

### 可控核聚变实现净能量输出

美国国家点火装置(NIF)再次成功实现核聚变净能量输出，输出能量是输入能量的1.5倍。这是继去年首次突破后的又一重要里程碑。

科学家们表示，可控核聚变有望在2030年代实现商业化应用，届时将提供清洁、安全、几乎无限的能源，彻底解决人类能源危机。

## 评论

本周的科技新闻显示，人工智能、量子计算、新能源、脑机接口、核聚变等前沿技术都在快速发展，正在重塑人类社会的方方面面。我们正处在一个技术爆炸的时代，未来十年将见证更多令人惊叹的突破。
""",
    "文学小说": """
# 《时光邮差》（节选）

## 第一章：神秘的信件

林晓站在邮局门口，手里握着一封泛黄的信。信封上的邮戳显示：2045年3月15日。

"这不可能。"她喃喃自语。今天是2025年3月15日，整整早了二十年。

信封上的地址正是她现在的住址，收件人写着她的名字：林晓。字迹潦草但清晰，就像是她自己的笔迹。

她犹豫了一下，撕开信封。里面是一张折叠的信纸，展开后，她看到了这样的内容：

---

*亲爱的林晓：*

*如果你收到这封信，说明时间邮局的实验成功了。我是二十年后的你。*

*不要惊慌，我知道你现在一定满脑子疑问。时间邮局是2043年才被发明的，它可以把信件送到过去的任何时间点。我冒着改变时间线的风险给你写这封信，是因为有些事情你必须知道。*

*三天后，也就是3月18日，你会收到清华大学的录取通知书。你会很高兴，因为这是你从小的梦想。但我要告诉你，千万不要去北京。*

*我知道这很难理解，但请相信我。如果你去了北京，你会遇到一个人，一个改变你一生的人。你们会相爱，会结婚，会生活在一起十五年。但在2040年的冬天，他会离开你，留下一片废墟。*

*我写这封信不是为了改变历史，而是为了拯救你。选择复旦大学吧，那里有另一种人生在等你。*

*不要试图回复这封信，时间邮局只能单向传递。相信我，相信你自己。*

*二十年后的你*
*2045年3月15日*

---

林晓的手在颤抖。她重新读了一遍，又读了一遍。这是恶作剧吗？还是某种精心策划的骗局？

但那笔迹，那语气，甚至是一些只有她自己知道的小细节，都让她不得不相信，这封信真的是她写的。

她抬起头，看向街道对面的咖啡馆。透过玻璃窗，她看到一个年轻男子正在看书。阳光洒在他的侧脸上，有种说不出的温柔。

"他就是那个人吗？"林晓想。"那个会让我爱上，然后又让我心碎的人？"

手机响了。是她妈妈打来的："晓晓，快递来了，好像是大学的录取通知书！"

林晓看了看手里的信，又看了看咖啡馆里的男子。她深吸一口气，做出了一个决定。

她转身走向邮局，从包里拿出一张白纸和一支笔，开始给二十年后的自己写信。

---

*亲爱的林晓：*

*谢谢你的来信，但我不会听你的建议。*

*也许你经历了痛苦，也许你后悔了。但那十五年的爱情，那些幸福的时光，难道不值得吗？*

*如果爱注定会结束，那我宁愿选择爱过，也不愿意留下"如果"的遗憾。*

*人生不是一道选择题，而是一段旅程。我不知道未来会怎样，但我知道，如果我因为害怕失去而放弃拥有，那才是真正的遗憾。*

*谢谢你想保护我，但请让我自己选择。*

*二十年前的你*
*2025年3月15日*

---

她把信装进信封，写上地址：2045年3月15日，林晓收。

邮局的老人接过信，看了一眼邮戳时间，笑了："姑娘，时间邮局要到2043年才会开张呢。"

林晓也笑了："我知道，但说不定未来会有奇迹发生呢？"

她走出邮局，穿过街道，推开了咖啡馆的门。

"你好，这个位置有人吗？"

年轻男子抬起头，微笑着说："请坐。"

阳光透过窗户洒进来，林晓觉得，这一刻，未来已经不重要了。重要的是现在，是此刻的选择。

（未完待续）
"""
}


def format_iteration_detail(detail: dict, iteration: int) -> str:
    """Format iteration detail for display."""
    md = f"""
---
## 迭代 {iteration}

### 📝 提议者 (Proposer)

"""
    
    if detail.get("proposer_output"):
        prop = detail["proposer_output"]
        md += f"""
**生成的问题：** {prop.get('question', 'N/A')}

**参考答案：** {prop.get('answer', 'N/A')}

**生成理由：** {prop.get('reasoning', 'N/A')}

"""
    else:
        md += "_未生成_\n\n"
    
    md += """
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
        
        md += f"""
**最终答案：** {solver.get('final_answer', 'N/A')}

"""
    else:
        md += "_未生成_\n\n"
    
    md += """
### ✅ 验证者 (Validator)

"""
    
    if detail.get("validator_output"):
        validator = detail["validator_output"]
        score = validator.get("score", 0)
        is_valid = validator.get("is_valid", False)
        status_emoji = f"✅ 通过 ({score}/10)" if is_valid else f"❌ 未通过 ({score}/10)"
        
        md += f"""
**验证结果：** {status_emoji}

**评估理由：** {validator.get('reasoning', 'N/A')}

"""
        
        if validator.get('feedback'):
            md += f"""
**详细反馈：** {validator['feedback']}

"""
    else:
        md += "_未验证_\n\n"
    
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
            yield (generate_stats_html(), "", "", None)
            return
        
        # Validate input
        if len(document) < 10:
            yield (generate_stats_html(), "", "", None)
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
            generate_stats_html(),
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
            
            # Stream the graph execution
            for output in graph.stream(state):
                # Check stop flag
                if stop_flag["should_stop"]:
                    logger.warning("User requested stop. Terminating synthesis...")
                    state["is_complete"] = True
                    valid_pairs_count = len(state.get('valid_pairs', []))
                    failed_count = state.get('failed_attempts', 0)
                    current_iter = state.get('current_iteration', 0)
                    success_rate = (valid_pairs_count / current_iter * 100) if current_iter > 0 else 0.0
                    elapsed = time.time() - start_time
                    yield (
                        generate_stats_html(current_iter, max_iterations, valid_pairs_count, failed_count, success_rate, 1.0, elapsed),
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
                    
                    # Format iteration display
                    iteration_display = ""
                    for detail in iteration_details:
                        iteration_display += format_iteration_detail(detail, detail["iteration"])
                    
                    # Calculate statistics
                    progress = current_iter / max_iterations if max_iterations > 0 else 0
                    success_count = len(valid_pairs)
                    success_rate = (success_count / current_iter * 100) if current_iter > 0 else 0.0
                    
                    # Calculate average difficulty (based on iteration number of successful pairs)
                    avg_difficulty = 1.0
                    if valid_pairs:
                        difficulty_scores = []
                        for qa in valid_pairs:
                            # Estimate difficulty based on when it was generated
                            # Later iterations = higher difficulty
                            iteration_num = qa.get('metadata', {}).get('iteration', 1)
                            difficulty = min(iteration_num / 2, 5.0)  # Scale to 1-5
                            difficulty_scores.append(difficulty)
                        avg_difficulty = sum(difficulty_scores) / len(difficulty_scores)
                    
                    # Format results
                    results_display = ""
                    if valid_pairs:
                        for i, qa in enumerate(valid_pairs, 1):
                            results_display += format_qa_for_display(qa, i)
                    
                    # Yield current state after each node
                    yield (
                        generate_stats_html(current_iter, max_iterations, success_count, failed_attempts, success_rate, avg_difficulty, elapsed_time),
                        iteration_display,
                        results_display,
                        None
                    )
            
            # Final results
            valid_pairs = state.get("valid_pairs", [])
            failed_attempts = state.get("failed_attempts", 0)
            total_iterations = state.get("current_iteration", 0)
            execution_time = time.time() - start_time
            
            # Save results
            output_file = None
            if valid_pairs:
                output_file = save_qa_pairs(valid_pairs, task_type)
            
            # Format final iteration display
            iteration_details = state.get("iteration_details", [])
            final_iteration_display = ""
            for detail in iteration_details:
                final_iteration_display += format_iteration_detail(detail, detail["iteration"])
            
            # Format final results
            final_results = ""
            if valid_pairs:
                for i, qa in enumerate(valid_pairs, 1):
                    final_results += format_qa_for_display(qa, i)
            
            # Calculate final statistics
            final_progress = 1.0 if not stop_flag["should_stop"] else (total_iterations / max_iterations)
            final_success_rate = (len(valid_pairs) / total_iterations * 100) if total_iterations > 0 else 0.0
            final_avg_difficulty = 1.0
            if valid_pairs:
                difficulty_scores = []
                for qa in valid_pairs:
                    iteration_num = qa.get('metadata', {}).get('iteration', 1)
                    difficulty = min(iteration_num / 2, 5.0)
                    difficulty_scores.append(difficulty)
                final_avg_difficulty = sum(difficulty_scores) / len(difficulty_scores)
            
            yield (
                generate_stats_html(total_iterations, max_iterations, len(valid_pairs), failed_attempts, final_success_rate, final_avg_difficulty, execution_time),
                final_iteration_display,
                final_results,
                output_file
            )
            
        except Exception as e:
            logger.error("Synthesis failed: {}", str(e))
            yield (
                generate_stats_html(0, 0, 0, 0, 0.0, 1.0),
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
            0.0,
            '<div class="progress-text">0/0 转 (0%)</div>',
            '<p class="stat-value success">0</p>',
            '<p class="stat-value error">0</p>',
            '<p class="stat-value rate">0.0%</p>',
            '<p class="stat-value difficulty">1.0/5</p>',
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
        .stats-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 8px 16px rgba(102, 126, 234, 0.2);
        }
        .stats-title {
            color: white;
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            letter-spacing: 0.5px;
        }
        .spinner {
            display: inline-block;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.75rem;
            margin-top: 0.75rem;
        }
        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            padding: 0.875rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        }
        .stat-label {
            font-size: 0.75rem;
            color: #6b7280;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            margin: 0;
            font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
        }
        .stat-value.success {
            color: #10b981;
        }
        .stat-value.error {
            color: #ef4444;
        }
        .stat-value.rate {
            color: #3b82f6;
        }
        .stat-value.difficulty {
            color: #f97316;
        }
        .progress-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            padding: 0.875rem;
            margin-bottom: 0.75rem;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        .progress-text {
            color: #667eea;
            font-size: 0.95rem;
            font-weight: 600;
            text-align: right;
            margin-bottom: 0.5rem;
            font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
        }
        .progress-bar-wrapper {
            width: 100%;
            height: 8px;
            background: rgba(102, 126, 234, 0.15);
            border-radius: 10px;
            overflow: hidden;
        }
        .progress-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            border-radius: 10px;
            transition: width 0.5s ease;
            box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
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
        .qa-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            margin-bottom: 1rem;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        .qa-card:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        .qa-card[open] {
            border-color: #667eea;
        }
        .qa-summary {
            background: linear-gradient(to right, #f9fafb, #ffffff);
            padding: 1rem 1.25rem;
            cursor: pointer;
            list-style: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 500;
            transition: background 0.2s ease;
            user-select: none;
        }
        .qa-summary::-webkit-details-marker {
            display: none;
        }
        .qa-summary::before {
            content: '▶';
            display: inline-block;
            margin-right: 0.75rem;
            transition: transform 0.3s ease;
            color: #667eea;
            font-size: 0.8rem;
        }
        .qa-card[open] .qa-summary::before {
            transform: rotate(90deg);
        }
        .qa-summary:hover {
            background: linear-gradient(to right, #f3f4f6, #fafafa);
        }
        .qa-number {
            font-size: 1rem;
            color: #1f2937;
            font-weight: 600;
        }
        .qa-meta {
            font-size: 0.875rem;
            color: #6b7280;
            font-weight: 400;
        }
        .qa-content {
            padding: 1.25rem;
            border-top: 1px solid #f3f4f6;
            background: #fafafa;
            animation: slideDown 0.3s ease;
        }
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        /* Prompt textbox scrollbar styling */
        .prompt-config textarea {
            overflow-y: auto !important;
            scrollbar-width: thin;
            scrollbar-color: #888 #f1f1f1;
        }
        .prompt-config textarea::-webkit-scrollbar {
            width: 10px;
        }
        .prompt-config textarea::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 5px;
        }
        .prompt-config textarea::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 5px;
        }
        .prompt-config textarea::-webkit-scrollbar-thumb:hover {
            background: #555;
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
                
                # Example document buttons
                gr.Markdown("**💡 快速开始 - 选择示例文档：**")
                with gr.Row():
                    example_btn_1 = gr.Button("🎓 学术报告", size="sm")
                    example_btn_2 = gr.Button("🔢 理科试题", size="sm")
                with gr.Row():
                    example_btn_3 = gr.Button("📰 时事新闻", size="sm")
                    example_btn_4 = gr.Button("📖 文学小说", size="sm")
                
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
                    maximum=100,
                    value=10,
                    step=1,
                    label="最大迭代次数",
                    info="生成问答对的最大尝试次数（建议10-50次）"
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
                
                # Real-time Statistics Panel
                with gr.Group():
                    stats_panel = gr.HTML(
                        value=generate_stats_html()
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
                            elem_classes=["iteration-box"],
                        )
                    
                    with gr.Tab("⚙️ Prompts 配置"):
                        gr.Markdown("### 配置各Agent的系统提示词和用户提示词")
                        
                        with gr.Accordion("📝 Proposer (提议者)", open=False):
                            proposer_system_prompt = gr.Textbox(
                                label="System Prompt",
                                value=PROMPTS["proposer"]["system"],
                                lines=10,
                                max_lines=20,
                                elem_classes=["prompt-config"],
                            )
                            proposer_user_first_prompt = gr.Textbox(
                                label="User Prompt (首次)",
                                value=PROMPTS["proposer"]["user_first"],
                                lines=10,
                                max_lines=20,
                                elem_classes=["prompt-config"],
                            )
                            proposer_user_iterative_prompt = gr.Textbox(
                                label="User Prompt (迭代)",
                                value=PROMPTS["proposer"]["user_iterative"],
                                lines=10,
                                max_lines=20,
                                elem_classes=["prompt-config"],
                            )
                        
                        with gr.Accordion("🔍 Solver (求解者)", open=False):
                            solver_system_prompt = gr.Textbox(
                                label="System Prompt",
                                value=PROMPTS["solver"]["system"],
                                lines=8,
                                max_lines=20,
                                elem_classes=["prompt-config"],
                            )
                            solver_user_prompt = gr.Textbox(
                                label="User Prompt",
                                value=PROMPTS["solver"]["user"],
                                lines=8,
                                max_lines=20,
                                elem_classes=["prompt-config"],
                            )
                        
                        with gr.Accordion("✅ Validator (验证者)", open=False):
                            validator_system_prompt = gr.Textbox(
                                label="System Prompt",
                                value=PROMPTS["validator"]["system"],
                                lines=12,
                                max_lines=25,
                                elem_classes=["prompt-config"],
                            )
                            validator_user_prompt = gr.Textbox(
                                label="User Prompt",
                                value=PROMPTS["validator"]["user"],
                                lines=10,
                                max_lines=20,
                                elem_classes=["prompt-config"],
                            )
                    
                    with gr.Tab("📥 下载结果"):
                        gr.Markdown("### 数据合成结果下载")
                        gr.Markdown("完成数据合成后，可以在这里下载生成的JSON格式文件")
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
        
        def load_example(example_name: str):
            """Load example document."""
            return EXAMPLE_DOCUMENTS[example_name]
        
        # Example button click handlers
        example_btn_1.click(
            fn=lambda: load_example("学术报告"),
            inputs=[],
            outputs=[document_text],
        )
        
        example_btn_2.click(
            fn=lambda: load_example("理科试题"),
            inputs=[],
            outputs=[document_text],
        )
        
        example_btn_3.click(
            fn=lambda: load_example("时事新闻"),
            inputs=[],
            outputs=[document_text],
        )
        
        example_btn_4.click(
            fn=lambda: load_example("文学小说"),
            inputs=[],
            outputs=[document_text],
        )
        
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
                stats_panel,
                iteration_output,
                results_output,
                download_file,
            ],
        )
        
        stop_btn.click(
            fn=stop_synthesis,
            inputs=[],
            outputs=[],
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
                generate_stats_html(),
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
                stats_panel,
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
