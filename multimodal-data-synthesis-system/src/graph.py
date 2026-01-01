"""基于 LangGraph 的工作流图"""

import logging
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from datetime import datetime

from config.settings import settings
from src.models import (
    AgentState, IterationState, QAPair,
    ProposerOutput, ValidationResult
)
from src.agents import (
    MultimodalLLMClient, ProposerAgent,
    SolverAgent, ValidatorAgent
)
from src.utils import setup_logger

# 设置日志
logger = setup_logger("graph", settings.LOG_DIR, settings.LOG_LEVEL)


class MultimodalSynthesisGraph:
    """多模态数据合成工作流图"""
    
    def __init__(self, llm_config=None):
        # 初始化 LLM 客户端
        self.llm_client = MultimodalLLMClient(llm_config)
        
        # 初始化 Agents
        self.proposer = ProposerAgent(self.llm_client)
        self.solver = SolverAgent(self.llm_client)
        self.validator = ValidatorAgent(self.llm_client)
        
        # 构建工作流图
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 工作流"""
        # 创建状态图
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("check_continue", self._check_continue)
        workflow.add_node("propose", self._propose_node)
        workflow.add_node("solve", self._solve_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("update_state", self._update_state_node)
        
        # 设置入口点
        workflow.set_entry_point("check_continue")
        
        # 添加边
        workflow.add_conditional_edges(
            "check_continue",
            self._should_continue,
            {
                "continue": "propose",
                "end": END
            }
        )
        workflow.add_edge("propose", "solve")
        workflow.add_edge("solve", "validate")
        workflow.add_edge("validate", "update_state")
        workflow.add_edge("update_state", "check_continue")
        
        return workflow.compile()
    
    def _check_continue(self, state: AgentState) -> AgentState:
        """检查是否继续迭代"""
        logger.info(f"检查是否继续 - 当前迭代: {state.current_iteration}/{state.task.max_iterations}")
        
        # 初始化当前迭代状态
        if state.current_iteration < state.task.max_iterations:
            state.current_iteration += 1
            state.current_difficulty = min(
                state.task.initial_difficulty + 
                (state.current_iteration - 1) * state.task.difficulty_increment,
                settings.MAX_DIFFICULTY
            )
            
            # 创建新的迭代状态
            state.current_state = IterationState(
                iteration=state.current_iteration,
                difficulty=state.current_difficulty,
                status="pending"
            )
            
            logger.info(f"开始迭代 {state.current_iteration}，难度: {state.current_difficulty:.2f}")
        
        return state
    
    def _should_continue(self, state: AgentState) -> str:
        """判断是否应该继续迭代"""
        if state.is_finished or state.current_iteration > state.task.max_iterations:
            logger.info("迭代完成")
            return "end"
        return "continue"
    
    def _propose_node(self, state: AgentState) -> AgentState:
        """提议者节点"""
        try:
            logger.info(f"[迭代 {state.current_iteration}] 提议者开始工作")
            state.current_state.status = "proposing"
            
            # 调用提议者
            output = self.proposer.propose(
                image_paths=state.image_paths,
                task_type=state.task.task_type,
                difficulty=state.current_difficulty,
                history_qa_pairs=state.history_qa_pairs
            )
            
            state.current_state.proposed_qa = output
            logger.info(f"[迭代 {state.current_iteration}] 提议者完成")
            
        except Exception as e:
            logger.error(f"[迭代 {state.current_iteration}] 提议者失败: {str(e)}")
            state.current_state.status = "failed"
            state.current_state.error = str(e)
        
        return state
    
    def _solve_node(self, state: AgentState) -> AgentState:
        """求解者节点"""
        try:
            logger.info(f"[迭代 {state.current_iteration}] 求解者开始工作")
            state.current_state.status = "solving"
            
            # 调用求解者
            output = self.solver.solve(
                image_paths=state.image_paths,
                question=state.current_state.proposed_qa.question
            )
            
            state.current_state.solved_answer = output.answer
            logger.info(f"[迭代 {state.current_iteration}] 求解者完成")
            
        except Exception as e:
            logger.error(f"[迭代 {state.current_iteration}] 求解者失败: {str(e)}")
            state.current_state.status = "failed"
            state.current_state.error = str(e)
        
        return state
    
    def _validate_node(self, state: AgentState) -> AgentState:
        """验证者节点"""
        try:
            logger.info(f"[迭代 {state.current_iteration}] 验证者开始工作")
            state.current_state.status = "validating"
            
            # 调用验证者
            validation = self.validator.validate(
                image_paths=state.image_paths,
                question=state.current_state.proposed_qa.question,
                reference_answer=state.current_state.proposed_qa.answer,
                predicted_answer=state.current_state.solved_answer
            )
            
            state.current_state.validation = validation
            logger.info(f"[迭代 {state.current_iteration}] 验证者完成")
            
        except Exception as e:
            logger.error(f"[迭代 {state.current_iteration}] 验证者失败: {str(e)}")
            state.current_state.status = "failed"
            state.current_state.error = str(e)
        
        return state
    
    def _update_state_node(self, state: AgentState) -> AgentState:
        """更新状态节点"""
        try:
            # 如果验证通过，添加到历史
            if (state.current_state.validation and 
                state.current_state.validation.is_valid):
                
                qa_pair = QAPair(
                    question=state.current_state.proposed_qa.question,
                    answer=state.current_state.proposed_qa.answer,
                    difficulty=state.current_difficulty,
                    iteration=state.current_iteration
                )
                state.history_qa_pairs.append(qa_pair)
                state.current_state.status = "completed"
                
                logger.info(
                    f"[迭代 {state.current_iteration}] 问答对已添加到历史 "
                    f"(共 {len(state.history_qa_pairs)} 对)"
                )
            else:
                state.current_state.status = "failed"
                logger.info(f"[迭代 {state.current_iteration}] 验证未通过，问答对未添加")
            
            # 添加到所有迭代记录
            state.all_iterations.append(state.current_state)
            
            # 检查是否应该结束
            if state.current_iteration >= state.task.max_iterations:
                state.is_finished = True
                logger.info("达到最大迭代次数，标记为完成")
            
        except Exception as e:
            logger.error(f"[迭代 {state.current_iteration}] 更新状态失败: {str(e)}")
            state.error = str(e)
            state.is_finished = True
        
        return state
    
    def run(self, initial_state: AgentState) -> AgentState:
        """运行工作流"""
        logger.info("=" * 50)
        logger.info("开始多模态数据合成工作流")
        logger.info(f"任务类型: {initial_state.task.task_type}")
        logger.info(f"图片数量: {len(initial_state.image_paths)}")
        logger.info(f"最大迭代次数: {initial_state.task.max_iterations}")
        logger.info("=" * 50)
        
        try:
            # 运行图
            final_state = self.graph.invoke(initial_state)
            
            logger.info("=" * 50)
            logger.info("工作流完成")
            logger.info(f"总迭代次数: {len(final_state.all_iterations)}")
            logger.info(f"有效问答对数量: {len(final_state.history_qa_pairs)}")
            logger.info("=" * 50)
            
            return final_state
        
        except Exception as e:
            logger.error(f"工作流执行失败: {str(e)}")
            raise
