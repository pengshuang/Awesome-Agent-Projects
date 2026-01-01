"""英语学习智能Agent"""

from typing import List, Dict, Optional, Generator
from datetime import datetime
from config.prompts import PROMPTS
from config.settings import settings
from src.api.llm_client import llm_client
from src.utils.logger import app_logger
from src.utils.storage import storage


class EnglishLearningAgent:
    """英语学习智能Agent
    
    功能：
    1. 自主规划学习内容
    2. 主动引导对话练习
    3. 实时纠错和反馈
    4. 复盘总结薄弱项
    5. 自适应调整难度
    6. 保持上下文记忆
    """
    
    def __init__(self, user_id: str = "default", difficulty: str = "中级"):
        """初始化Agent
        
        Args:
            user_id: 用户ID
            difficulty: 学习难度（初级/中级/高级）
        """
        self.user_id = user_id
        self.difficulty = difficulty
        self.llm = llm_client
        
        # 对话历史
        self.chat_history: List[Dict[str, str]] = []
        
        # 学生档案
        self.student_profile = {
            "level": difficulty,
            "weak_points": [],  # 薄弱项
            "strong_points": [],  # 优势项
            "practice_count": 0,  # 练习次数
            "error_patterns": {},  # 错误模式
        }
        
        # 会话ID
        self.session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 加载历史档案
        self._load_profile()
        
        app_logger.info(f"英语学习Agent初始化: 用户={user_id}, 难度={difficulty}")
    
    def chat(
        self,
        user_message: str,
        stream: bool = True
    ) -> Generator[str, None, None]:
        """与Agent对话（流式输出）
        
        Args:
            user_message: 用户消息
            stream: 是否流式输出
            
        Yields:
            生成的回复内容
        """
        try:
            # 添加用户消息到历史
            self.chat_history.append({
                "role": "user",
                "content": user_message
            })
            
            # 构建完整消息列表
            messages = self._build_messages()
            
            # 调用LLM
            assistant_reply = ""
            for chunk in self.llm.chat(messages, stream=stream):
                assistant_reply += chunk
                yield chunk
            
            # 保存助手回复
            self.chat_history.append({
                "role": "assistant",
                "content": assistant_reply
            })
            
            # 更新学生档案
            self._update_profile(user_message, assistant_reply)
            
            # 保存对话历史
            self._save_history()
            
        except Exception as e:
            error_msg = f"❌ 对话失败: {str(e)}"
            app_logger.error(error_msg)
            yield error_msg
    
    def chat_complete(self, user_message: str) -> str:
        """与Agent对话（完整输出）
        
        Args:
            user_message: 用户消息
            
        Returns:
            完整回复
        """
        result = ""
        for chunk in self.chat(user_message, stream=False):
            result += chunk
        return result
    
    def _build_messages(self) -> List[Dict[str, str]]:
        """构建发送给LLM的消息列表"""
        messages = []
        
        # 系统提示词
        level_descriptions = {
            "初级": "学生处于英语初级水平，需要从基础词汇和简单句型开始学习。",
            "中级": "学生具备一定英语基础，能进行日常对话，需要提升词汇量和语法准确性。",
            "高级": "学生英语水平较高，需要提升高级表达能力和专业领域词汇。"
        }
        
        system_prompt = PROMPTS.AGENT_SYSTEM_PROMPT.format(
            difficulty=self.difficulty,
            level_description=level_descriptions.get(self.difficulty, "")
        )
        
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # 如果有历史对话，添加引导提示
        if len(self.chat_history) > 2:
            chat_summary = self._summarize_chat_history()
            weak_points = ", ".join(self.student_profile["weak_points"][-5:]) or "暂无"
            
            context_prompt = PROMPTS.AGENT_CHAT_PROMPT.format(
                chat_history=chat_summary,
                weak_points=weak_points
            )
            
            messages.append({
                "role": "system",
                "content": context_prompt
            })
        
        # 添加最近的对话历史（保留最近10轮）
        recent_history = self.chat_history[-20:]  # 最近10轮（每轮2条消息）
        messages.extend(recent_history)
        
        return messages
    
    def _summarize_chat_history(self) -> str:
        """总结对话历史（避免上下文过长）"""
        if len(self.chat_history) <= 4:
            summary = ""
            for msg in self.chat_history[:-1]:  # 排除最新的用户消息
                role = "学生" if msg["role"] == "user" else "导师"
                summary += f"{role}: {msg['content'][:100]}...\n"
            return summary
        else:
            # 只保留最近几轮的简要总结
            summary = "之前的对话内容：\n"
            for msg in self.chat_history[-8:-1]:
                role = "学生" if msg["role"] == "user" else "导师"
                summary += f"{role}: {msg['content'][:80]}...\n"
            return summary
    
    def _update_profile(self, user_message: str, assistant_reply: str):
        """更新学生档案"""
        try:
            self.student_profile["practice_count"] += 1
            
            # 简单分析：检测关键词识别薄弱项
            # （实际项目中可以用更复杂的NLP分析）
            error_keywords = ["错误", "纠正", "应该", "不对", "改正"]
            if any(keyword in assistant_reply for keyword in error_keywords):
                # 提取可能的薄弱项
                if "语法" in assistant_reply:
                    self._add_weak_point("语法")
                if "发音" in assistant_reply:
                    self._add_weak_point("发音")
                if "词汇" in assistant_reply:
                    self._add_weak_point("词汇")
        
        except Exception as e:
            app_logger.warning(f"更新档案失败: {str(e)}")
    
    def _add_weak_point(self, point: str):
        """添加薄弱项"""
        if point not in self.student_profile["weak_points"]:
            self.student_profile["weak_points"].append(point)
            # 只保留最近10个
            if len(self.student_profile["weak_points"]) > 10:
                self.student_profile["weak_points"] = self.student_profile["weak_points"][-10:]
    
    def generate_summary(self) -> str:
        """生成学习总结报告"""
        try:
            duration = len(self.chat_history) // 2  # 对话轮数
            practice_count = self.student_profile["practice_count"]
            
            # 提取主要学习内容
            content_keywords = []
            for msg in self.chat_history[::2]:  # 只看用户消息
                if msg["role"] == "user":
                    content_keywords.append(msg["content"][:50])
            
            content_summary = "; ".join(content_keywords[:5])
            errors = ", ".join(self.student_profile["weak_points"]) or "无"
            
            prompt = PROMPTS.SUMMARY_PROMPT.format(
                duration=f"{duration}轮对话",
                practice_count=practice_count,
                content_summary=content_summary,
                errors=errors
            )
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            summary = self.llm.chat_complete(messages)
            
            app_logger.info("生成学习总结完成")
            return summary
        
        except Exception as e:
            app_logger.error(f"生成总结失败: {str(e)}")
            return f"❌ 生成总结失败: {str(e)}"
    
    def suggest_difficulty_adjustment(self) -> str:
        """评估并建议难度调整"""
        try:
            practice_count = self.student_profile["practice_count"]
            
            if practice_count < 5:
                return "练习次数较少，暂不调整难度。建议继续练习以便更好评估。"
            
            # 简单的评估逻辑（实际可以更复杂）
            accuracy = 100 - len(self.student_profile["weak_points"]) * 10
            accuracy = max(0, min(100, accuracy))
            
            prompt = PROMPTS.DIFFICULTY_ADJUSTMENT_PROMPT.format(
                current_difficulty=self.difficulty,
                accuracy=accuracy,
                duration=f"{practice_count}次练习",
                completion="良好"
            )
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            suggestion = self.llm.chat_complete(messages)
            
            app_logger.info("难度调整建议生成完成")
            return suggestion
        
        except Exception as e:
            app_logger.error(f"生成难度建议失败: {str(e)}")
            return f"❌ 生成建议失败: {str(e)}"
    
    def set_difficulty(self, difficulty: str):
        """设置学习难度
        
        Args:
            difficulty: 难度级别（初级/中级/高级）
        """
        if difficulty in settings.DIFFICULTY_LEVELS:
            self.difficulty = difficulty
            self.student_profile["level"] = difficulty
            app_logger.info(f"难度已调整为: {difficulty}")
        else:
            app_logger.warning(f"无效的难度级别: {difficulty}")
    
    def clear_history(self):
        """清空对话历史"""
        self.chat_history = []
        app_logger.info("对话历史已清空")
    
    def _save_history(self):
        """保存对话历史"""
        try:
            storage.save_chat_history(
                self.session_id,
                self.chat_history,
                metadata={
                    "user_id": self.user_id,
                    "difficulty": self.difficulty,
                    "profile": self.student_profile
                }
            )
        except Exception as e:
            app_logger.warning(f"保存对话历史失败: {str(e)}")
    
    def _load_profile(self):
        """加载历史档案"""
        try:
            # 尝试加载最近的会话
            history_data = storage.load_chat_history(self.session_id)
            if history_data and "metadata" in history_data:
                metadata = history_data["metadata"]
                if "profile" in metadata:
                    self.student_profile.update(metadata["profile"])
                    app_logger.info("已加载历史学习档案")
        except Exception as e:
            app_logger.warning(f"加载历史档案失败: {str(e)}")
    
    def get_profile_summary(self) -> Dict:
        """获取学生档案摘要"""
        return {
            "用户ID": self.user_id,
            "当前难度": self.difficulty,
            "练习次数": self.student_profile["practice_count"],
            "薄弱项": self.student_profile["weak_points"][-5:] if self.student_profile["weak_points"] else ["暂无"],
            "对话轮数": len(self.chat_history) // 2
        }
