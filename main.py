"""
AI自动写小说智能体 - 主入口
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from gui.main_window import MainWindow


def main():
    """主函数"""
    # 设置高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("AI自动写小说智能体")
    app.setOrganizationName("AI Novel Writer")

    # 创建主窗口
    window = MainWindow()
    window.show()

    # 运行
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
