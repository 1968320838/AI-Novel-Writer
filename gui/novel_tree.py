"""
小说结构树
"""

from PyQt5.QtWidgets import (QTreeWidget, QTreeWidgetItem, QMenu,
                             QAbstractItemView, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QCursor

from models.chapter import NovelProject, Chapter


class NovelStructureTree(QTreeWidget):
    """小说结构树"""

    chapter_selected = pyqtSignal(object)  # 章节选择信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.project = None

    def _setup_ui(self):
        """设置UI"""
        self.setHeaderLabels(["项目结构"])
        self.setAlternatingRowColors(True)
        self.setIndentation(20)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.itemClicked.connect(self._on_item_clicked)

    def load_project(self, project: NovelProject):
        """加载项目"""
        self.project = project
        self.clear()

        # 根节点
        root = QTreeWidgetItem(self)
        root.setText(0, project.name)
        root.setExpanded(True)

        # 设定节点
        settings_item = QTreeWidgetItem(root)
        settings_item.setText(0, "设定")
        settings_item.setExpanded(True)

        # 添加设定文件
        settings_files = [
            ("大纲", project.outline),
            ("角色设定", project.characters),
            ("技能体系", project.skills),
            ("世界观", project.worldview),
        ]

        for name, content in settings_files:
            if content:
                item = QTreeWidgetItem(settings_item)
                item.setText(0, f"{name}.md")
                item.setData(0, Qt.UserRole, {"type": "setting", "name": name})

        # 章节节点
        chapters_item = QTreeWidgetItem(root)
        chapters_item.setText(0, "章节")
        chapters_item.setExpanded(True)

        # 按卷分组
        volumes = {}
        for chapter in project.chapters:
            if chapter.volume not in volumes:
                volumes[chapter.volume] = []
            volumes[chapter.volume].append(chapter)

        # 添加章节
        for volume_name in sorted(volumes.keys()):
            volume_item = QTreeWidgetItem(chapters_item)
            volume_item.setText(0, volume_name)
            volume_item.setExpanded(True)

            for chapter in sorted(volumes[volume_name], key=lambda x: x.number):
                chapter_item = QTreeWidgetItem(volume_item)
                chapter_item.setText(0, f"第{chapter.number}章 - {chapter.title}")
                chapter_item.setData(0, Qt.UserRole, {"type": "chapter", "chapter": chapter})

    def refresh(self):
        """刷新树"""
        if self.project:
            self.load_project(self.project)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """项目点击事件"""
        data = item.data(0, Qt.UserRole)
        if data and data.get("type") == "chapter":
            chapter = data.get("chapter")
            if chapter:
                self.chapter_selected.emit(chapter)

    def _show_context_menu(self, pos):
        """显示右键菜单"""
        item = self.itemAt(pos)
        if not item:
            return

        data = item.data(0, Qt.UserRole)
        if not data:
            return

        menu = QMenu(self)

        if data.get("type") == "chapter":
            view_action = menu.addAction("查看章节")
            view_action.triggered.connect(lambda: self.chapter_selected.emit(data.get("chapter")))

            menu.addSeparator()

            copy_action = menu.addAction("复制文件名")
            copy_action.triggered.connect(
                lambda: QApplication.clipboard().setText(data.get("chapter").filename)
            )

        menu.exec_(QCursor.pos())
