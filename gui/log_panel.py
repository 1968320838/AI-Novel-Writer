"""
日志面板
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton,
                             QHBoxLayout, QCheckBox)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QTextCursor, QFont, QColor, QTextCharFormat


class LogPanel(QWidget):
    """日志面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.auto_scroll = True

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # 工具栏
        toolbar_layout = QHBoxLayout()

        self.clear_btn = QPushButton("清空日志")
        self.clear_btn.clicked.connect(self.clear_log)
        toolbar_layout.addWidget(self.clear_btn)

        self.auto_scroll_cb = QCheckBox("自动滚动")
        self.auto_scroll_cb.setChecked(True)
        self.auto_scroll_cb.toggled.connect(self._toggle_auto_scroll)
        toolbar_layout.addWidget(self.auto_scroll_cb)

        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_text)

    def append_log(self, message: str):
        """添加日志"""
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        self._append_text(f"[{timestamp}] {message}", "normal")

    def append_error(self, message: str):
        """添加错误日志"""
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        self._append_text(f"[{timestamp}] [错误] {message}", "error")

    def append_success(self, message: str):
        """添加成功日志"""
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        self._append_text(f"[{timestamp}] {message}", "success")

    def _append_text(self, text: str, msg_type: str = "normal"):
        """添加文本"""
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)

        # 设置颜色
        if msg_type == "error":
            color = QColor(200, 50, 50)
        elif msg_type == "success":
            color = QColor(50, 150, 50)
        else:
            color = QColor(0, 0, 0)

        format = QTextCharFormat()
        format.setForeground(color)

        cursor.insertText(text + "\n", format)

        if self.auto_scroll:
            self.log_text.verticalScrollBar().setValue(
                self.log_text.verticalScrollBar().maximum()
            )

    def clear_log(self):
        """清空日志"""
        self.log_text.clear()

    def _toggle_auto_scroll(self, checked: bool):
        """切换自动滚动"""
        self.auto_scroll = checked
