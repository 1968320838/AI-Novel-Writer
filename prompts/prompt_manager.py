"""
提示词模板管理器
支持Jinja2模板，变量注入，版本切换
"""

from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader, select_autoescape


class PromptManager:
    """提示词管理器"""

    def __init__(self, template_dir: Optional[Path] = None):
        """
        初始化提示词管理器

        Args:
            template_dir: 模板目录路径
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"

        self.template_dir = Path(template_dir)

        # 创建Jinja2环境
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['j2']),
            trim_blocks=True,
            keep_trailing_newline=True
        )

        # 当前模板集
        self.current_set = "default"

        # 缓存编译后的模板
        self._template_cache: Dict[str, Template] = {}

    def get_template(self, template_name: str) -> Template:
        """
        获取模板（带缓存）

        Args:
            template_name: 模板名称（如'writing_system'）

        Returns:
            编译后的Jinja2模板
        """
        if template_name not in self._template_cache:
            template_path = self.template_dir / f"{template_name}.txt.j2"
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                self._template_cache[template_name] = self.env.from_string(template_content)
            else:
                # 如果模板文件不存在，使用内置默认模板
                self._template_cache[template_name] = self.env.from_string(self._get_builtin_template(template_name))

        return self._template_cache[template_name]

    def render_prompt(self, template_name: str, **context) -> str:
        """
        渲染提示词

        Args:
            template_name: 模板名称
            **context: 模板变量

        Returns:
            渲染后的提示词文本
        """
        template = self.get_template(template_name)
        return template.render(**context)

    def _get_builtin_template(self, template_name: str) -> str:
        """
        获取内置默认模板

        Args:
            template_name: 模板名称

        Returns:
            默认模板内容
        """
        templates = {
            "writing_system": """你是一位专业的网络小说作家，擅长写作"{{genre}}"类型的小说。

你的写作风格特点：
1. 节奏明快，爽点密集
2. 人物性格鲜明，对话生动
3. 诡异场景描写细腻，氛围感强
4. 善于制造悬念和反转
5. 文笔流畅，不拖沓

写作要求：
1. 每章{{min_words}}-{{max_words}}字
2. 保持角色性格一致
3. 严格按大纲推进剧情
4. 包含对话、动作、心理描写
5. 使用系统公告格式：【...】
6. 使用直播弹幕增强代入感

请严格按照指定格式输出章节内容。""",

            "writing_user": """请根据以下信息写作第{{chapter_number}}章：《{{chapter_title}}》

---

## 【大纲信息】

{{chapter_plan|truncate(1000) or '请根据上下文继续推进剧情'}}

---

## 【角色设定】

{{character_summary}}

---

## 【世界观设定】

{{worldview_summary}}

---

## 【上一章结尾】

{{prev_summary}}

---

## 【写作要求】

1. 字数要求：{{target_words}}-{{max_words}}字
2. 保持主角{{protagonist_name}}的性格：{{protagonist_personality}}
3. 按大纲推进剧情，如有需要可以适当发挥
4. 包含对话和动作描写
5. 结尾留下悬念，预示下一章内容

## 【输出格式】

请按以下格式输出：

```
# 第{{chapter_number}}章 {{chapter_title}}

[正文内容，3000-5000字]

---

**下章预告：**

[下一章的简短预告，100字左右]

敬请期待第{{chapter_number + 1}}章：《[下章标题]》

---

**本章字数：约[字数]字**

**核心看点：**
- [看点1]
- [看点2]
- [看点3]
```

请开始创作：""",

            "review_system": """你是一位专业的网络小说编辑，负责审核"{{genre}}"类型小说的章节质量。

你的职责是仔细检查章节中可能存在的问题，包括：
1. 逻辑一致性 - 剧情是否合理，前后是否矛盾
2. 角色一致性 - 角色行为是否符合设定
3. 剧情推进 - 是否有效推进主线剧情
4. 文字质量 - 用词、描写是否到位

请以JSON格式返回审核结果。""",

            "revision_system": """你是一位专业的小说编辑，负责修正章节中的问题。

修正原则：
1. 保持原有风格和语调
2. 只修正指出的问题，不大幅改动其他内容
3. 保持剧情连贯性
4. 尊重原作意图

请根据反馈的问题进行精准修正。""",
        }

        return templates.get(template_name, "")

    def list_available_sets(self) -> Dict[str, str]:
        """列出可用的模板集"""
        return {
            "default": "默认模板集",
        }

    def reload_templates(self):
        """重新加载模板（清除缓存）"""
        self._template_cache.clear()
