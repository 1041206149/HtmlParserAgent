"""
配置管理模块
"""
import os
from typing import Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """全局配置"""

    # API配置
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_api_base: str = Field(default_factory=lambda: os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4-vision-preview"))
    openai_temperature: float = Field(default_factory=lambda: float(os.getenv("OPENAI_TEMPERATURE", "0.3")))

    # 视觉理解专用模型配置 (Stage 2)
    vision_model: str = Field(default_factory=lambda: os.getenv("VISION_MODEL", os.getenv("OPENAI_MODEL", "gpt-4-vision-preview")))

    # Playwright配置
    headless: bool = Field(default_factory=lambda: os.getenv("HEADLESS", "true").lower() == "true")
    timeout: int = Field(default_factory=lambda: int(os.getenv("TIMEOUT", "30000")))

    # 截图配置
    screenshot_full_page: bool = Field(default_factory=lambda: os.getenv("SCREENSHOT_FULL_PAGE", "true").lower() == "true")
    screenshot_max_width: int = Field(default_factory=lambda: int(os.getenv("SCREENSHOT_MAX_WIDTH", "1920")))
    screenshot_max_height: int = Field(default_factory=lambda: int(os.getenv("SCREENSHOT_MAX_HEIGHT", "10800")))

    # HTML处理配置
    max_html_length: int = Field(default_factory=lambda: int(os.getenv("MAX_HTML_LENGTH", "50000")))
    chunk_overlap: int = Field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "500")))

    # 验证配置
    min_sample_size: int = Field(default_factory=lambda: int(os.getenv("MIN_SAMPLE_SIZE", "3")))
    success_threshold: float = Field(default_factory=lambda: float(os.getenv("SUCCESS_THRESHOLD", "0.9")))
    max_iterations: int = Field(default_factory=lambda: int(os.getenv("MAX_ITERATIONS", "3")))

    def __init__(self, config_file: Optional[str] = None, **kwargs):
        """初始化配置

        Args:
            config_file: 可选的配置文件路径
            **kwargs: 其他配置参数
        """
        super().__init__(**kwargs)

        if config_file:
            # TODO: 支持从YAML/JSON文件加载配置
            pass

    class Config:
        """Pydantic配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"

