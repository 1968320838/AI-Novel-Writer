"""
小说项目模型和状态管理
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from datetime import datetime

from models.chapter import NovelProject, Chapter
from models.review_result import ReviewResult


@dataclass
class WritingSession:
    """写作会话状态"""
    novel_path: str                       # 小说路径
    novel_name: str                        # 小说名称
    current_volume: str                    # 当前卷
    current_chapter: int                  # 当前章节号
    chapters_completed: List[str] = field(default_factory=list)  # 已完成章节

    # 写作统计
    total_chapters: int = 0
    total_words: int = 0
    api_calls: int = 0
    tokens_used: int = 0

    # Agent状态
    current_agent: str = "idle"           # 当前活跃的agent
    last_review: Optional[Dict] = None    # 最后的审核结果
    revision_count: int = 0                # 当前修正次数

    # 设置
    auto_mode: bool = False               # 自动模式
    target_chapters: Optional[int] = None  # 目标章节数

    # 时间戳
    start_time: Optional[str] = None
    last_update: Optional[str] = None

    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'WritingSession':
        """从字典创建"""
        return cls(**data)

    def update_timestamp(self):
        """更新时间戳"""
        self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_completed_chapter(self, chapter: Chapter):
        """记录完成的章节"""
        chapter_id = f"{chapter.volume}/{chapter.filename}"
        if chapter_id not in self.chapters_completed:
            self.chapters_completed.append(chapter_id)

        self.total_chapters = len(self.chapters_completed)
        self.total_words += chapter.word_count
        self.update_timestamp()


class StateManager:
    """状态持久化管理器"""

    def __init__(self, state_dir: Path):
        """
        初始化状态管理器

        Args:
            state_dir: 状态文件存储目录
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session: WritingSession, session_name: str = "current"):
        """
        保存会话状态

        Args:
            session: 写作会话
            session_name: 会话名称
        """
        session.update_timestamp()
        state_file = self.state_dir / f"{session_name}.json"

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)

    def load_session(self, session_name: str = "current") -> Optional[WritingSession]:
        """
        加载会话状态

        Args:
            session_name: 会话名称

        Returns:
            WritingSession对象，如果不存在则返回None
        """
        state_file = self.state_dir / f"{session_name}.json"

        if not state_file.exists():
            return None

        with open(state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return WritingSession.from_dict(data)

    def delete_session(self, session_name: str = "current"):
        """
        删除会话状态

        Args:
            session_name: 会话名称
        """
        state_file = self.state_dir / f"{session_name}.json"
        if state_file.exists():
            state_file.unlink()

    def list_sessions(self) -> List[str]:
        """
        列出所有会话

        Returns:
            会话名称列表
        """
        sessions = []
        for file in self.state_dir.glob("*.json"):
            sessions.append(file.stem)
        return sessions
