"""
对话框组件
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QSpinBox, QFileDialog,
                             QGroupBox, QFormLayout, QComboBox, QMessageBox,
                             QCheckBox, QTabWidget, QWidget, QSlider)
from PyQt5.QtCore import Qt

from config import (WRITING_CONFIG, API_CONFIG, ADVANCED_CONFIG,
                 AUTO_MODE_CONFIG, AVAILABLE_MODELS)


class ImportDialog(QDialog):
    """导入小说对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.novel_path = ""
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        self.setWindowTitle("导入小说")
        self.setModal(True)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # 说明
        info_label = QLabel("请选择小说文件夹，文件夹应包含\"设定\"和\"章节\"子文件夹")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # 路径输入
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("选择小说文件夹...")
        self.path_edit.setReadOnly(True)
        path_layout.addWidget(self.path_edit)

        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self._browse_folder)
        path_layout.addWidget(browse_btn)

        layout.addLayout(path_layout)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_btn = QPushButton("导入")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _browse_folder(self):
        """浏览文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择小说文件夹")
        if folder:
            self.novel_path = folder
            self.path_edit.setText(folder)

    def get_novel_path(self) -> str:
        """获取小说路径"""
        return self.novel_path


class SettingsDialog(QDialog):
    """设置对话框 - 增强版"""

    def __init__(self, parent=None, current_config=None):
        super().__init__(parent)
        self.mode = "settings"  # settings or auto
        self.current_config = current_config or {}
        self._settings = {}
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        self.setWindowTitle("设置")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        main_layout = QVBoxLayout(self)

        # 使用Tab分类配置
        tab_widget = QTabWidget()
        tab_widget.addTab(self._create_basic_tab(), "基础")
        tab_widget.addTab(self._create_advanced_tab(), "高级")
        tab_widget.addTab(self._create_model_tab(), "模型")
        tab_widget.addTab(self._create_prompt_tab(), "提示词")

        main_layout.addWidget(tab_widget)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_btn = QPushButton("保存")
        ok_btn.clicked.connect(self._save_and_accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        main_layout.addLayout(button_layout)

    def _create_basic_tab(self) -> QWidget:
        """创建基础设置Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 写作设置组
        writing_group = QGroupBox("写作设置")
        writing_layout = QFormLayout(writing_group)

        self.min_words_spin = QSpinBox()
        self.min_words_spin.setRange(1000, 10000)
        self.min_words_spin.setValue(WRITING_CONFIG["min_words"])
        self.min_words_spin.setSuffix(" 字")
        writing_layout.addRow("最小字数:", self.min_words_spin)

        self.target_words_spin = QSpinBox()
        self.target_words_spin.setRange(1000, 10000)
        self.target_words_spin.setValue(WRITING_CONFIG["target_words"])
        self.target_words_spin.setSuffix(" 字")
        writing_layout.addRow("目标字数:", self.target_words_spin)

        self.max_words_spin = QSpinBox()
        self.max_words_spin.setRange(1000, 20000)
        self.max_words_spin.setValue(WRITING_CONFIG["max_words"])
        self.max_words_spin.setSuffix(" 字")
        writing_layout.addRow("最大字数:", self.max_words_spin)

        self.temperature_spin = QSpinBox()
        self.temperature_spin.setRange(1, 100)
        self.temperature_spin.setValue(int(WRITING_CONFIG["temperature"] * 100))
        self.temperature_spin.setSuffix("%")
        writing_layout.addRow("创作温度:", self.temperature_spin)

        self.max_revisions_spin = QSpinBox()
        self.max_revisions_spin.setRange(1, 10)
        self.max_revisions_spin.setValue(WRITING_CONFIG["max_revisions"])
        self.max_revisions_spin.setToolTip("最多修正次数，1-10次")
        writing_layout.addRow("最大修正次数:", self.max_revisions_spin)

        layout.addWidget(writing_group)

        # 自动模式设置组
        auto_group = QGroupBox("自动写作设置")
        auto_layout = QFormLayout(auto_group)

        self.target_chapters_spin = QSpinBox()
        self.target_chapters_spin.setRange(1, 1000)
        self.target_chapters_spin.setValue(AUTO_MODE_CONFIG.get("target_chapters", 0) or 0)
        self.target_chapters_spin.setSpecialValueText("无限")
        auto_layout.addRow("目标章节数:", self.target_chapters_spin)

        self.max_errors_spin = QSpinBox()
        self.max_errors_spin.setRange(1, 20)
        self.max_errors_spin.setValue(AUTO_MODE_CONFIG["max_consecutive_errors"])
        auto_layout.addRow("最大连续错误:", self.max_errors_spin)

        layout.addWidget(auto_group)
        layout.addStretch()

        return widget

    def _create_advanced_tab(self) -> QWidget:
        """创建高级设置Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 功能开关组
        features_group = QGroupBox("功能开关")
        features_layout = QFormLayout(features_group)

        # 记忆系统
        self.enable_memory_check = QCheckBox("启用记忆系统")
        self.enable_memory_check.setChecked(ADVANCED_CONFIG.get("enable_memory", True))
        self.enable_memory_check.setToolTip("让AI记住历史剧情和角色状态")
        features_layout.addRow(self.enable_memory_check)

        self.memory_chapters_spin = QSpinBox()
        self.memory_chapters_spin.setRange(10, 200)
        self.memory_chapters_spin.setValue(ADVANCED_CONFIG.get("memory_max_chapters", 50))
        self.memory_chapters_spin.setSuffix(" 章")
        features_layout.addRow("记忆保留章节数:", self.memory_chapters_spin)

        # 一致性检查
        self.enable_consistency_check = QCheckBox("启用一致性检查")
        self.enable_consistency_check.setChecked(ADVANCED_CONFIG.get("enable_consistency_check", True))
        self.enable_consistency_check.setToolTip("自动检查角色行为、设定、时间线的一致性")
        features_layout.addRow(self.enable_consistency_check)

        # 角色追踪
        self.enable_char_tracking_check = QCheckBox("启用角色状态追踪")
        self.enable_char_tracking_check.setChecked(ADVANCED_CONFIG.get("enable_character_tracking", True))
        features_layout.addRow(self.enable_char_tracking_check)

        # 半自动模式
        self.semi_auto_check = QCheckBox("半自动模式（生成后等待确认）")
        self.semi_auto_check.setChecked(ADVANCED_CONFIG.get("semi_auto_mode", False))
        self.semi_auto_check.setToolTip("每次生成后暂停，等待人工确认后再继续")
        features_layout.addRow(self.semi_auto_check)

        # 显示diff
        self.show_diff_check = QCheckBox("显示修改对比")
        self.show_diff_check.setChecked(ADVANCED_CONFIG.get("show_diff_on_revision", True))
        features_layout.addRow(self.show_diff_check)

        # 版本控制
        self.enable_version_check = QCheckBox("启用版本控制")
        self.enable_version_check.setChecked(ADVANCED_CONFIG.get("enable_version_control", True))
        self.enable_version_check.setToolTip("记录每次修改的历史版本")
        features_layout.addRow(self.enable_version_check)

        self.max_versions_spin = QSpinBox()
        self.max_versions_spin.setRange(5, 50)
        self.max_versions_spin.setValue(ADVANCED_CONFIG.get("max_history_versions", 10))
        self.max_versions_spin.setSuffix(" 个版本")
        features_layout.addRow("每章保留版本:", self.max_versions_spin)

        layout.addWidget(features_group)
        layout.addStretch()

        return widget

    def _create_model_tab(self) -> QWidget:
        """创建模型设置Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # API配置组
        api_group = QGroupBox("API配置")
        api_layout = QFormLayout(api_group)

        # 模型选择
        self.model_combo = QComboBox()
        for model_id, model_desc in AVAILABLE_MODELS.items():
            self.model_combo.addItem(model_desc, model_id)
        current_model = API_CONFIG.get("model", "glm-4.7")
        index = self.model_combo.findData(current_model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        api_layout.addRow("模型:", self.model_combo)

        # API密钥
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setText(API_CONFIG.get("api_key", ""))
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("留空使用默认密钥")
        api_layout.addRow("API密钥:", self.api_key_edit)

        # 超时设置
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(30, 600)
        self.timeout_spin.setValue(API_CONFIG.get("timeout", 300))
        self.timeout_spin.setSuffix(" 秒")
        api_layout.addRow("请求超时:", self.timeout_spin)

        # 重试设置
        self.max_retries_spin = QSpinBox()
        self.max_retries_spin.setRange(1, 10)
        self.max_retries_spin.setValue(API_CONFIG.get("max_retries", 3))
        api_layout.addRow("最大重试:", self.max_retries_spin)

        # 重试延迟
        self.retry_delay_spin = QSpinBox()
        self.retry_delay_spin.setRange(1, 60)
        self.retry_delay_spin.setValue(API_CONFIG.get("retry_delay", 5))
        self.retry_delay_spin.setSuffix(" 秒")
        api_layout.addRow("重试延迟:", self.retry_delay_spin)

        layout.addWidget(api_group)
        layout.addStretch()

        # 说明文字
        info_label = QLabel(
            "<b>提示:</b> API密钥留空将使用config.py中的默认值。<br>"
            "修改模型后需要重启程序生效。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 10px; background: #f0f0f0; border-radius: 5px;")
        layout.addWidget(info_label)

        return widget

    def _create_prompt_tab(self) -> QWidget:
        """创建提示词设置Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 提示词配置组
        prompt_group = QGroupBox("提示词配置")
        prompt_layout = QFormLayout(prompt_group)

        self.template_set_combo = QComboBox()
        self.template_set_combo.addItem("默认模板", "default")
        self.template_set_combo.addItem("爽文模板", "cool_style")
        self.template_set_combo.addItem("悬疑模板", "suspense_style")
        self.template_set_combo.setCurrentIndex(0)
        prompt_layout.addRow("模板集:", self.template_set_combo)

        # A/B测试
        self.ab_test_check = QCheckBox("启用A/B测试")
        self.ab_test_check.setChecked(ADVANCED_CONFIG.get("enable_prompt_ab_test", False))
        self.ab_test_check.setToolTip("随机使用不同提示词模板，测试效果")
        prompt_layout.addRow(self.ab_test_check)

        layout.addWidget(prompt_group)
        layout.addStretch()

        # 说明
        info_label = QLabel(
            "<b>提示:</b> 不同模板集适用于不同风格。<br>"
            "A/B测试会在同一章节随机使用不同模板。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 10px; background: #f0f0f0; border-radius: 5px;")
        layout.addWidget(info_label)

        return widget

    def set_mode(self, mode: str):
        """设置对话框模式"""
        self.mode = mode
        if mode == "auto":
            self.setWindowTitle("开始自动写作")
        else:
            self.setWindowTitle("设置")

    def get_settings(self) -> dict:
        """
        获取所有设置

        Returns:
            设置字典
        """
        return {
            # 基础设置
            "min_words": self.min_words_spin.value(),
            "target_words": self.target_words_spin.value(),
            "max_words": self.max_words_spin.value(),
            "temperature": self.temperature_spin.value() / 100,
            "max_revisions": self.max_revisions_spin.value(),
            "target_chapters": self.target_chapters_spin.value() or None,
            "max_consecutive_errors": self.max_errors_spin.value(),

            # 高级功能
            "enable_memory": self.enable_memory_check.isChecked(),
            "memory_max_chapters": self.memory_chapters_spin.value(),
            "enable_consistency_check": self.enable_consistency_check.isChecked(),
            "enable_character_tracking": self.enable_char_tracking_check.isChecked(),
            "semi_auto_mode": self.semi_auto_check.isChecked(),
            "show_diff_on_revision": self.show_diff_check.isChecked(),
            "enable_version_control": self.enable_version_check.isChecked(),
            "max_history_versions": self.max_versions_spin.value(),

            # 模型设置
            "model": self.model_combo.currentData(),
            "api_key": self.api_key_edit.text() or None,
            "timeout": self.timeout_spin.value(),
            "max_retries": self.max_retries_spin.value(),
            "retry_delay": self.retry_delay_spin.value(),

            # 提示词
            "prompt_template_set": self.template_set_combo.currentData(),
            "enable_prompt_ab_test": self.ab_test_check.isChecked(),
        }

    def _save_and_accept(self):
        """保存设置并关闭"""
        settings = self.get_settings()

        # 应用设置到配置
        from config import save_local_config

        # 保存API配置
        api_config = {
            "model": settings["model"],
            "timeout": settings["timeout"],
            "max_retries": settings["max_retries"],
            "retry_delay": settings["retry_delay"],
        }
        if settings["api_key"]:
            api_config["api_key"] = settings["api_key"]

        save_local_config("API_CONFIG", api_config)

        # 保存写作配置
        writing_config = {
            "min_words": settings["min_words"],
            "target_words": settings["target_words"],
            "max_words": settings["max_words"],
            "temperature": settings["temperature"],
            "max_revisions": settings["max_revisions"],
        }
        save_local_config("WRITING_CONFIG", writing_config)

        # 保存高级配置
        advanced_config = {
            "enable_memory": settings["enable_memory"],
            "memory_max_chapters": settings["memory_max_chapters"],
            "enable_character_tracking": settings["enable_character_tracking"],
            "enable_consistency_check": settings["enable_consistency_check"],
            "semi_auto_mode": settings["semi_auto_mode"],
            "show_diff_on_revision": settings["show_diff_on_revision"],
            "enable_version_control": settings["enable_version_control"],
            "max_history_versions": settings["max_history_versions"],
            "prompt_template_set": settings["prompt_template_set"],
            "enable_prompt_ab_test": settings["enable_prompt_ab_test"],
        }
        save_local_config("ADVANCED_CONFIG", advanced_config)

        # 保存自动模式配置
        auto_config = {
            "target_chapters": settings["target_chapters"],
            "max_consecutive_errors": settings["max_consecutive_errors"],
        }
        save_local_config("AUTO_MODE_CONFIG", auto_config)

        QMessageBox.information(
            self,
            "设置已保存",
            "设置已保存，部分设置需要重启程序后生效。"
        )

        self.accept()
