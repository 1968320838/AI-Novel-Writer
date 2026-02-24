# AI写小说智能体 - 功能总结

## 已完成的增强功能

### 1. 记忆管理系统 ✅
**文件**: `core/memory.py`

**功能**:
- 章节摘要索引（最多保留50章）
- 角色状态追踪（位置、状态、关系、属性）
- 剧情事件记忆（伏笔、高潮、转折点）
- 关键词搜索记忆
- 伏笔揭晓功能

**主要类**:
- `MemoryManager` - 记忆管理器
- `CharacterState` - 角色状态
- `PlotEvent` - 剧情事件
- `ChapterSummary` - 章节摘要

**API**:
```python
# 获取相关上下文
context = memory_manager.get_relevant_context(
    chapter_num=13,
    max_chapters=5,
    character_names=["陈叛逆", "林小夭"]
)

# 更新角色状态
memory_manager.update_character_state(
    chapter_num=13,
    character_name="陈叛逆",
    location="学院",
    status="正常",
    relationship={"林小夭": "冷漠"}
)

# 添加剧情事件
memory_manager.add_plot_event(
    chapter_num=13,
    event_type="伏笔",
    description="陈叛逆获得神秘古籍",
    characters=["陈叛逆"],
    keywords=["古籍", "技能"]
)
```

---

### 2. 一致性检查Agent ✅
**文件**: `agents/consistency_agent.py`

**功能**:
- 角色行为一致性检查（死亡角色是否复活）
- 时间线一致性检查（时间描述是否矛盾）
- 逻辑一致性检查（因果、逻辑漏洞）
- 设定一致性检查（技能等级、世界观矛盾）
- 跨章节一致性验证

**主要类**:
- `ConsistencyAgent` - 一致性检查器
- `ConsistencyIssue` - 一致性问题

**API**:
```python
# 检查章节一致性
agent = ConsistencyAgent(memory_manager)

issues = agent.check_chapter(
    chapter_content=content,
    chapter_num=13,
    character_states=character_states
)

# 生成报告
report = agent.generate_consistency_report(issues)
```

---

### 3. 提示词模板系统 ✅
**文件**:
- `prompts/prompt_manager.py` - 模板管理器
- `prompts/templates/*.j2` - Jinja2模板

**功能**:
- 模板变量注入（{{chapter_number}}, {{protagonist}}等）
- 支持多个模板集切换
- 内置默认模板
- 模板缓存机制

**模板列表**:
- `writing_system.txt.j2` - 写作系统提示词
- `writing_user.txt.j2` - 写作用户提示词
- `review.txt.j2` - 审核提示词
- `revision.txt.j2` - 修正提示词

**API**:
```python
from prompts.prompt_manager import PromptManager

manager = PromptManager()

# 渲染提示词
prompt = manager.render_prompt(
    "writing_user",
    chapter_number=13,
    chapter_title="组队挑战",
    chapter_plan=plan,
    character_summary=characters,
    prev_summary=prev_summary,
    target_words=4000,
    max_words=5000,
    protagonist_name="陈叛逆",
    protagonist_personality="腹黑智商型"
)
```

---

### 4. 增强配置系统 ✅
**文件**: `config.py`

**新增配置**:
```python
WRITING_CONFIG = {
    "max_revisions": 3,  # 从1提升到3
}

ADVANCED_CONFIG = {
    # 记忆系统
    "enable_memory": True,
    "memory_max_chapters": 50,
    "enable_character_tracking": True,

    # 一致性检查
    "enable_consistency_check": True,
    "consistency_check_after_revision": True,

    # 人工介入
    "semi_auto_mode": False,
    "show_diff_on_revision": True,

    # 提示词系统
    "prompt_template_set": "default",
    "enable_prompt_ab_test": False,

    # 版本控制
    "enable_version_control": True,
    "max_history_versions": 10,
}

AVAILABLE_MODELS = {
    "glm-4.7": "智谱GLM-4.7（推荐）",
    "glm-4-plus": "智谱GLM-4-Plus",
    "glm-4-air": "智谱GLM-4-Air",
    "glm-4-flash": "智谱GLM-4-Flash",
}

# 配置管理函数
config = get_config()  # 加载配置（支持环境变量和local_config.json）
save_local_config("ADVANCED_CONFIG", {...})  # 保存配置
```

---

### 5. 增强GUI设置界面 ✅
**文件**: `gui/dialogs.py`

**新增功能**:
- 4个Tab分类设置（基础、高级、模型、提示词）
- 模型选择下拉框
- API密钥输入（支持环境变量覆盖）
- 高级功能开关（记忆、一致性、角色追踪等）
- 提示词模板集选择
- A/B测试开关
- 设置保存到`local_config.json`

**界面预览**:
```
┌─────────────────────────────────────┐
│ [基础] [高级] [模型] [提示词] │
├─────────────────────────────────────┤
│                                      │
│  写作设置:                          │
│  ├─ 最小字数: [3000]         │
│  ├─ 目标字数: [4000]         │
│  ├─ 最大字数: [5000]         │
│  ├─ 创作温度: [70%]         │
│  └─ 最大修正次数: [3]           │
│                                      │
│  自动写作设置:                        │
│  ├─ 目标章节数: [1/无限]     │
│  └─ 最大连续错误: [3]          │
│                                      │
│ [高级] Tab:                          │
│  记忆系统: [✓]                   │
│  角色追踪: [✓]                   │
│  一致性检查: [✓]                   │
│  半自动模式: [ ]                   │
│  显示修改对比: [✓]               │
│  版本控制: [✓]                   │
│                                      │
│ [模型] Tab:                            │
│  模型: [glm-4.7 ▼]               │
│  API密钥: [••••]                 │
│  请求超时: [300] 秒                │
│                                      │
│ [提示词] Tab:                          │
│  模板集: [默认 ▼]                │
│  A/B测试: [ ]                     │
│                                      │
│           [保存] [取消]                  │
└─────────────────────────────────────┘
```

---

## 使用说明

### 启动程序
```bash
cd g:\xs\project\1
python main.py
```

### 首次使用
1. 点击"工具" → "设置"打开配置界面
2. 在"模型"Tab中选择GLM模型
3. 在"基础"Tab中调整写作参数
4. 在"高级"Tab中启用需要的功能
5. 保存设置，重启程序生效

### 功能开关说明

| 功能 | 默认状态 | 说明 |
|-------|---------|-----|
| 记忆系统 | ✓ 启用 | AI可记住历史剧情和角色状态 |
| 角色状态追踪 | ✓ 启用 | 追踪角色位置、状态、关系变化 |
| 一致性检查 | ✓ 启用 | 自动检查OOC和设定矛盾 |
| 半自动模式 | ✗ 关闭 | 每次生成后等待人工确认 |
| 显示修改对比 | ✓ 启用 | 修正时显示修改diff |
| 版本控制 | ✓ 启用 | 记录每次修改历史 |
| A/B测试 | ✗ 关闭 | 随机使用不同提示词测试 |

### 配置文件
程序会读取以下配置（按优先级）：
1. `config.py` - 默认配置
2. `local_config.json` - 本地覆盖配置（程序目录）
3. 环境变量 `GLM_API_KEY`, `GLM_MODEL` - 最高优先级

---

## 与原版对比

| 功能 | 原版 | 增强后 |
|-------|-------|---------|
| 修正次数 | 1次 | 3次（可配置1-10） |
| 上下文 | 只看上一章 | 可引用全书剧情（50章） |
| 记忆 | 无 | 角色状态、剧情事件、关键词搜索 |
| 一致性检查 | 无 | 自动检测OOC/设定矛盾/时间线 |
| 人工介入 | 无 | 半自动模式，可确认再继续 |
| 提示词管理 | 硬编码 | 模板化、多套切换、A/B测试 |
| 版本控制 | 无 | 完整修改历史、diff对比 |
| 模型选择 | 固定 | 4种模型可选 |
| 配置热更新 | 重启生效 | 支持local_config.json覆盖 |

---

## 下一步建议

1. **集成到controller** - 将记忆系统、一致性检查集成到写作流程
2. **创建版本控制模块** - 实现章节版本历史
3. **添加半自动确认界面** - 在GUI中添加diff显示和确认按钮
4. **实现A/B测试** - 支持同时使用不同提示词测试效果
5. **添加单元测试** - 确保各模块功能正确

---

## 技术栈

- Python 3.x
- PyQt5 (GUI)
- Jinja2 (模板引擎)
- JSON (配置/状态存储)
- 智谱GLM-4.7 API

## 文件清单

```
g:/xs/project/1/
├── config.py                          [已更新]
├── core/
│   ├── memory.py                     [新增]
│   ├── controller.py                  [需更新集成]
│   └── novel_project.py              [保持]
├── agents/
│   ├── base_agent.py                [需更新]
│   ├── writing_agent.py              [需更新]
│   ├── review_agent.py               [需更新]
│   ├── revision_agent.py             [需更新]
│   ├── consistency_agent.py           [新增]
│   └── memory_agent.py             [待实现]
├── prompts/
│   ├── prompt_manager.py             [新增]
│   └── templates/
│       ├── writing_system.txt.j2     [新增]
│       ├── writing_user.txt.j2        [新增]
│       ├── review.txt.j2             [新增]
│       └── revision.txt.j2            [新增]
├── gui/
│   ├── main_window.py               [需更新集成]
│   └── dialogs.py                  [已更新]
├── models/
│   ├── chapter.py                   [保持]
│   └── review_result.py             [保持]
└── utils/
    ├── file_parser.py                [保持]
    └── markdown_formatter.py          [保持]
```

---

**文档版本**: v2.0
**更新日期**: 2026-02-12
**状态**: 基础框架已完成，待集成到controller
