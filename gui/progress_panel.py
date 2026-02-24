"""
进度面板
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QProgressBar, QGroupBox)
from PyQt5.QtCore import Qt


class ProgressPanel(QWidget):
    """写作进度面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # 当前操作组
        current_group = QGroupBox("当前状态")
        current_layout = QVBoxLayout(current_group)

        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        current_layout.addWidget(self.status_label)

        self.chapter_label = QLabel("当前章节: -")
        current_layout.addWidget(self.chapter_label)

        layout.addWidget(current_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% - %v")
        layout.addWidget(self.progress_bar)

        # 详细信息
        detail_group = QGroupBox("详细信息")
        detail_layout = QVBoxLayout(detail_group)

        self.stage_label = QLabel("阶段: -")
        detail_layout.addWidget(self.stage_label)

        self.message_label = QLabel("消息: -")
        self.message_label.setWordWrap(True)
        detail_layout.addWidget(self.message_label)

        layout.addWidget(detail_group)

    def update_progress(self, stage: str, chapter_num: int, progress: int, message: str):
        """
        更新进度

        Args:
            stage: 阶段 (writing/review/revision/final_check/saving/complete)
            chapter_num: 章节号
            progress: 进度百分比
            message: 状态消息
        """
        self.progress_bar.setValue(progress)

        # 阶段映射
        stage_names = {
            "writing": "正在写作",
            "review": "正在审核",
            "revision": "正在修正",
            "final_check": "最终检查",
            "saving": "保存中",
            "complete": "完成"
        }

        stage_name = stage_names.get(stage, stage)

        if stage == "complete":
            self.status_label.setText(f"第{chapter_num}章完成")
            self.status_label.setStyleSheet("color: green; font-size: 14px; font-weight: bold;")
        else:
            self.status_label.setText(f"正在处理第{chapter_num}章")
            self.status_label.setStyleSheet("color: blue; font-size: 14px; font-weight: bold;")

        self.chapter_label.setText(f"当前章节: 第{chapter_num}章")
        self.stage_label.setText(f"阶段: {stage_name}")
        self.message_label.setText(f"消息: {message}")

    def reset(self):
        """重置面板"""
        self.progress_bar.setValue(0)
        self.status_label.setText("就绪")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.chapter_label.setText("当前章节: -")
        self.stage_label.setText("阶段: -")
        self.message_label.setText("消息: -")
