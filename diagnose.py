"""
诊断脚本 - 帮助排查PyQt5问题
"""

import sys
import os


def check_pyqt5():
    """检查PyQt5安装"""
    print("检查PyQt5安装...")

    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QT_VERSION_STR
        print(f"   PyQt5版本: {QT_VERSION_STR}")
        print("   PyQt5导入: OK")
        return True
    except ImportError as e:
        print(f"   错误: {e}")
        return False


def check_env():
    """检查环境变量"""
    print("\n检查环境变量:")
    env_vars = ["PYTHONPATH", "QT_QPA_PLATFORM", "QT_DEBUG"]
    for var in env_vars:
        value = os.environ.get(var, "未设置")
        print(f"   {var}: {value}")


def check_files():
    """检查项目文件"""
    print("\n检查项目文件:")
    files = [
        "main.py",
        "config.py",
        "core/controller.py",
        "agents/writing_agent.py",
        "models/chapter.py"
    ]

    for file in files:
        if os.path.exists(file):
            print(f"   [存在] {file}")
        else:
            print(f"   [缺失] {file}")


def main():
    """主函数"""
    print("=" * 50)
    print("AI自动写小说智能体 - 诊断工具")
    print("=" * 50)

    # 检查PyQt5
    if not check_pyqt5():
        print("\n请先安装PyQt5:")
        print("   pip install PyQt5")
        return

    # 检查环境
    check_env()

    # 检查文件
    check_files()

    print("\n建议的启动方式:")
    print("1. 使用命令行测试基础功能:")
    print("   python test_basic.py")
    print("\n2. 如果GUI卡死，尝试:")
    print("   - 设置环境变量: set QT_DEBUG=1")
    print("   - 或使用无GUI模式进行API测试")
    print("\n按回车退出...")


if __name__ == "__main__":
    input()
    main()
