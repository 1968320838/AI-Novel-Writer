"""
一致性检查Agent
用于检查角色行为、设定、时间线的一致性
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ConsistencyIssue:
    """一致性问题"""
    type: str  # 问题类型：character, setting, timeline, logic
    severity: str  # 严重程度：critical, major, minor
    location: str  # 问题描述的位置
    description: str  # 问题描述
    suggestion: str  # 修改建议

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "severity": self.severity,
            "location": self.location,
            "description": self.description,
            "suggestion": self.suggestion
        }


class ConsistencyAgent:
    """一致性检查Agent"""

    def __init__(self, memory_manager=None):
        """
        初始化一致性检查Agent

        Args:
            memory_manager: 记忆管理器（可选）
        """
        self.memory_manager = memory_manager

    def check_chapter(self, chapter_content: str, chapter_num: int,
                     character_states: Dict = None) -> List[ConsistencyIssue]:
        """
        检查章节一致性

        Args:
            chapter_content: 章节内容
            chapter_num: 章节号
            character_states: 角色状态字典（从记忆中获取）

        Returns:
            一致性问题列表
        """
        issues = []

        # 1. 角色行为一致性检查
        if character_states:
            char_issues = self._check_character_consistency(
                chapter_content, chapter_num, character_states
            )
            issues.extend(char_issues)

        # 2. 时间线一致性检查
        timeline_issues = self._check_timeline_consistency(chapter_content, chapter_num)
        issues.extend(timeline_issues)

        # 3. 逻辑一致性检查
        logic_issues = self._check_logic_consistency(chapter_content, chapter_num)
        issues.extend(logic_issues)

        # 4. 设定一致性检查
        setting_issues = self._check_setting_consistency(chapter_content, chapter_num)
        issues.extend(setting_issues)

        return issues

    def _check_character_consistency(self, content: str, chapter_num: int,
                                   char_states: Dict) -> List[ConsistencyIssue]:
        """
        检查角色行为一致性

        检查项：
        - 死亡角色是否复活
        - 角色位置是否合理
        - 角色性格是否突变
        """
        issues = []

        for char_name, state in char_states.items():
            # 检查死亡角色是否出现
            if state.status == "死亡":
                if char_name in content:
                    issues.append(ConsistencyIssue(
                        type="character",
                        severity="critical",
                        location=f"第{chapter_num}章",
                        description=f"角色'{char_name}'在之前章节已死亡，但本章再次出现",
                        suggestion=f"检查'{char_name}'是否真的复活，或者使用另一个角色名"
                    ))

            # 检查角色性格是否一致（简单实现：检查关键词）
            if "性格" in state.attributes:
                expected_personality = state.attributes["性格"]
                # 如果内容中角色表现与设定相反，则报警
                # 这里只是简单实现，实际需要更复杂的NLP

        return issues

    def _check_timeline_consistency(self, content: str, chapter_num: int) -> List[ConsistencyIssue]:
        """
        检查时间线一致性

        检查项：
        - 时间是否合理（白天/夜晚）
        - 季节是否合理
        - 时间间隔是否合理
        """
        issues = []

        # 检查时间描述矛盾
        time_patterns = [
            (r'第二天晚上', r'第三天白天'),  # 可能矛盾
            (r'次日清晨', r'次日深夜'),
        ]

        for pattern_a, pattern_b in time_patterns:
            import re
            if re.search(pattern_a, content) and re.search(pattern_b, content):
                issues.append(ConsistencyIssue(
                    type="timeline",
                    severity="major",
                    location=f"第{chapter_num}章",
                    description=f"时间描述可能存在矛盾：同时出现'{pattern_a}'和'{pattern_b}'",
                    suggestion="检查时间线设置是否合理"
                ))

        return issues

    def _check_logic_consistency(self, content: str, chapter_num: int) -> List[ConsistencyIssue]:
        """
        检查逻辑一致性

        检查项：
        - 因果关系是否合理
        - 是否有明显的逻辑漏洞
        """
        issues = []

        # 检查常见的逻辑问题标记
        logic_indicators = [
            "突然",
            "莫名其妙",
            "毫无理由",
            "不知为何"
        ]

        for indicator in logic_indicators:
            if indicator in content:
                issues.append(ConsistencyIssue(
                    type="logic",
                    severity="minor",
                    location=f"第{chapter_num}章",
                    description=f"可能存在逻辑问题：使用了'{indicator}'",
                    suggestion="检查是否有足够的铺垫和解释"
                ))

        return issues

    def _check_setting_consistency(self, content: str, chapter_num: int) -> List[ConsistencyIssue]:
        """
        检查设定一致性

        检查项：
        - 技能等级是否与之前矛盾
        - 世界观设定是否与之前矛盾
        """
        issues = []

        # 这里需要与记忆系统配合，暂时只做基本检查
        # 实际应用时需要传入更多上下文信息

        return issues

    def check_cross_chapter_consistency(self, current_chapter: int,
                                    previous_chapters: List) -> List[ConsistencyIssue]:
        """
        检查跨章节一致性

        Args:
            current_chapter: 当前章节号
            previous_chapters: 之前的章节列表（包含content等信息）

        Returns:
            跨章节一致性问题列表
        """
        issues = []

        if not previous_chapters:
            return issues

        # 获取最近的章节
        recent_chapters = previous_chapters[-3:]  # 最近3章

        # 检查是否有明显的不一致
        # 这里可以实现更复杂的比较逻辑

        return issues

    def generate_consistency_report(self, issues: List[ConsistencyIssue]) -> str:
        """
        生成一致性检查报告

        Args:
            issues: 问题列表

        Returns:
            格式化的报告文本
        """
        if not issues:
            return "✓ 一致性检查通过，未发现问题。"

        # 按严重程度分组
        critical_issues = [i for i in issues if i.severity == "critical"]
        major_issues = [i for i in issues if i.severity == "major"]
        minor_issues = [i for i in issues if i.severity == "minor"]

        report_parts = ["# 一致性检查报告\n"]

        if critical_issues:
            report_parts.append(f"## 严重问题 ({len(critical_issues)})")
            for issue in critical_issues:
                report_parts.append(f"- [{issue.type}] {issue.description}")
                report_parts.append(f"  位置: {issue.location}")
                report_parts.append(f"  建议: {issue.suggestion}")

        if major_issues:
            report_parts.append(f"\n## 重要问题 ({len(major_issues)})")
            for issue in major_issues:
                report_parts.append(f"- [{issue.type}] {issue.description}")

        if minor_issues:
            report_parts.append(f"\n## 次要问题 ({len(minor_issues)})")
            for issue in minor_issues[:5]:  # 最多显示5个
                report_parts.append(f"- [{issue.type}] {issue.description}")

        return "\n".join(report_parts)
