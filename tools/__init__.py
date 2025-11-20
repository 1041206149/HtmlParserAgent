"""
网页工具模块
"""
from .webpage_source import get_webpage_source
from .webpage_screenshot import capture_webpage_screenshot

__all__ = [
    "get_webpage_source",
    "capture_webpage_screenshot"
]

