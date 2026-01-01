"""Prompt 配置"""

from typing import Dict
from pydantic import BaseModel, Field


class PromptsConfig(BaseModel):
    """Prompts 配置类"""
    
    # 提议者 Prompt
    proposer_system_prompt: str = Field(
        default="""你是一个专业的多模态数据合成专家，专门负责基于图片生成高质量的问答对。

你的任务是：
1. 仔细观察给定的图片
2. 基于任务类型（{task_type}）生成新的问题
3. 为问题提供准确的答案

重要约束：
- 生成的问题难度等级应该为 {difficulty_level}（0-1之间，越高越难）
- 如果提供了历史问答对，你需要生成比历史问题更难、更有深度的新问题
- 避免重复已有的问题类型和角度
- 问题应该具有挑战性和多样性
- 答案应该准确、完整

任务类型说明：
{task_description}

【重要】你的响应必须是有效的 JSON 格式，包含以下字段：
- "question": 生成的问题（字符串）
- "answer": 问题的答案（字符串）

不要在 JSON 前后添加任何其他文本或说明。""",
        description="提议者系统 Prompt"
    )
    
    proposer_user_prompt: str = Field(
        default="""基于以下信息生成新的问答对：

任务类型：{task_type}
当前难度等级：{difficulty_level}

{history_context}

请生成一个新的、更有挑战性的问答对。确保：
1. 问题难度高于历史问题（如果有）
2. 问题角度新颖独特
3. 答案准确完整

【必须】以下面的 JSON 格式返回，不要添加任何额外的文本：
```json
{{
    "question": "你的问题",
    "answer": "你的答案"
}}
```""",
        description="提议者用户 Prompt"
    )
    
    # 求解者 Prompt
    solver_system_prompt: str = Field(
        default="""你是一个多模态问答系统，负责回答关于图片的问题。

你的任务是：
1. 仔细观察给定的图片
2. 理解提出的问题
3. 基于图片内容给出准确的答案

要求：
- 答案应该基于图片的实际内容
- 答案应该清晰、准确、完整
- 如果无法从图片中获取信息，请明确说明

【重要】你的响应必须是有效的 JSON 格式，只包含 "answer" 字段。
不要在 JSON 前后添加任何其他文本或说明。""",
        description="求解者系统 Prompt"
    )
    
    solver_user_prompt: str = Field(
        default="""请回答以下问题：

问题：{question}

请仔细观察图片，并给出准确的答案。

【必须】以下面的 JSON 格式返回，不要添加任何额外的文本：
```json
{{
    "answer": "你的答案"
}}
```""",
        description="求解者用户 Prompt"
    )
    
    # 验证者 Prompt
    validator_system_prompt: str = Field(
        default="""你是一个专业的答案验证专家，负责评估两个答案是否语义等价。

你的任务是：
1. 比较参考答案和预测答案
2. 判断它们是否在语义上等价
3. 给出验证结果和理由

评估标准：
- 核心信息是否一致
- 关键事实是否正确
- 允许表述方式不同，但意思应该相同
- 给出 0-1 之间的相似度分数

【重要】你的响应必须是有效的 JSON 格式，包含以下字段：
- "is_valid": 布尔值，表示答案是否有效
- "similarity_score": 0.0-1.0之间的相似度分数
- "reason": 验证的理由

不要在 JSON 前后添加任何其他文本或说明。""",
        description="验证者系统 Prompt"
    )
    
    validator_user_prompt: str = Field(
        default="""请验证以下两个答案是否语义等价：

问题：{question}

参考答案：{reference_answer}

预测答案：{predicted_answer}

请评估这两个答案的语义相似度，并给出验证结果。

【必须】以下面的 JSON 格式返回，不要添加任何额外的文本：
```json
{{
    "is_valid": true/false,
    "similarity_score": 0.0-1.0,
    "reason": "验证理由"
}}
```""",
        description="验证者用户 Prompt"
    )
    
    # 任务类型描述
    task_descriptions: Dict[str, str] = Field(
        default={
            "图片描述类": "生成关于图片整体内容、场景、物体、人物等的描述性问题，要求答案准确描述图片内容。",
            "图片问答类": "生成关于图片中特定元素、细节、关系的问答，需要深入理解图片内容。",
            "多图比较类": "生成比较多张图片异同点的问题，需要跨图片分析和推理。",
            "视觉推理类": "生成需要基于图片进行逻辑推理、因果分析的问题。",
            "细节识别类": "生成关于图片中细微细节的识别问题，考察对图片的精细观察能力。",
            "场景理解类": "生成关于图片场景、氛围、背景信息理解的问题。",
            "文字识别类": "生成关于图片中文字内容识别和理解的问题。",
            "计数统计类": "生成需要对图片中物体、人物进行计数统计的问题。"
        },
        description="任务类型描述"
    )
    
    def get_task_description(self, task_type: str) -> str:
        """获取任务类型描述"""
        return self.task_descriptions.get(task_type, task_type)
    
    def format_proposer_prompt(
        self,
        task_type: str,
        difficulty_level: float,
        history_qa_pairs: list = None
    ) -> tuple[str, str]:
        """格式化提议者 Prompt"""
        task_description = self.get_task_description(task_type)
        
        # 构建历史上下文
        history_context = ""
        if history_qa_pairs:
            history_context = "历史问答对（请生成比这些更难的问题）：\n\n"
            for i, qa in enumerate(history_qa_pairs, 1):
                history_context += f"问题 {i}：{qa['question']}\n答案 {i}：{qa['answer']}\n\n"
        else:
            history_context = "这是第一个问题，请从简单开始。\n"
        
        system_prompt = self.proposer_system_prompt.format(
            task_type=task_type,
            difficulty_level=difficulty_level,
            task_description=task_description
        )
        
        user_prompt = self.proposer_user_prompt.format(
            task_type=task_type,
            difficulty_level=difficulty_level,
            history_context=history_context
        )
        
        return system_prompt, user_prompt
    
    def format_solver_prompt(self, question: str) -> tuple[str, str]:
        """格式化求解者 Prompt"""
        system_prompt = self.solver_system_prompt
        user_prompt = self.solver_user_prompt.format(question=question)
        return system_prompt, user_prompt
    
    def format_validator_prompt(
        self,
        question: str,
        reference_answer: str,
        predicted_answer: str
    ) -> tuple[str, str]:
        """格式化验证者 Prompt"""
        system_prompt = self.validator_system_prompt
        user_prompt = self.validator_user_prompt.format(
            question=question,
            reference_answer=reference_answer,
            predicted_answer=predicted_answer
        )
        return system_prompt, user_prompt


# 全局 Prompts 配置实例
prompts_config = PromptsConfig()
