# 配置管理
import os

# 写作配置
WRITING_CONFIG = {
    "min_words": 3000,      # 最小字数
    "target_words": 4000,    # 目标字数
    "max_words": 5000,       # 最大字数
    "temperature": 0.7,      # 创作温度
    "max_tokens": 8000,      # 最大token
    "max_revisions": 3,      # 最大修正次数（提升到3）
}

# API配置
API_CONFIG = {
    "model": "glm-4.7",
    "api_key": os.getenv("GLM_API_KEY", ""),  # 从环境变量读取，请在.env文件或系统环境变量中设置
    "timeout": 300,  # 5分钟
    "max_retries": 3,
    "retry_delay": 5,
}

# 高级功能配置
ADVANCED_CONFIG = {
    # 记忆系统
    "enable_memory": True,           # 是否启用记忆系统
    "memory_max_chapters": 50,       # 记忆系统保留的最大章节数
    "enable_character_tracking": True,  # 是否启用角色状态追踪

    # 一致性检查
    "enable_consistency_check": True,  # 是否启用一致性检查
    "consistency_check_after_revision": True,  # 修正后是否重新检查一致性

    # 人工介入
    "semi_auto_mode": False,        # 半自动模式（生成后等待确认）
    "show_diff_on_revision": True,  # 修正时显示修改对比

    # 提示词系统
    "prompt_template_set": "default",  # 当前使用的提示词模板集
    "enable_prompt_ab_test": False,  # 是否启用A/B测试

    # 版本控制
    "enable_version_control": True,  # 是否启用版本控制
    "max_history_versions": 10,     # 每个章节保留的最大历史版本数
}

# 可用模型列表
AVAILABLE_MODELS = {
    "glm-4.7": "智谱GLM-4.7（推荐）",
    "glm-4-plus": "智谱GLM-4-Plus",
    "glm-4-air": "智谱GLM-4-Air",
    "glm-4-flash": "智谱GLM-4-Flash",
}

# 24/7模式配置
AUTO_MODE_CONFIG = {
    "enabled": True,
    "target_chapters": None,  # None=无限
    "max_consecutive_errors": 3,
    "heartbeat_interval": 30,
}

# 小说文件夹结构配置
NOVEL_STRUCTURE = {
    "settings_dir": "设定",
    "chapters_dir": "章节",
    "outline_file": "大纲.md",
    "character_file": "角色设定.md",
    "skill_file": "技能体系.md",
    "worldview_file": "世界观设定.md",
}


def get_config():
    """
    获取配置（支持从环境变量或配置文件覆盖）

    Returns:
        配置字典合并结果
    """
    import os
    from pathlib import Path
    import json

    config = {
        "WRITING_CONFIG": WRITING_CONFIG,
        "API_CONFIG": API_CONFIG,
        "ADVANCED_CONFIG": ADVANCED_CONFIG,
        "AUTO_MODE_CONFIG": AUTO_MODE_CONFIG,
        "AVAILABLE_MODELS": AVAILABLE_MODELS,
    }

    # 尝试从项目根目录的配置文件加载
    local_config_path = Path(__file__).parent / "local_config.json"
    if local_config_path.exists():
        try:
            with open(local_config_path, 'r', encoding='utf-8') as f:
                local_config = json.load(f)
                # 递归合并配置
                for section, values in local_config.items():
                    if section in config:
                        config[section].update(values)
        except Exception as e:
            print(f"警告: 加载本地配置文件失败: {e}")

    # 环境变量覆盖（最高优先级）
    if os.getenv("GLM_API_KEY"):
        config["API_CONFIG"]["api_key"] = os.getenv("GLM_API_KEY")
    if os.getenv("GLM_MODEL"):
        config["API_CONFIG"]["model"] = os.getenv("GLM_MODEL")

    return config


def save_local_config(config_section: str, config_values: dict):
    """
    保存本地配置（覆盖默认值）

    Args:
        config_section: 配置节名称（如"ADVANCED_CONFIG"）
        config_values: 要保存的配置值字典
    """
    from pathlib import Path
    import json

    local_config_path = Path(__file__).parent / "local_config.json"

    # 加载现有配置
    existing_config = {}
    if local_config_path.exists():
        try:
            with open(local_config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
        except Exception:
            existing_config = {}

    # 更新配置
    existing_config[config_section] = config_values

    # 保存
    with open(local_config_path, 'w', encoding='utf-8') as f:
        json.dump(existing_config, f, ensure_ascii=False, indent=2)

    print(f"配置已保存到: {local_config_path}")
