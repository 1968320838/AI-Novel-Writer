"""
审核Agent - 负责检查章节质量
"""

from typing import List, Optional
import re

from agents.base_agent import BaseAgent
from models.chapter import Chapter, NovelProject
from models.review_result import ReviewResult, Issue, IssueType, IssueSeverity


class ReviewAgent(BaseAgent):
    """审核Agent"""

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的网络小说编辑，负责审核"诡异复苏"类型小说的章节质量。

你的职责是仔细检查章节中可能存在的问题，包括：
1. 逻辑一致性 - 剧情是否合理，前后是否矛盾
2. 角色一致性 - 角色行为是否符合设定
3. 剧情推进 - 是否有效推进主线剧情
4. 文字质量 - 用词、描写是否到位

请以JSON格式返回审核结果。"""

    def review_chapter(
        self,
        project: NovelProject,
        chapter: Chapter,
        temperature: float = 0.5
    ) -> ReviewResult:
        """
        审核章节

        Args:
            project: 小说项目
            chapter: 待审核章节
            temperature: 温度参数（审核时使用较低温度）

        Returns:
            审核结果
        """
        # 获取上下文
        prev_chapter = project.get_previous_chapter(chapter.number)
        prev_summary = prev_chapter.content[-500:] if prev_chapter else "这是第一章"

        # 构建审核提示词
        prompt = self._build_review_prompt(
            project=project,
            chapter=chapter,
            prev_summary=prev_summary
        )

        # 调用模型
        response = self.call_model(prompt, temperature)

        # 解析响应
        return self._parse_review_response(response)

    def _build_review_prompt(
        self,
        project: NovelProject,
        chapter: Chapter,
        prev_summary: str
    ) -> str:
        """构建审核提示词"""
        prompt = f"""请审核以下章节，找出所有问题并给出修改建议。

---

## 【章节信息】

章节：第{chapter.number}章 {chapter.title}
字数：{chapter.word_count}字

---

## 【角色设定参考】

{self._get_character_summary(project)}

---

## 【上一章结尾】

{prev_summary}

---

## 【待审核章节】

{chapter.content[:3000]}

{('...' if len(chapter.content) > 3000 else '')}

---

## 【审核要求】

请从以下四个维度审核该章节：

### 1. 逻辑一致性 (logic)
- 剧情是否合理
- 前后是否有矛盾
- 时间线是否连贯
- 因果关系是否成立

### 2. 角色一致性 (character)
- 角色行为是否符合其设定
- 对话风格是否一致
- 角色关系是否合理

### 3. 剧情推进 (plot)
- 是否有效推进主线
- 是否与大纲相符
- 节奏是否合理

### 4. 文字质量 (quality)
- 描写是否到位
- 用词是否准确
- 对话是否自然

---

## 【输出格式】

请严格按照以下JSON格式输出：

```json
{{
  "issues": [
    {{
      "type": "logic|character|plot|quality",
      "severity": "critical|major|minor",
      "location": "问题位置描述",
      "description": "问题描述",
      "suggestion": "修改建议"
    }}
  ],
  "overall_assessment": "总体评价，100字以内",
  "score": 85
}}
```

如果没有问题，issues数组可以为空。
评分范围0-100分，低于60分需要大改，60-80分有小问题，80分以上质量良好。

请开始审核："""

        return prompt

    def _get_character_summary(self, project: NovelProject) -> str:
        """获取角色摘要"""
        if len(project.characters) > 500:
            return project.characters[:500] + "\n...（更多角色设定）..."
        return project.characters

    def _parse_review_response(self, response: str) -> ReviewResult:
        """解析审核响应"""
        # 尝试提取JSON
        data = self.extract_json_from_response(response)

        if data:
            result = ReviewResult()
            result.issues = []
            result.overall_assessment = data.get("overall_assessment", "")
            result.score = data.get("score", 0.0)
            result.passed = result.score >= 60 and not any(
                (isinstance(i, dict) and i.get("severity") == "critical") or
                (isinstance(i, Issue) and i.severity == IssueSeverity.CRITICAL)
                for i in data.get("issues", [])
            )

            for issue_data in data.get("issues", []):
                try:
                    result.issues.append(Issue(
                        type=IssueType(issue_data["type"]),
                        severity=IssueSeverity(issue_data["severity"]),
                        location=issue_data["location"],
                        description=issue_data["description"],
                        suggestion=issue_data["suggestion"]
                    ))
                except (KeyError, ValueError) as e:
                    print(f"警告: 解析问题数据失败: {e}")
                    continue

            return result

        # 如果无法解析JSON，返回默认结果
        return ReviewResult(
            overall_assessment="审核响应解析失败",
            passed=False,
            score=0.0
        )
