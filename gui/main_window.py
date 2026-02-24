"""
PyQt5主窗口
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QSplitter, QMenuBar, QToolBar, QAction,
                             QStatusBar, QFileDialog, QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QTextCursor

from core.controller import NovelController
from gui.novel_tree import NovelStructureTree
from gui.progress_panel import ProgressPanel
from gui.chapter_viewer import ChapterViewer
from gui.log_panel import LogPanel
from gui.dialogs import ImportDialog, SettingsDialog


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.controller = NovelController()
        self.current_chapter = None
        self.current_review = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """设置UI"""
        self.setWindowTitle("AI自动写小说智能体")
        self.setGeometry(100, 100, 1400, 900)

        # 菜单栏
        self._create_menu_bar()

        # 工具栏
        self._create_tool_bar()

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)

        # 分割器
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：小说结构树
        self.novel_tree = NovelStructureTree()
        splitter.addWidget(self.novel_tree)

        # 右侧：功能面板（使用Tab布局）
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        # 设置分割比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()

    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        import_action = QAction("导入小说(&I)", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._import_novel)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")

        settings_action = QAction("设置(&S)", self)
        settings_action.triggered.connect(self._open_settings)
        tools_menu.addAction(settings_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)

        # 导入按钮
        import_action = QAction("导入", self)
        import_action.triggered.connect(self._import_novel)
        toolbar.addAction(import_action)

        toolbar.addSeparator()

        # 开始按钮
        self.start_action = QAction("开始", self)
        self.start_action.setEnabled(False)
        self.start_action.triggered.connect(self._start_writing)
        toolbar.addAction(self.start_action)

        # 暂停按钮
        self.pause_action = QAction("暂停", self)
        self.pause_action.setEnabled(False)
        self.pause_action.triggered.connect(self._pause_writing)
        toolbar.addAction(self.pause_action)

        # 停止按钮
        self.stop_action = QAction("停止", self)
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(self._stop_writing)
        toolbar.addAction(self.stop_action)

        toolbar.addSeparator()

        # 单章写作按钮
        self.single_action = QAction("写一章", self)
        self.single_action.setEnabled(False)
        self.single_action.triggered.connect(self._write_single)
        toolbar.addAction(self.single_action)

    def _create_right_panel(self) -> QWidget:
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 进度面板
        self.progress_panel = ProgressPanel()
        layout.addWidget(self.progress_panel)

        # Tab控件
        tab_widget = QTabWidget()

        # 章节预览
        self.chapter_viewer = ChapterViewer()
        tab_widget.addTab(self.chapter_viewer, "章节预览")

        # 日志面板
        self.log_panel = LogPanel()
        tab_widget.addTab(self.log_panel, "日志")

        layout.addWidget(tab_widget)

        return panel

    def _connect_signals(self):
        """连接信号"""
        # 控制器信号（线程安全的GUI更新）
        self.controller.progress.connect(self._on_progress)
        self.controller.log.connect(self._on_log)
        self.controller.chapter_complete.connect(self._on_chapter_complete)
        self.controller.error.connect(self._on_error)

        # 树的选择信号
        self.novel_tree.chapter_selected.connect(self._on_chapter_selected)

    def _import_novel(self):
        """导入小说"""
        dialog = ImportDialog(self)
        if dialog.exec_() == ImportDialog.Accepted:
            novel_path = dialog.get_novel_path()
            try:
                project = self.controller.load_novel(novel_path)
                self.novel_tree.load_project(project)
                self.start_action.setEnabled(True)
                self.single_action.setEnabled(True)
                self._update_status_bar()
            except Exception as e:
                QMessageBox.critical(self, "导入失败", f"导入小说失败: {e}")

    def _start_writing(self):
        """开始自动写作"""
        dialog = SettingsDialog(self)
        dialog.set_mode("auto")
        if dialog.exec_() == SettingsDialog.Accepted:
            settings = dialog.get_settings()
            target_chapters = settings.get("target_chapters")
            self.controller.start_auto_mode(target_chapters)
            self.start_action.setEnabled(False)
            self.pause_action.setEnabled(True)
            self.stop_action.setEnabled(True)
            self.single_action.setEnabled(False)

    def _pause_writing(self):
        """暂停写作"""
        self.controller.pause()
        self.pause_action.setEnabled(False)
        self.start_action.setEnabled(True)

    def _stop_writing(self):
        """停止写作"""
        reply = QMessageBox.question(
            self, "确认停止", "确定要停止自动写作吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.controller.stop()
            self.start_action.setEnabled(True)
            self.pause_action.setEnabled(False)
            self.stop_action.setEnabled(False)
            self.single_action.setEnabled(True)

    def _write_single(self):
        """写单章"""
        self.controller.write_single_chapter()

    def _open_settings(self):
        """打开设置"""
        dialog = SettingsDialog(self)
        dialog.exec_()

    def _show_about(self):
        """显示关于"""
        QMessageBox.about(
            self, "关于",
            "AI自动写小说智能体 v1.0\n\n"
            "基于GLM-4.7的智能小说写作系统\n"
            "支持自动写作、审核、修正全流程"
        )

    def _on_progress(self, stage: str, chapter_num: int, progress: int, message: str):
        """进度回调"""
        self.progress_panel.update_progress(stage, chapter_num, progress, message)

    def _on_log(self, message: str):
        """日志回调"""
        self.log_panel.append_log(message)

    def _on_chapter_complete(self, chapter, review):
        """章节完成回调"""
        self.current_chapter = chapter
        self.current_review = review
        self.chapter_viewer.set_chapter(chapter, review)
        self.novel_tree.refresh()
        self._update_status_bar()

    def _on_error(self, error: str):
        """错误回调"""
        self.log_panel.append_error(error)
        QMessageBox.warning(self, "错误", error)

    def _on_chapter_selected(self, chapter):
        """章节选择回调"""
        self.chapter_viewer.set_chapter(chapter)

    def _update_status_bar(self):
        """更新状态栏"""
        info = self.controller.get_session_info()
        if info:
            status_text = (
                f"小说: {info.get('novel_name', '未加载')} | "
                f"已完成: {info.get('completed_chapters', 0)}章 | "
                f"总字数: {info.get('total_words', 0)} | "
                f"API调用: {info.get('api_calls', 0)}次 | "
                f"Token: {info.get('tokens_used', 0)}"
            )
            self.status_bar.showMessage(status_text)
        else:
            self.status_bar.showMessage("就绪")

    def closeEvent(self, event):
        """关闭事件"""
        if self.controller.session:
            self.controller.stop()
        event.accept()
