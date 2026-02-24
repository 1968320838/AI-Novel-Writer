"""
数据模型
"""

from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path
from datetime import datetime
import re


@dataclass
class Chapter:
    """章节数据模型"""

    volume: str              # 卷名，如"第一卷"
    number: int              # 章节号
    title: str               # 章节标题
    content: str = ""        # 章节内容
    word_count: int = 0      # 字数统计
    preview: str = ""        # 下章预告
    highlights: List[str] = field(default_factory=list)  # 核心看点

    @property
    def filename(self) -> str:
        """获取章节文件名"""
        return f"第{self.number}章-{self.title}.md"

    @property
    def full_path(self, novel_path: Path) -> Path:
        """获取章节完整路径"""
        return novel_path / "章节" / self.volume / self.filename

    @classmethod
    def parse_from_file(cls, file_path: Path) -> 'Chapter':
        """
        从文件解析章节

        Args:
            file_path: 章节文件路径

        Returns:
            Chapter对象
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析章节号和标题（从文件名）
        filename = file_path.stem
        match = re.match(r'第(\d+)章-(.+)', filename)
        if match:
            number = int(match.group(1))
            title = match.group(2)
        else:
            raise ValueError(f"无法解析章节文件名: {filename}")

        # 提取卷名
        volume = file_path.parent.name

        # 提取内容
        chapter_content = cls._extract_content(content)

        # 提取下章预告
        preview = cls._extract_preview(content)

        # 提取核心看点
        highlights = cls._extract_highlights(content)

        # 统计字数（排除标题、分隔线等）
        word_count = cls._count_words(chapter_content)

        return cls(
            volume=volume,
            number=number,
            title=title,
            content=chapter_content,
            word_count=word_count,
            preview=preview,
            highlights=highlights
        )

    @staticmethod
    def _extract_content(full_content: str) -> str:
        """提取章节正文内容"""
        # 找到第一个标题行之后的内容
        lines = full_content.split('\n')
        content_start = 0

        for i, line in enumerate(lines):
            if line.strip().startswith('# ') and '第' in line and '章' in line:
                content_start = i + 1
                break

        # 找到分隔线"---"之前的内容
        content_lines = []
        for line in lines[content_start:]:
            if line.strip() == '---':
                break
            content_lines.append(line)

        return '\n'.join(content_lines).strip()

    @staticmethod
    def _extract_preview(full_content: str) -> str:
        """提取下章预告"""
        match = re.search(r'下章预告：(.*?)(?=\n敬请期待|\n---)', full_content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    @staticmethod
    def _extract_highlights(full_content: str) -> List[str]:
        """提取核心看点"""
        match = re.search(r'核心看点：(.*?)(?=\n---|$)', full_content, re.DOTALL)
        if match:
            highlights_text = match.group(1).strip()
            # 解析列表项
            highlights = []
            for line in highlights_text.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('、'):
                    highlights.append(line.lstrip('-、').strip())
            return highlights
        return []

    @staticmethod
    def _count_words(content: str) -> int:
        """统计字数（排除markdown符号）"""
        # 移除markdown标记
        clean_text = re.sub(r'[#*\-\[\]()》《`]', '', content)
        # 统计中文字符和英文单词
        chinese_chars = sum(1 for c in clean_text if '\u4e00' <= c <= '\u9fff')
        # 粗略估算英文单词数
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', clean_text))
        return chinese_chars + english_words

    def format_for_output(self) -> str:
        """
        格式化章节用于输出

        Returns:
            格式化后的完整章节文本
        """
        output = f"# 第{self.number}章 {self.title}\n\n"
        output += self.content + "\n\n"
        output += "---\n\n"
        output += "**下章预告：**\n\n" + self.preview + "\n\n"
        output += f"敬请期待第{self.number + 1}章。\n\n"
        output += "---\n\n"
        output += f"**本章字数：约{self.word_count}字**\n\n"

        if self.highlights:
            output += "**核心看点：**\n"
            for highlight in self.highlights:
                output += f"- {highlight}\n"

        return output


@dataclass
class NovelProject:
    """小说项目模型"""

    name: str                       # 小说名称
    path: Path                      # 小说根目录
    outline: str = ""                # 大纲内容
    characters: str = ""             # 角色设定
    skills: str = ""                 # 技能体系
    worldview: str = ""              # 世界观设定
    chapters: List[Chapter] = field(default_factory=list)  # 章节列表

    @property
    def current_chapter_number(self) -> int:
        """当前最新章节号"""
        if not self.chapters:
            return 0
        return max(ch.number for ch in self.chapters)

    @property
    def current_volume(self) -> str:
        """当前最新卷名"""
        if not self.chapters:
            return "第一卷"
        return self.chapters[-1].volume

    def get_chapter_by_number(self, number: int) -> Optional[Chapter]:
        """根据章节号获取章节"""
        for ch in self.chapters:
            if ch.number == number:
                return ch
        return None

    def get_previous_chapter(self, current_number: int) -> Optional[Chapter]:
        """获取上一章节"""
        return self.get_chapter_by_number(current_number - 1)

    def add_chapter(self, chapter: Chapter):
        """添加章节"""
        # 检查是否已存在
        for i, ch in enumerate(self.chapters):
            if ch.number == chapter.number:
                self.chapters[i] = chapter
                return
        self.chapters.append(chapter)
        # 按章节号排序
        self.chapters.sort(key=lambda x: x.number)
