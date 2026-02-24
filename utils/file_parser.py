"""
文件解析工具
用于解析小说文件夹结构
"""

from pathlib import Path
from typing import Optional
import re

from models.chapter import NovelProject, Chapter
from config import NOVEL_STRUCTURE


class NovelParser:
    """小说文件夹解析器"""

    def __init__(self, novel_path: str):
        """
        初始化解析器

        Args:
            novel_path: 小说文件夹路径
        """
        self.novel_path = Path(novel_path)
        if not self.novel_path.exists():
            raise FileNotFoundError(f"小说文件夹不存在: {novel_path}")

        self.settings_dir = self.novel_path / NOVEL_STRUCTURE["settings_dir"]
        self.chapters_dir = self.novel_path / NOVEL_STRUCTURE["chapters_dir"]

    def parse(self) -> NovelProject:
        """
        解析整个小说项目

        Returns:
            NovelProject对象
        """
        # 获取小说名称
        novel_name = self.novel_path.name

        # 创建项目对象
        project = NovelProject(
            name=novel_name,
            path=self.novel_path
        )

        # 解析设定文件
        if self.settings_dir.exists():
            self._parse_settings(project)

        # 解析章节文件
        if self.chapters_dir.exists():
            self._parse_chapters(project)

        return project

    def _parse_settings(self, project: NovelProject):
        """解析设定文件夹"""
        settings_files = {
            "outline": NOVEL_STRUCTURE["outline_file"],
            "characters": NOVEL_STRUCTURE["character_file"],
            "skills": NOVEL_STRUCTURE["skill_file"],
            "worldview": NOVEL_STRUCTURE["worldview_file"],
        }

        for key, filename in settings_files.items():
            file_path = self.settings_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    setattr(project, key, content)

    def _parse_chapters(self, project: NovelProject):
        """解析章节文件夹"""
        # 遍历所有卷文件夹
        for volume_dir in sorted(self.chapters_dir.iterdir()):
            if not volume_dir.is_dir():
                continue

            # 遍历该卷的所有章节文件
            for chapter_file in sorted(volume_dir.iterdir()):
                if not chapter_file.is_file() or not chapter_file.suffix == '.md':
                    continue

                try:
                    chapter = Chapter.parse_from_file(chapter_file)
                    project.add_chapter(chapter)
                except Exception as e:
                    print(f"警告: 解析章节文件失败 {chapter_file}: {e}")

    def get_outline_summary(self, project: NovelProject, max_length: int = 2000) -> str:
        """
        获取大纲摘要（用于AI上下文）

        Args:
            project: 小说项目
            max_length: 最大长度

        Returns:
            大纲摘要文本
        """
        if not project.outline:
            return ""

        outline = project.outline

        # 如果大纲较短，直接返回
        if len(outline) <= max_length:
            return outline

        # 如果大纲较长，截取关键部分
        lines = outline.split('\n')

        # 保留标题和前几章的规划
        result = []
        current_length = 0

        for line in lines:
            if current_length + len(line) > max_length:
                break
            result.append(line)
            current_length += len(line) + 1

        result.append("\n...（后续大纲省略）...")
        return '\n'.join(result)

    def get_character_summary(self, project: NovelProject, max_length: int = 1500) -> str:
        """
        获取角色设定摘要

        Args:
            project: 小说项目
            max_length: 最大长度

        Returns:
            角色设定摘要
        """
        if not project.characters:
            return ""

        characters = project.characters

        if len(characters) <= max_length:
            return characters

        # 截取主要角色设定
        lines = characters.split('\n')
        result = []
        current_length = 0

        for line in lines:
            if current_length + len(line) > max_length:
                break
            result.append(line)
            current_length += len(line) + 1

        return '\n'.join(result)

    def get_previous_chapter_summary(self, project: NovelProject, chapter_number: int) -> str:
        """
        获取上一章的摘要

        Args:
            project: 小说项目
            chapter_number: 当前章节号

        Returns:
            上一章摘要
        """
        prev_chapter = project.get_previous_chapter(chapter_number)
        if not prev_chapter:
            return "这是第一章，没有前文。"

        # 返回上一章的标题和末尾部分
        content_lines = prev_chapter.content.split('\n')

        # 取最后30行作为摘要
        summary_lines = content_lines[-30:] if len(content_lines) > 30 else content_lines

        summary = f"# {prev_chapter.title}（第{prev_chapter.number}章）\n\n"
        summary += "...（前文省略）...\n\n"
        summary += '\n'.join(summary_lines)

        return summary


def save_chapter(project: NovelProject, chapter: Chapter) -> Path:
    """
    保存章节到文件

    Args:
        project: 小说项目
        chapter: 章节对象

    Returns:
        保存的文件路径
    """
    # 确保目录存在
    chapter_dir = project.path / "章节" / chapter.volume
    chapter_dir.mkdir(parents=True, exist_ok=True)

    # 文件路径
    file_path = chapter_dir / chapter.filename

    # 写入内容
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(chapter.format_for_output())

    return file_path
