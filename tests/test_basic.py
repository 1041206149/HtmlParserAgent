"""
基础测试用例
"""
import pytest
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from agents import HtmlPreprocessor


class TestHtmlPreprocessor:
    """测试HTML预处理器"""

    def test_init(self):
        """测试初始化"""
        settings = Settings()
        preprocessor = HtmlPreprocessor(settings)
        assert preprocessor is not None

    def test_clean_html(self):
        """测试HTML清理"""
        settings = Settings()
        preprocessor = HtmlPreprocessor(settings)

        html = """
        <html>
            <head>
                <script>alert('test')</script>
                <style>.test{}</style>
            </head>
            <body>
                <article>Content</article>
                <div class="advertisement">Ad</div>
            </body>
        </html>
        """

        cleaned = preprocessor.chunker.clean_html(html)

        # 验证script和style被移除
        assert '<script>' not in cleaned
        assert '<style>' not in cleaned


class TestSettings:
    """测试配置"""

    def test_load_settings(self):
        """测试加载配置"""
        settings = Settings()
        assert settings.max_html_length > 0
        assert settings.timeout > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

