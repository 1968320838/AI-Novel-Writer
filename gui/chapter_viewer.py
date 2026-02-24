"""
章节预览面板
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QTabWidget,
                             QLabel, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextDocument, QFont
from markdown import markdown

from models.chapter import Chapter
from models.review_result import ReviewResult


class ChapterViewer(QWidget):
    """章节预览面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # 标签页
        self.tab_widget = QTabWidget()

        # 原文标签页
        self.content_edit = QTextEdit()
        self.content_edit.setReadOnly(True)
        self.content_edit.setFont(QFont("Microsoft YaHei", 11))
        self.tab_widget.addTab(self.content_edit, "原文")

        # Markdown预览标签页
        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setFont(QFont("Microsoft YaHei", 11))
        self.tab_widget.addTab(self.preview_edit, "预览")

        # 审核结果标签页
        self.review_widget = QWidget()
        review_layout = QVBoxLayout(self.review_widget)
        self.review_text = QTextEdit()
        self.review_text.setReadOnly(True)
        review_layout.addWidget(self.review_text)
        self.tab_widget.addTab(self.review_widget, "审核结果")

        layout.addWidget(self.tab_widget)

        # 信息标签
        self.info_label = QLabel("请选择一个章节查看")
        self.info_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        layout.addWidget(self.info_label)

    def set_chapter(self, chapter: Chapter, review: ReviewResult = None):
        """
        设置章节内容

        Args:
            chapter: 章节对象
            review: 审核结果（可选）
        """
        # 显示原文
        full_text = chapter.format_for_output()
        self.content_edit.setPlainText(full_text)

        # 显示Markdown预览
        html_content = markdown(full_text)
        self.preview_edit.setHtml(html_content)

        # 显示审核结果
        if review:
            review_text = self._format_review_result(review)
            self.review_text.setPlainText(review_text)
        else:
            self.review_text.setPlainText("暂无审核结果")

        # 更新信息标签
        info = (
            f"章节: 第{chapter.number}章 - {chapter.title} | "
            f"卷: {chapter.volume} | "
            f"字数: {chapter.word_count}"
        )
        self.info_label.setText(info)

    def _format_review_result(self, review: ReviewResult) -> str:
        """格式化审核结果"""
        lines = [
            f"总体评价: {review.overall_assessment}",
            f"评分: {review.score}",
            f"是否通过: {'是' if review.passed else '否'}",
            f"\n发现问题 ({len(review.issues)}个):",
            ""
        ]

        for i, issue in enumerate(review.issues, 1):
            severity_names = {
                "critical": "严重",
                "major": "重要",
                "minor": "次要"
            }
            severity_name = severity_names.get(issue.severity.value, issue.severity.value)

            lines.append(f"{i}. [{severity_name}] {issue.type.value} - {issue.location}")
            lines.append(f"   描述: {issue.description}")
            lines.append(f"   建议: {issue.suggestion}")
            lines.append("")

        return "\n".join(lines)

    def clear(self):
        """清空内容"""
        self.content_edit.clear()
        self.preview_edit.clear()
        self.review_text.clear()
        self.info_label.setText("请选择一个章节查看")
