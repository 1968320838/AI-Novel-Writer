"""
Markdown格式化工具
"""

import re


def extract_title_from_outline(outline: str, chapter_number: int) -> str:
    """
    从大纲中提取指定章节的标题

    Args:
        outline: 大纲内容
        chapter_number: 章节号

    Returns:
        章节标题
    """
    # 匹配模式: **第X章：标题** 或 **第X章 标题**
    pattern = rf'\*\*第{chapter_number}章[:：\s]+(.+?)\*\*'
    matches = re.findall(pattern, outline)

    if matches:
        return matches[0].strip()

    # 如果没有找到，尝试其他格式
    pattern = rf'第{chapter_number}章[:：\s]+(.+)'
    matches = re.findall(pattern, outline)

    if matches:
        return matches[0].strip()

    # 尝试从章节组标题中提取（如 "第11-15章：组队挑战"）
    group_pattern = rf'\*\*第(\d+)-(\d+)章[:：\s]+(.+?)\*\*'
    group_matches = re.findall(group_pattern, outline)

    for start, end, group_title in group_matches:
        if int(start) <= chapter_number <= int(end):
            return group_title.strip()

    # 如果还是没有，返回默认标题
    return f"未命名章节_{chapter_number}"


def get_chapter_plan_from_outline(outline: str, chapter_number: int) -> str:
    """
    从大纲中提取指定章节的规划

    Args:
        outline: 大纲内容
        chapter_number: 章节号

    Returns:
        章节规划内容
    """
    # 找到该章节的部分
    pattern = rf'\*\*第{chapter_number}章[:：].+?\*\*'

    # 分割大纲
    parts = re.split(pattern, outline)

    if len(parts) > 1:
        # 获取该章节后的内容，直到下一个章节标记
        chapter_content = parts[1]

        # 找到下一个章节标记的位置
        next_chapter_match = re.search(r'\*\*第\d+章[:：]', chapter_content)

        if next_chapter_match:
            chapter_content = chapter_content[:next_chapter_match.start()]

        return chapter_content.strip()

    return ""


def clean_markdown_text(text: str) -> str:
    """
    清理Markdown文本

    Args:
        text: 原始文本

    Returns:
        清理后的文本
    """
    # 移除多余的空行
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 统一引号
    text = text('"', '"').text('"', '"')
    text = text(''', "'").text(''', "'")

    # 移除行尾空格
    lines = text.split('\n')
    lines = [line.rstrip() for line in lines]
    text = '\n'.join(lines)

    return text.strip()


def format_chapter_content(title: str, content: str, preview: str = "", highlights: list = None) -> str:
    """
    格式化章节内容

    Args:
        title: 章节标题
        content: 章节正文
        preview: 下章预告
        highlights: 核心看点列表

    Returns:
        格式化后的完整章节
    """
    output = f"# {title}\n\n"
    output += content + "\n\n"
    output += "---\n\n"

    if preview:
        output += "**下章预告：**\n\n"
        output += preview + "\n\n"

    output += "---\n\n"
    output += f"**本章字数：约{len(content)}字**\n\n"

    if highlights:
        output += "**核心看点：**\n"
        for item in highlights:
            output += f"- {item}\n"

    return output
