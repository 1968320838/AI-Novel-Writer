"""
写作Agent - 负责生成新章节
"""

from typing import Optional, List
import re

from agents.base_agent import BaseAgent
from models.chapter import NovelProject, Chapter
from utils.file_parser import NovelParser
from utils.markdown_formatter import extract_title_from_outline, get_chapter_plan_from_outline
from config import WRITING_CONFIG


class WritingAgent(BaseAgent):
    """写作Agent"""

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的网络小说作家，擅长写作"诡异复苏"类型的小说。

你的写作风格特点：
1. 节奏明快，爽点密集
2. 人物性格鲜明，对话生动
3. 诡异场景描写细腻，氛围感强
4. 善于制造悬念和反转
5. 文笔流畅，不拖沓

写作要求：
1. 每章3000-5000字
2. 保持角色性格一致
3. 严格按大纲推进剧情
4. 包含对话、动作、心理描写
5. 使用系统公告格式：【...】
6. 使用直播弹幕增强代入感

请严格按照指定格式输出章节内容。"""

    def write_chapter(
        self,
        project: NovelProject,
        chapter_number: int,
        temperature: float = 0.7
    ) -> Chapter:
        """
        写作新章节

        Args:
            project: 小说项目
            chapter_number: 章节号
            temperature: 创作温度

        Returns:
            新章节对象
        """
        # 获取章节标题
        title = extract_title_from_outline(project.outline, chapter_number)

        # 获取章节规划
        chapter_plan = get_chapter_plan_from_outline(project.outline, chapter_number)

        # 获取上一章摘要
        parser = NovelParser(str(project.path))
        prev_summary = parser.get_previous_chapter_summary(project, chapter_number)

        # 构建写作提示词
        prompt = self._build_writing_prompt(
            project=project,
            chapter_number=chapter_number,
            title=title,
            chapter_plan=chapter_plan,
            prev_summary=prev_summary
        )

        # 调用模型生成
        response = self.call_model(prompt, temperature)

        # 解析响应
        chapter = self._parse_chapter_response(
            response=response,
            volume=project.current_volume,
            number=chapter_number,
            title=title
        )

        return chapter

    def _build_writing_prompt(
        self,
        project: NovelProject,
        chapter_number: int,
        title: str,
        chapter_plan: str,
        prev_summary: str
    ) -> str:
        """构建写作提示词"""
        prompt = f"""请根据以下信息写作第{chapter_number}章：《{title}》

---

## 【大纲信息】

{chapter_plan[:1000] if chapter_plan else "请根据上下文继续推进剧情"}

---

## 【角色设定】

{self._get_character_summary(project)}

---

## 【世界观设定】

{self._get_worldview_summary(project)}

---

## 【上一章结尾】

{prev_summary[:500]}

---

## 【写作要求】

1. 字数要求：{WRITING_CONFIG['target_words']}-{WRITING_CONFIG['max_words']}字
2. 保持主角陈叛逆腹黑智商型性格
3. 按大纲推进剧情，如有需要可以适当发挥
4. 包含对话和动作描写
5. 结尾留下悬念，预示下一章内容

## 【输出格式】

请按以下格式输出：

```
# 第{chapter_number}章 {title}

[正文内容，3000-5000字]

---

**下章预告：**

[下一章的简短预告，100字左右]

敬请期待第{chapter_number + 1}章：《[下章标题]》

---

**本章字数：约[字数]字**

**核心看点：**
- [看点1]
- [看点2]
- [看点3]
```

请开始创作："""

        return prompt

    def _get_character_summary(self, project: NovelProject) -> str:
        """获取角色摘要"""
        if len(project.characters) > 500:
            # 截取主要角色部分
            lines = project.characters.split('\n')
            result = []
            for line in lines[:50]:  # 前50行
                result.append(line)
                if result and len('\n'.join(result)) > 500:
                    break
            return '\n'.join(result) + "\n...（更多角色设定）..."
        return project.characters

    def _get_worldview_summary(self, project: NovelProject) -> str:
        """获取世界观摘要"""
        if len(project.worldview) > 300:
            return project.worldview[:300] + "\n...（更多设定）..."
        return project.worldview

    def _parse_chapter_response(
        self,
        response: str,
        volume: str,
        number: int,
        title: str
    ) -> Chapter:
        """解析写作响应"""
        # 清理响应
        cleaned = self.clean_response(response)

        # 提取各部分内容
        content = self._extract_content(cleaned)
        preview = self._extract_preview(cleaned)
        highlights = self._extract_highlights(cleaned)

        # 统计字数
        word_count = len(content)

        return Chapter(
            volume=volume,
            number=number,
            title=title,
            content=content,
            word_count=word_count,
            preview=preview,
            highlights=highlights
        )

    def _extract_content(self, text: str) -> str:
        """提取正文内容"""
        # 移除标题行
        lines = text.split('\n')
        content_start = 0

        for i, line in enumerate(lines):
            if line.strip().startswith('# ') and '第' in line and '章' in line:
                content_start = i + 1
                break

        # 找到分隔线之前的内容
        content_lines = []
        for line in lines[content_start:]:
            if line.strip() == '---':
                break
            content_lines.append(line)

        return '\n'.join(content_lines).strip()

    def _extract_preview(self, text: str) -> str:
        """提取下章预告"""
        match = re.search(r'下章预告[:：]\s*\n?(.*?)(?=\n敬请期待|\n---)', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return "更多精彩内容，敬请期待..."

    def _extract_highlights(self, text: str) -> List[str]:
        """提取核心看点"""
        match = re.search(r'核心看点[:：]\s*\n?(.*?)(?=\n---|$)', text, re.DOTALL)
        if match:
            highlights_text = match.group(1).strip()
            highlights = []
            for line in highlights_text.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('、'):
                    highlights.append(line.lstrip('-、').strip())
            return highlights
        return []
