"""
核心控制器 - 协调各Agent工作
"""

import time
from typing import Optional, Dict, Any
from pathlib import Path
from threading import Thread, Event
from PyQt5.QtCore import QObject, pyqtSignal

from api.glm_client import GLMClient, get_glm_client
from models.chapter import NovelProject, Chapter
from models.review_result import ReviewResult
from agents.writing_agent import WritingAgent
from agents.review_agent import ReviewAgent
from agents.revision_agent import RevisionAgent
from utils.file_parser import NovelParser, save_chapter
from core.novel_project import WritingSession, StateManager
from config import WRITING_CONFIG, AUTO_MODE_CONFIG


class NovelController(QObject):
    """小说写作控制器"""

    # 定义信号 - 线程安全的GUI更新
    progress = pyqtSignal(str, int, int, str)  # stage, chapter_num, progress, message
    log = pyqtSignal(str)  # message
    chapter_complete = pyqtSignal(object, object)  # chapter, review
    error = pyqtSignal(str)  # error message

    def __init__(self, state_dir: Optional[Path] = None, parent=None):
        """
        初始化控制器

        Args:
            state_dir: 状态文件存储目录
            parent: 父QObject
        """
        super().__init__(parent)
        self.client = get_glm_client()
        self.state_manager = StateManager(state_dir or Path.cwd() / ".ai_novel_state")

        # 控制标志
        self._stop_event = Event()
        self._pause_event = Event()
        self._worker_thread: Optional[Thread] = None

        # 当前项目
        self.project: Optional[NovelProject] = None
        self.session: Optional[WritingSession] = None

        # Agents（延迟初始化）
        self.writing_agent = None
        self.review_agent = None
        self.revision_agent = None

        # 预先初始化GLM客户端和Agents
        try:
            client = get_glm_client()
            self.writing_agent = WritingAgent(client)
            self.review_agent = ReviewAgent(client)
            self.revision_agent = RevisionAgent(client)
        except Exception as e:
            self.log.emit(f"初始化Agent失败: {e}")

    def load_novel(self, novel_path: str) -> NovelProject:
        """
        加载小说项目

        Args:
            novel_path: 小说文件夹路径

        Returns:
            加载的NovelProject对象
        """
        parser = NovelParser(novel_path)
        self.project = parser.parse()

        # 创建或加载会话
        session = self.state_manager.load_session()
        # 始终基于实际文件中的章节号计算下一章
        next_chapter = self.project.current_chapter_number + 1

        if session and session.novel_path == novel_path:
            self.session = session
            # 更新为实际的章节号
            self.session.current_chapter = next_chapter
        else:
            self.session = WritingSession(
                novel_path=novel_path,
                novel_name=self.project.name,
                current_volume=self.project.current_volume,
                current_chapter=next_chapter
            )

        self.log.emit(f"已加载小说: {self.project.name}")
        self.log.emit(f"当前已有章节: {len(self.project.chapters)}章")
        self.log.emit(f"下一章待写: 第{self.session.current_chapter}章")

        return self.project

    def start_auto_mode(self, target_chapters: Optional[int] = None):
        """
        启动自动写作模式

        Args:
            target_chapters: 目标章节数，None表示无限
        """
        if not self.project:
            raise ValueError("请先加载小说项目")

        self.session.auto_mode = True
        self.session.target_chapters = target_chapters
        self.session.start_time = time.strftime("%Y-%m-%d %H:%M:%S")

        # 重置本次会话的完成计数
        self.session.chapters_completed = []
        self.session.total_chapters = 0
        self.session.revision_count = 0

        self._stop_event.clear()
        self._pause_event.clear()

        # 启动工作线程
        self._worker_thread = Thread(target=self._auto_write_loop, daemon=True)
        self._worker_thread.start()

        self.log.emit(f"自动写作模式已启动，目标章节: {target_chapters or '无限'}")

    def stop(self):
        """停止自动写作"""
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=5)

        self.log.emit("自动写作已停止")

    def pause(self):
        """暂停自动写作"""
        self._pause_event.set()
        self.log.emit("自动写作已暂停")

    def resume(self):
        """恢复自动写作"""
        self._pause_event.clear()
        self.log.emit("自动写作已恢复")

    def write_single_chapter(self, chapter_number: Optional[int] = None) -> Chapter:
        """
        写作单章（同步）

        Args:
            chapter_number: 章节号，None则写下一章

        Returns:
            写作的章节
        """
        if not self.project:
            raise ValueError("请先加载小说项目")

        if chapter_number is None:
            chapter_number = self.session.current_chapter

        self.log.emit(f"开始写作第{chapter_number}章...")
        self.progress.emit("writing", chapter_number, 0, "正在写作...")

        # 1. 写作
        self.session.current_agent = "writing"
        chapter = self.writing_agent.write_chapter(self.project, chapter_number)

        self.log.emit(f"写作完成，字数: {chapter.word_count}")
        self.progress.emit("writing", chapter_number, 30, "审核中...")

        # 2. 审核
        self.session.current_agent = "review"
        review_result = self.review_agent.review_chapter(self.project, chapter)

        self.log.emit(f"审核完成，评分: {review_result.score}")
        self.progress.emit("review", chapter_number, 50, f"发现{len(review_result.issues)}个问题")

        # 3. 修正（如果需要）
        revision_count = 0
        while review_result.has_critical_or_major and revision_count < WRITING_CONFIG["max_revisions"]:
            revision_count += 1
            self.session.revision_count = revision_count

            self.log.emit(f"开始第{revision_count}次修正...")
            self.progress.emit("revision", chapter_number, 50 + revision_count * 10, "修正中...")

            self.session.current_agent = "revision"
            chapter = self.revision_agent.revise_chapter(chapter, review_result)

            # 再次审核
            self.log.emit("修正完成，重新审核...")
            review_result = self.review_agent.review_chapter(self.project, chapter)
            self.log.emit(f"审核完成，评分: {review_result.score}")

        # 4. 最终检查（如果已达到最大修正次数，直接保存）
        self.progress.emit("final_check", chapter_number, 90, "最终检查...")

        # 判断是否保存：通过审核，或已用完修正次数
        should_save = (review_result.passed or
                      not review_result.has_critical_or_major or
                      revision_count >= WRITING_CONFIG["max_revisions"])

        if should_save:
            # 5. 保存
            self.progress.emit("saving", chapter_number, 95, "保存中...")
            file_path = save_chapter(self.project, chapter)

            # 更新状态
            self.project.add_chapter(chapter)
            self.session.add_completed_chapter(chapter)
            self.session.current_chapter = chapter_number + 1
            self.session.current_agent = "idle"
            self.session.revision_count = 0

            # 更新API统计
            stats = self.client.get_stats()
            self.session.api_calls = stats["total_calls"]
            self.session.tokens_used = stats["total_tokens"]

            # 保存状态
            self.state_manager.save_session(self.session)

            self.progress.emit("complete", chapter_number, 100, "完成")
            self.chapter_complete.emit(chapter, review_result)
            self.log.emit(f"第{chapter_number}章已保存: {file_path}")

            return chapter
        else:
            # 修正失败
            self.error.emit(f"第{chapter_number}章修正失败，需要人工介入")
            self.session.current_agent = "idle"
            return chapter

    def _auto_write_loop(self):
        """自动写作循环"""
        consecutive_errors = 0

        while not self._stop_event.is_set():
            # 检查暂停
            if self._pause_event.is_set():
                time.sleep(1)
                continue

            # 检查目标
            if self.session.target_chapters:
                completed = len(self.session.chapters_completed)
                if completed >= self.session.target_chapters:
                    self.log.emit("已达到目标章节数，自动写作停止")
                    break

            try:
                # 写作一章
                self.write_single_chapter()
                consecutive_errors = 0

                # 检查是否停止
                if self._stop_event.is_set():
                    break

                # 短暂休息
                time.sleep(2)

            except Exception as e:
                consecutive_errors += 1
                self.error.emit(f"写作出错: {e}")

                if consecutive_errors >= AUTO_MODE_CONFIG["max_consecutive_errors"]:
                    self.error.emit("连续错误次数过多，自动写作停止")
                    break

                time.sleep(5)

        self.session.current_agent = "idle"
        self.state_manager.save_session(self.session)

    def get_session_info(self) -> Dict[str, Any]:
        """获取当前会话信息"""
        if not self.session:
            return {}

        return {
            "novel_name": self.session.novel_name,
            "current_chapter": self.session.current_chapter,
            "completed_chapters": len(self.session.chapters_completed),
            "total_words": self.session.total_words,
            "api_calls": self.session.api_calls,
            "tokens_used": self.session.tokens_used,
            "auto_mode": self.session.auto_mode,
            "current_agent": self.session.current_agent
        }
