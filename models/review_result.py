"""
审核结果数据模型
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class IssueType(Enum):
    """问题类型"""
    LOGIC = "logic"           # 逻辑问题
    CHARACTER = "character"    # 角色一致性问题
    PLOT = "plot"            # 剧情推进问题
    QUALITY = "quality"      # 文字质量问题
    FORMAT = "format"         # 格式问题


class IssueSeverity(Enum):
    """问题严重程度"""
    CRITICAL = "critical"     # 严重，必须修正
    MAJOR = "major"          # 重要，建议修正
    MINOR = "minor"          # 次要，可选修正


@dataclass
class Issue:
    """审核问题"""
    type: IssueType          # 问题类型
    severity: IssueSeverity   # 严重程度
    location: str            # 位置描述
    description: str          # 问题描述
    suggestion: str           # 修改建议

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "type": self.type.value,
            "severity": self.severity.value,
            "location": self.location,
            "description": self.description,
            "suggestion": self.suggestion
        }


@dataclass
class ReviewResult:
    """审核结果"""
    issues: List[Issue] = field(default_factory=list)
    overall_assessment: str = ""  # 总体评价
    passed: bool = False          # 是否通过审核
    score: float = 0.0           # 评分 (0-100)

    @property
    def critical_issues(self) -> List[Issue]:
        """获取所有严重问题"""
        return [i for i in self.issues if i.severity == IssueSeverity.CRITICAL]

    @property
    def major_issues(self) -> List[Issue]:
        """获取所有重要问题"""
        return [i for i in self.issues if i.severity == IssueSeverity.MAJOR]

    @property
    def minor_issues(self) -> List[Issue]:
        """获取所有次要问题"""
        return [i for i in self.issues if i.severity == IssueSeverity.MINOR]

    @property
    def has_critical_or_major(self) -> bool:
        """是否有严重或重要问题"""
        return any(i.severity in [IssueSeverity.CRITICAL, IssueSeverity.MAJOR] for i in self.issues)

    def add_issue(self, issue_type: IssueType, severity: IssueSeverity,
                  location: str, description: str, suggestion: str):
        """添加问题"""
        self.issues.append(Issue(
            type=issue_type,
            severity=severity,
            location=location,
            description=description,
            suggestion=suggestion
        ))

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "issues": [i.to_dict() for i in self.issues],
            "overall_assessment": self.overall_assessment,
            "passed": self.passed,
            "score": self.score
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ReviewResult':
        """从字典创建"""
        result = cls()
        for issue_data in data.get("issues", []):
            result.issues.append(Issue(
                type=IssueType(issue_data["type"]),
                severity=IssueSeverity(issue_data["severity"]),
                location=issue_data["location"],
                description=issue_data["description"],
                suggestion=issue_data["suggestion"]
            ))
        result.overall_assessment = data.get("overall_assessment", "")
        result.passed = data.get("passed", False)
        result.score = data.get("score", 0.0)
        return result
