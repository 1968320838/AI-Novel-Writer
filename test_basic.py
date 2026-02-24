"""
基础功能测试 - 验证导入和解析是否正常
"""

from pathlib import Path
from models.chapter import NovelProject
from utils.file_parser import NovelParser


def test_import():
    """测试导入功能"""
    print("=" * 50)
    print("测试基础功能")
    print("=" * 50)

    # 测试小说路径
    novel_path = r"G:\xs\全民诡异时代复苏，我抽取到了最次的F级技能叛逆"
    print(f"\n1. 测试路径: {novel_path}")

    # 创建解析器
    try:
        parser = NovelParser(novel_path)
        print("   - NovelParser创建成功")

        # 解析项目
        project = parser.parse()
        print(f"   - 项目名称: {project.name}")
        print(f"   - 章节数量: {len(project.chapters)}")

        # 测试大纲
        if project.outline:
            print(f"   - 大纲长度: {len(project.outline)} 字符")

        # 测试角色设定
        if project.characters:
            print(f"   - 角色设定长度: {len(project.characters)} 字符")

        # 测试现有章节
        for chapter in project.chapters[:3]:
            print(f"   - 章节 {chapter.number}: {chapter.title}")

        print("\n2. 基础功能测试通过!")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)


if __name__ == "__main__":
    test_import()
