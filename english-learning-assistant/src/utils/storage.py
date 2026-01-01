"""学习记录存储模块"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from config.settings import settings
from src.utils.logger import app_logger


class StorageManager:
    """学习记录存储管理器"""
    
    def __init__(self):
        self.history_dir = settings.HISTORY_DIR
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    def save_chat_history(
        self,
        session_id: str,
        messages: List[Dict[str, str]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """保存对话历史
        
        Args:
            session_id: 会话ID
            messages: 消息列表
            metadata: 元数据
            
        Returns:
            是否保存成功
        """
        try:
            file_path = self.history_dir / f"chat_{session_id}.json"
            data = {
                "session_id": session_id,
                "messages": messages,
                "metadata": metadata or {},
                "updated_at": datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            app_logger.info(f"对话历史已保存: {session_id}")
            return True
        
        except Exception as e:
            app_logger.error(f"保存对话历史失败: {str(e)}")
            return False
    
    def load_chat_history(self, session_id: str) -> Optional[Dict]:
        """加载对话历史
        
        Args:
            session_id: 会话ID
            
        Returns:
            对话历史数据
        """
        try:
            file_path = self.history_dir / f"chat_{session_id}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            app_logger.info(f"对话历史已加载: {session_id}")
            return data
        
        except Exception as e:
            app_logger.error(f"加载对话历史失败: {str(e)}")
            return None
    
    def save_learning_record(
        self,
        user_id: str,
        record_type: str,
        content: Dict[str, Any]
    ) -> bool:
        """保存学习记录
        
        Args:
            user_id: 用户ID
            record_type: 记录类型（translation/speaking/writing等）
            content: 记录内容
            
        Returns:
            是否保存成功
        """
        try:
            # 创建用户目录
            user_dir = self.history_dir / user_id
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名（按日期）
            date_str = datetime.now().strftime("%Y%m%d")
            file_path = user_dir / f"{record_type}_{date_str}.json"
            
            # 加载现有记录
            records = []
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            
            # 添加新记录
            record = {
                "timestamp": datetime.now().isoformat(),
                "type": record_type,
                "content": content
            }
            records.append(record)
            
            # 保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            
            app_logger.info(f"学习记录已保存: {user_id}/{record_type}")
            return True
        
        except Exception as e:
            app_logger.error(f"保存学习记录失败: {str(e)}")
            return False
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取用户学习统计
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计数据
        """
        try:
            user_dir = self.history_dir / user_id
            if not user_dir.exists():
                return {
                    "total_records": 0,
                    "by_type": {},
                    "recent_activities": []
                }
            
            stats = {
                "total_records": 0,
                "by_type": {},
                "recent_activities": []
            }
            
            # 遍历用户所有记录文件
            for file_path in user_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        records = json.load(f)
                    
                    for record in records:
                        record_type = record.get("type", "unknown")
                        stats["total_records"] += 1
                        stats["by_type"][record_type] = stats["by_type"].get(record_type, 0) + 1
                        
                        # 收集最近活动
                        stats["recent_activities"].append({
                            "type": record_type,
                            "timestamp": record.get("timestamp", ""),
                            "summary": self._get_record_summary(record)
                        })
                
                except Exception as e:
                    app_logger.warning(f"读取记录文件失败 {file_path}: {str(e)}")
                    continue
            
            # 按时间排序最近活动
            stats["recent_activities"].sort(
                key=lambda x: x["timestamp"],
                reverse=True
            )
            stats["recent_activities"] = stats["recent_activities"][:20]
            
            return stats
        
        except Exception as e:
            app_logger.error(f"获取用户统计失败: {str(e)}")
            return {
                "total_records": 0,
                "by_type": {},
                "recent_activities": []
            }
    
    def _get_record_summary(self, record: Dict) -> str:
        """生成记录摘要"""
        content = record.get("content", {})
        record_type = record.get("type", "")
        
        if record_type == "translation":
            return f"翻译: {content.get('text', '')[:30]}..."
        elif record_type == "speaking":
            return f"口语练习: {content.get('topic', 'N/A')}"
        elif record_type == "writing":
            return f"写作批改: {content.get('title', 'N/A')}"
        else:
            return f"{record_type}练习"
    
    def clear_old_records(self, days: int = 90) -> int:
        """清理旧记录
        
        Args:
            days: 保留天数
            
        Returns:
            删除的文件数
        """
        try:
            deleted_count = 0
            current_time = datetime.now()
            
            for file_path in self.history_dir.rglob("*.json"):
                # 检查文件修改时间
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if (current_time - file_time).days > days:
                    file_path.unlink()
                    deleted_count += 1
            
            app_logger.info(f"清理了 {deleted_count} 个旧记录文件")
            return deleted_count
        
        except Exception as e:
            app_logger.error(f"清理旧记录失败: {str(e)}")
            return 0


# 全局存储管理器实例
storage = StorageManager()
