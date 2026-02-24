"""
Agent基类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import json
import re

from api.glm_client import GLMClient


class BaseAgent(ABC):
    """Agent基类"""

    def __init__(self, client: Optional[GLMClient] = None):
        """
        初始化Agent

        Args:
            client: GLM客户端，如果不提供则使用全局单例
        """
        self.client = client

    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        pass

    def call_model(self, user_message: str, temperature: float = 0.7) -> str:
        """
        调用语言模型

        Args:
            user_message: 用户消息
            temperature: 温度参数

        Returns:
            模型回复
        """
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": user_message}
        ]

        return self.client.chat(messages, temperature)

    def extract_json_from_response(self, response: str) -> Optional[Dict]:
        """
        从响应中提取JSON内容

        Args:
            response: 模型响应文本

        Returns:
            解析后的JSON字典，如果解析失败则返回None
        """
        # 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 尝试提取markdown代码块中的JSON
        pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        matches = re.findall(pattern, response, re.DOTALL)

        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

        # 尝试提取花括号内的内容
        pattern = r'\{.*\}'
        matches = re.findall(pattern, response, re.DOTALL)

        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        return None

    def clean_response(self, response: str) -> str:
        """
        清理响应文本

        Args:
            response: 原始响应

        Returns:
            清理后的文本
        """
        # 移除可能的markdown代码块标记
        response = re.sub(r'^```\w*\n?', '', response)
        response = re.sub(r'\n?```$', '', response)

        return response.strip()
