# 24小时自动写小说智能体

基于大语言模型的智能小说写作系统，支持自动写作、审核、修正全流程。

## 功能特点

- 自动写作：根据大纲自动生成章节内容
- 智能审核：多维度审核章节质量（逻辑、角色、剧情、文字）
- 自动修正：根据审核反馈自动修正问题
- 记忆系统：AI可记住历史剧情和角色状态
- 一致性检查：自动检测OOC、设定矛盾、时间线问题
- 提示词模板：支持多套模板切换、A/B测试

## 技术栈

- Python 3.x
- PyQt5（GUI界面）
- Jinja2（提示词模板）
- 智谱GLM-4.7 API

## 项目结构

```
project/
├── main.py                 # 程序入口
├── config.py               # 配置管理
├── agents/                 # Agent模块
│   ├── base_agent.py       # Agent基类
│   ├── writing_agent.py    # 写作Agent
│   ├── review_agent.py     # 审核Agent
│   ├── revision_agent.py   # 修正Agent
│   └── consistency_agent.py # 一致性检查Agent
├── api/                    # API模块
│   └── glm_client.py       # GLM客户端
├── core/                   # 核心模块
│   ├── controller.py       # 控制器
│   ├── novel_project.py    # 项目管理
│   └── memory.py           # 记忆管理
├── models/                 # 数据模型
│   ├── chapter.py          # 章节模型
│   └── review_result.py    # 审核结果模型
├── prompts/                # 提示词模块
│   ├── prompt_manager.py   # 模板管理器
│   └── templates/          # Jinja2模板
├── gui/                    # GUI模块
│   ├── main_window.py      # 主窗口
│   └── dialogs.py          # 对话框
└── utils/                  # 工具类
    ├── file_parser.py      # 文件解析
    └── markdown_formatter.py # 格式化工具
```

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/your-username/ai-novel-writer.git
cd ai-novel-writer
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API密钥

方式一：设置环境变量（推荐）

```bash
# Windows
set GLM_API_KEY=your_api_key_here

# Linux/Mac
export GLM_API_KEY=your_api_key_here
```

方式二：修改 `config.py`

```python
API_CONFIG = {
    "model": "glm-4.7",
    "api_key": "your_api_key_here",  # 替换为你的API密钥
    "timeout": 300,
    "max_retries": 3,
    "retry_delay": 5,
}
```

方式三：使用GUI配置

启动程序后，点击"工具" → "设置"，在"模型"标签页中配置API密钥。

## 使用方法

### 启动程序

```bash
python main.py
```

### 导入小说

1. 准备小说文件夹，结构如下：

```
小说名称/
├── 设定/
│   ├── 大纲.md           # 章节大纲
│   ├── 角色设定.md       # 角色信息
│   ├── 技能体系.md       # 技能设定
│   └── 世界观设定.md     # 世界观
└── 章节/
    └── 第一卷/
        ├── 第1章-标题.md
        ├── 第2章-标题.md
        └── ...
```

2. 点击"导入"按钮，选择小说文件夹

### 开始写作

1. 导入小说后，点击"开始"按钮
2. 设置目标章节数（可选）
3. 程序将自动开始写作、审核、修正

### 单章写作

点击"写一章"按钮，只写作一章后停止。

## 配置说明

### 基础配置

| 配置项 | 默认值 | 说明 |
|-------|-------|------|
| min_words | 3000 | 最小字数 |
| target_words | 4000 | 目标字数 |
| max_words | 5000 | 最大字数 |
| temperature | 0.7 | 创作温度（0-1） |
| max_revisions | 3 | 最大修正次数 |

### 高级配置

| 配置项 | 默认值 | 说明 |
|-------|-------|------|
| enable_memory | True | 启用记忆系统 |
| enable_consistency_check | True | 启用一致性检查 |
| enable_character_tracking | True | 启用角色状态追踪 |
| semi_auto_mode | False | 半自动模式（生成后等待确认） |
| enable_version_control | True | 启用版本控制 |

### 支持的模型

- glm-5（推荐）
- glm-4.7（推荐）
- glm-4-plus
- glm-4-air
- glm-4-flash

## 大纲格式示例

```markdown
# 小说大纲

## 第一卷：觉醒与首秀（1-50章）

**第1章：全员SSR，只有我抽到F**
- 全球觉醒直播，每个人抽取天赋技能
- 主角抽到F级技能，全网嘲笑

**第2章：F班的欢迎仪式**
- 觉醒者学院分班仪式
- 主角被分到F班

**第3-5章：首场诡异挑战**
- 进入诡异场景【深夜便利店】
- 用特殊方式通关
```

## 工作流程

```
┌─────────────┐
│  写作章节    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  一致性检查  │ ← 可选
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   审核章节   │
└──────┬──────┘
       │
       ▼
┌─────────────┐    有问题    ┌─────────────┐
│  是否通过？  │────────────→│   修正章节   │
└──────┬──────┘              └──────┬──────┘
       │ 通过                       │
       │                            │
       ▼                            ▼
┌─────────────┐              ┌─────────────┐
│   保存章节   │              │  重新审核   │
└─────────────┘              └─────────────┘
```

## 注意事项

1. API调用需要网络连接
2. 建议使用代理或VPN以获得稳定的API访问
3. 首次使用请确保配置正确的API密钥
4. 生成的章节会自动保存到小说文件夹

## 开发计划

- [ ] 支持更多LLM模型（Claude、GPT等）
- [ ] 添加章节编辑器
- [ ] 实现多人协作写作
- [ ] 添加导出功能（PDF、EPUB）
- [ ] 优化记忆系统（向量数据库）

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 致谢

- 智谱AI GLM-4.7
- PyQt5
- Jinja2
