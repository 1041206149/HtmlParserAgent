"""
配置管理模块
"""
import os
from typing import Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """全局配置"""

    # ============================================
    # LLM API 统一配置
    # ============================================
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_api_base: str = Field(default_factory=lambda: os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"))

    # ============================================
    # 场景化模型配置
    # ============================================
    # 默认模型
    default_model: str = Field(default_factory=lambda: os.getenv("DEFAULT_MODEL", "gpt-4-vision-preview"))
    default_temperature: float = Field(default_factory=lambda: float(os.getenv("DEFAULT_TEMPERATURE", "0")))

    # 代码生成场景
    code_gen_model: str = Field(default_factory=lambda: os.getenv("CODE_GEN_MODEL", os.getenv("DEFAULT_MODEL", "gpt-4-vision-preview")))
    code_gen_temperature: float = Field(default_factory=lambda: float(os.getenv("CODE_GEN_TEMPERATURE", "0.3")))
    code_gen_max_tokens: int = Field(default_factory=lambda: int(os.getenv("CODE_GEN_MAX_TOKENS", "8192")))

    # 视觉理解场景
    vision_model: str = Field(default_factory=lambda: os.getenv("VISION_MODEL", os.getenv("DEFAULT_MODEL", "gpt-4-vision-preview")))
    vision_temperature: float = Field(default_factory=lambda: float(os.getenv("VISION_TEMPERATURE", "0")))
    vision_max_tokens: int = Field(default_factory=lambda: int(os.getenv("VISION_MAX_TOKENS", "4096")))
    vision_parallel: bool = Field(default_factory=lambda: os.getenv("VISION_PARALLEL", "true").lower() == "true")
    vision_max_workers: int = Field(default_factory=lambda: int(os.getenv("VISION_MAX_WORKERS", "4")))

    # Agent 场景（LangChain）
    agent_model: str = Field(default_factory=lambda: os.getenv("AGENT_MODEL", os.getenv("DEFAULT_MODEL", "gpt-4-vision-preview")))
    agent_temperature: float = Field(default_factory=lambda: float(os.getenv("AGENT_TEMPERATURE", "0")))

    # ============================================
    # 兼容旧配置（保持向后兼容）
    # ============================================
    @property
    def openai_model(self) -> str:
        """兼容旧代码中的 openai_model"""
        return self.default_model

    @property
    def openai_temperature(self) -> float:
        """兼容旧代码中的 openai_temperature"""
        return self.default_temperature

    # ============================================
    # 浏览器和截图配置
    # ============================================
    # Playwright配置
    headless: bool = Field(default_factory=lambda: os.getenv("HEADLESS", "true").lower() == "true")
    timeout: int = Field(default_factory=lambda: int(os.getenv("TIMEOUT", "30000")))

    # 截图配置
    screenshot_full_page: bool = Field(default_factory=lambda: os.getenv("SCREENSHOT_FULL_PAGE", "true").lower() == "true")
    screenshot_max_width: int = Field(default_factory=lambda: int(os.getenv("SCREENSHOT_MAX_WIDTH", "1920")))
    screenshot_max_height: int = Field(default_factory=lambda: int(os.getenv("SCREENSHOT_MAX_HEIGHT", "10800")))

    # ============================================
    # HTML处理配置
    # ============================================
    max_html_length: int = Field(default_factory=lambda: int(os.getenv("MAX_HTML_LENGTH", "50000")))
    chunk_overlap: int = Field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "500")))

    # ============================================
    # 验证配置
    # ============================================
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
