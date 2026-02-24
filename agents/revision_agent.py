"""
修正Agent - 负责修正章节中的问题
"""

from typing import List, Optional
import re

from agents.base_agent import BaseAgent
from models.chapter import Chapter
from models.review_result import ReviewResult, Issue


class RevisionAgent(BaseAgent):
    """修正Agent"""

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的网络小说编辑，负责根据审核反馈修改章节内容。

你的职责：
1. 仔细阅读审核反馈中的问题
2. 修改原文以解决所有严重和重要问题
3. 保持原有写作风格和节奏
4. 确保修改后的内容仍然符合大纲设定
5. 不要删除原有内容，而是修正问题部分

请输出修改后的完整章节内容。"""

    def revise_chapter(
        self,
        original_chapter: Chapter,
        review_result: ReviewResult,
        temperature: float = 0.6
    ) -> Chapter:
        """
        修正章节

        Args:
            original_chapter: 原始章节
            review_result: 审核结果
            temperature: 温度参数

        Returns:
            修正后的章节
        """
        # 如果没有问题，直接返回原章节
        if not review_result.issues:
            return original_chapter

        # 构建修正提示词
        prompt = self._build_revision_prompt(
            chapter=original_chapter,
            review_result=review_result
        )

        # 调用模型
        response = self.call_model(prompt, temperature)

        # 解析响应
        return self._parse_revision_response(
            response=response,
            original_chapter=original_chapter
        )

    def _build_revision_prompt(
        self,
        chapter: Chapter,
        review_result: ReviewResult
    ) -> str:
        """构建修正提示词"""
        # 按严重程度组织问题
        issues_by_severity = {
            "critical": [i for i in review_result.issues if i.severity.value == "critical"],
            "major": [i for i in review_result.issues if i.severity.value == "major"],
            "minor": [i for i in review_result.issues if i.severity.value == "minor"]
        }

        # 构建问题描述
        issues_description = self._format_issues(issues_by_severity)

        prompt = f"""请根据以下审核反馈修改章节内容。

---

## 【章节信息】

章节：第{chapter.number}章 {chapter.title}

---

## 【需要修改的问题】

### 严重问题 (Critical) - 必须修改
{self._format_issues_list(issues_by_severity['critical'])}

### 重要问题 (Major) - 建议修改
{self._format_issues_list(issues_by_severity['major'])}

### 次要问题 (Minor) - 可选修改
{self._format_issues_list(issues_by_severity['minor'])}

---

## 【总体评价】

{review_result.overall_assessment}

---

## 【原始章节内容】

{chapter.content}

---

## 【修改要求】

1. 必须解决所有严重问题(critical)和重要问题(major)
2. 保持原有的章节结构和节奏
3. 不要大幅改变剧情走向
4. 修改时注意保持角色性格一致
5. 保持原有的描写风格

## 【输出格式】

请输出修改后的完整正文内容：

```
[修改后的正文内容，保持原有格式]
```

请开始修改："""

        return prompt

    def _format_issues_list(self, issues: List) -> str:
        """格式化问题列表"""
        if not issues:
            return "无"

        formatted = []
        for i, issue in enumerate(issues, 1):
            formatted.append(f"""
{i}. 【{issue.type.value}】{issue.location}
   问题描述：{issue.description}
   修改建议：{issue.suggestion}
""")

        return '\n'.join(formatted)

    def _format_issues(self, issues_by_severity: dict) -> str:
        """格式化所有问题"""
        all_issues = (
            issues_by_severity["critical"] +
            issues_by_severity["major"] +
            issues_by_severity["minor"]
        )

        if not all_issues:
            return "本章没有发现问题。"

        return self._format_issues_list(all_issues)

    def _parse_revision_response(
        self,
        response: str,
        original_chapter: Chapter
    ) -> Chapter:
        """解析修正响应"""
        # 清理响应
        cleaned = self.clean_response(response)

        # 提取修正后的内容
        revised_content = cleaned.strip()

        # 统计新字数
        word_count = len(revised_content)

        # 创建新的章节对象
        return Chapter(
            volume=original_chapter.volume,
            number=original_chapter.number,
            title=original_chapter.title,
            content=revised_content,
            word_count=word_count,
            preview=original_chapter.preview,  # 保持原预告
            highlights=original_chapter.highlights  # 保持原看点
        )
