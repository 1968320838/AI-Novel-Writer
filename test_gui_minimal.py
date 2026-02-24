"""
最简化的PyQt5测试
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton


def main():
    # 创建应用
    app = QApplication(sys.argv)
    print("PyQt5应用已创建")

    # 创建简单窗口
    window = QWidget()
    window.setWindowTitle("GUI测试窗口")
    window.resize(300, 200)

    # 创建布局
    layout = QVBoxLayout(window)

    # 添加标签
    label = QLabel("如果你能看到这个窗口，PyQt5 GUI正常工作！")
    label.setStyleSheet("font-size: 16px; padding: 20px;")
    layout.addWidget(label)

    # 添加按钮
    btn = QPushButton("关闭")
    btn.clicked.connect(app.quit)
    layout.addWidget(btn)

    window.setLayout(layout)

    # 显示窗口
    print("准备显示窗口...")
    window.show()

    print("进入事件循环...")
    app.exec_()
    print("程序正常退出")


if __name__ == "__main__":
    print("开始简化GUI测试...")
    print(f"Python版本: {sys.version}")
    main()
