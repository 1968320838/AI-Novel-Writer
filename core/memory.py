"""
记忆管理模块
用于存储和检索小说的长期记忆、角色状态和关键事件
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
from datetime import datetime
import re


@dataclass
class CharacterState:
    """角色状态"""
    name: str                           # 角色名称
    current_location: Optional[str] = None    # 当前位置
    status: str = "正常"                  # 状态（正常、受伤、死亡等）
    relationships: Dict[str, str] = field(default_factory=dict)  # 关系：{"林小夭": "冷漠"}
    attributes: Dict[str, Any] = field(default_factory=dict)  # 属性：{"等级": "F级", "技能": "叛逆"}
    last_appearance_chapter: int = 0     # 最后出现的章节号

    def update_state(self, chapter_num: int, **kwargs):
        """更新角色状态"""
        for key, value in kwargs.items():
            if key == "location":
                self.current_location = value
            elif key == "status":
                self.status = value
            elif key == "relationship":
                if value[0] in self.relationships and value[1]:
                    self.relationships[value[0]] = value[1]
                else:
                    self.relationships[value[0]] = value[1]
            elif key == "attribute":
                self.attributes[value[0]] = value[1]
        self.last_appearance_chapter = chapter_num


@dataclass
class PlotEvent:
    """剧情事件"""
    chapter: int                         # 发生的章节号
    event_type: str                      # 事件类型（伏笔、高潮、转折、揭晓等）
    description: str                      # 事件描述
    characters: List[str] = field(default_factory=list)  # 涉及角色
    keywords: List[str] = field(default_factory=list)  # 关键词，用于检索
    resolved: bool = False                  # 是否已揭晓/回收

    def to_search_text(self) -> str:
        """转换为可搜索的文本"""
        return f"第{self.chapter}章 {self.description} {' '.join(self.keywords)}"


@dataclass
class ChapterSummary:
    """章节摘要"""
    chapter: int                         # 章节号
    title: str                           # 章节标题
    summary: str                          # 摘要内容
    key_events: List[str] = field(default_factory=list)  # 关键事件
    characters: List[str] = field(default_factory=list)  # 涉及角色
    word_count: int = 0                   # 字数

    def to_search_text(self) -> str:
        """转换为可搜索的文本"""
        return f"第{self.chapter}章 {self.title} {self.summary}"


class MemoryManager:
    """记忆管理器"""

    def __init__(self, state_dir: Path):
        """
        初始化记忆管理器

        Args:
            state_dir: 状态存储目录
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.memory_file = self.state_dir / "memory.json"
        self.character_states: Dict[str, CharacterState] = {}
        self.plot_events: List[PlotEvent] = []
        self.chapter_summaries: List[ChapterSummary] = []

        self._load_memory()

    def _load_memory(self):
        """加载记忆数据"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # 加载角色状态
                    for name, state_data in data.get("character_states", {}).items():
                        self.character_states[name] = CharacterState(**state_data)

                    # 加载剧情事件
                    for event_data in data.get("plot_events", []):
                        self.plot_events.append(PlotEvent(**event_data))

                    # 加载章节摘要
                    for summary_data in data.get("chapter_summaries", []):
                        self.chapter_summaries.append(ChapterSummary(**summary_data))

            except Exception as e:
                print(f"警告: 加载记忆数据失败: {e}")

    def _save_memory(self):
        """保存记忆数据"""
        data = {
            "character_states": {
                name: asdict(state)
                for name, state in self.character_states.items()
            },
            "plot_events": [asdict(event) for event in self.plot_events],
            "chapter_summaries": [asdict(summary) for summary in self.chapter_summaries],
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_chapter_summary(self, chapter_num: int, title: str, content: str,
                          word_count: int, characters: List[str]):
        """
        添加章节摘要

        Args:
            chapter_num: 章节号
            title: 章节标题
            content: 章节内容
            word_count: 字数
            characters: 涉及角色列表
        """
        # 提取关键事件（简单实现：取前500字作为摘要）
        summary_text = content[:500] if len(content) > 500 else content

        # 提取关键词（章节号、标题中的关键词）
        keywords = [title]
        # 从内容中提取可能的关键词（被【】包围的内容）
        keywords.extend(re.findall(r'【(.+?)】', content))

        summary = ChapterSummary(
            chapter=chapter_num,
            title=title,
            summary=summary_text,
            key_events=keywords[:5],  # 最多保存5个关键事件
            characters=characters,
            word_count=word_count
        )

        # 更新摘要列表（保持最新的N个摘要）
        self.chapter_summaries.append(summary)
        max_summaries = 50  # 最多保留50个章节摘要
        if len(self.chapter_summaries) > max_summaries:
            self.chapter_summaries = self.chapter_summaries[-max_summaries:]

        # 更新角色最后出现时间
        for char in characters:
            if char in self.character_states:
                self.character_states[char].last_appearance_chapter = chapter_num

        self._save_memory()
        return summary

    def update_character_state(self, chapter_num: int, character_name: str, **kwargs):
        """
        更新角色状态

        Args:
            chapter_num: 当前章节号
            character_name: 角色名称
            **kwargs: 状态更新参数
        """
        if character_name not in self.character_states:
            self.character_states[character_name] = CharacterState(name=character_name)

        self.character_states[character_name].update_state(chapter_num, **kwargs)
        self._save_memory()

    def add_plot_event(self, chapter_num: int, event_type: str,
                       description: str, characters: List[str], keywords: List[str]):
        """
        添加剧情事件

        Args:
            chapter_num: 章节号
            event_type: 事件类型（伏笔、高潮、转折、揭晓等）
            description: 事件描述
            characters: 涉及角色
            keywords: 关键词
        """
        event = PlotEvent(
            chapter=chapter_num,
            event_type=event_type,
            description=description,
            characters=characters,
            keywords=keywords + [event_type]
        )

        self.plot_events.append(event)
        # 最多保留100个事件
        if len(self.plot_events) > 100:
            self.plot_events = self.plot_events[-100:]

        self._save_memory()

    def get_relevant_context(self, chapter_num: int, max_chapters: int = 5,
                          character_names: List[str] = None) -> str:
        """
        获取相关上下文

        Args:
            chapter_num: 当前章节号
            max_chapters: 最多返回多少章的上下文
            character_names: 指定角色名，优先返回相关内容

        Returns:
            上下文文本
        """
        context_parts = []

        # 1. 获取最近章节摘要
        relevant_summaries = [
            s for s in self.chapter_summaries
            if 0 <= (chapter_num - s.chapter) <= max_chapters
        ]
        relevant_summaries.sort(key=lambda x: x.chapter, reverse=True)

        if relevant_summaries:
            context_parts.append("## 之前章节摘要：")
            for s in relevant_summaries[:3]:  # 最多3个章节摘要
                context_parts.append(f"第{s.chapter}章 {s.title}: {s.summary}")

        # 2. 获取相关剧情事件
        if character_names:
            # 优先返回指定角色相关的事件
            relevant_events = [
                e for e in self.plot_events
                if e.chapter < chapter_num and any(c in e.characters for c in character_names)
            ]
        else:
            # 返回最近的事件
            relevant_events = [e for e in self.plot_events if e.chapter < chapter_num][-5:]

        if relevant_events:
            context_parts.append("\n## 相关剧情事件：")
            for e in relevant_events:
                context_parts.append(f"- 第{e.chapter}章: {e.description}")

        # 3. 获取角色状态
        if character_names:
            context_parts.append("\n## 角色当前状态：")
            for name in character_names:
                if name in self.character_states:
                    state = self.character_states[name]
                    context_parts.append(f"- {name}: 位置={state.current_location or '未知'}, "
                                   f"状态={state.status}")
                    if state.relationships:
                        context_parts.append(f"  关系: {state.relationships}")
                    if state.attributes:
                        context_parts.append(f"  属性: {state.attributes}")

        return "\n".join(context_parts) if context_parts else "暂无相关上下文"

    def get_character_info(self, character_name: str) -> Optional[CharacterState]:
        """获取角色信息"""
        return self.character_states.get(character_name)

    def search_by_keyword(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """
        按关键词搜索记忆

        Args:
            keyword: 搜索关键词
            max_results: 最大返回结果数

        Returns:
            匹配结果列表，每个元素包含type, chapter, description
        """
        results = []

        # 搜索章节摘要
        for summary in self.chapter_summaries:
            if keyword.lower() in summary.to_search_text().lower():
                results.append({
                    "type": "章节",
                    "chapter": summary.chapter,
                    "title": summary.title,
                    "summary": summary.summary[:100]
                })

        # 搜索剧情事件
        for event in self.plot_events:
            if keyword.lower() in event.to_search_text().lower():
                results.append({
                    "type": "事件",
                    "chapter": event.chapter,
                    "event_type": event.event_type,
                    "description": event.description
                })

        # 搜索角色状态
        for name, state in self.character_states.items():
            if keyword.lower() in name.lower():
                results.append({
                    "type": "角色",
                    "name": name,
                    "location": state.current_location,
                    "status": state.status
                })

        return results[:max_results]

    def resolve_foreshadow(self, chapter_num: int, foreshadow_keywords: List[str]):
        """
        揭示伏笔

        Args:
            chapter_num: 当前章节号
            foreshadow_keywords: 伏笔关键词列表
        """
        resolved_count = 0
        for event in self.plot_events:
            if event.chapter < chapter_num and not event.resolved:
                # 检查是否有伏笔关键词
                if any(kw.lower() in event.description.lower() for kw in foreshadow_keywords):
                    event.resolved = True
                    resolved_count += 1

        if resolved_count > 0:
            self._save_memory()
            return resolved_count
        return 0

    def get_statistics(self) -> Dict:
        """获取记忆统计信息"""
        return {
            "total_chapters": len(self.chapter_summaries),
            "total_events": len(self.plot_events),
            "total_characters": len(self.character_states),
            "memory_file_size_kb": self.memory_file.stat().st_size / 1024 if self.memory_file.exists() else 0
        }
