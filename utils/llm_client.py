"""
LLM客户端封装
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI

# 加载项目根目录的 .env 文件
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

# 验证
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(f".env 文件路径: {env_path}, API Key未加载")

class LLMClient:
    """LLM客户端封装类"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3
    ):
        """初始化LLM客户端

        Args:
            api_key: API密钥
            api_base: API基础URL
            model: 模型名称
            temperature: 温度参数
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_base = api_base or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4-vision-preview")
        self.temperature = temperature

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )

        logger.info(f"LLM客户端初始化完成 - 模型: {self.model}, Base: {self.api_base}")

    @classmethod
    def from_settings(cls, settings, model: Optional[str] = None):
        """从Settings对象创建LLMClient

        Args:
            settings: Settings配置对象
            model: 可选的模型名称覆盖（如vision_model）

        Returns:
            LLMClient实例
        """
        return cls(
            api_key=settings.openai_api_key,
            api_base=settings.openai_api_base,
            model=model or settings.openai_model,
            temperature=settings.openai_temperature
        )

    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """调用聊天完成API

        Args:
            messages: 消息列表
            temperature: 温度参数（可选）
            max_tokens: 最大token数（可选）
            **kwargs: 其他参数

        Returns:
            模型响应文本
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise

    def vision_completion(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        image_data: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """调用视觉理解API

        Args:
            prompt: 提示文本
            image_url: 图片URL
            image_data: Base64编码的图片数据
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            模型响应文本
        """
        content = [{"type": "text", "text": prompt}]

        if image_url:
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
        elif image_data:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_data}"}
            })

        messages = [{"role": "user", "content": content}]

        return self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

