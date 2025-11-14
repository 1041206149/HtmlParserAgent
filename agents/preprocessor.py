"""
HTML预处理器 Agent
"""
from pathlib import Path
from typing import Dict

import requests
from loguru import logger

from config.settings import Settings
from utils.html_chunker import HtmlChunker


class HtmlPreprocessor:
    """HTML预处理器

    负责：
    1. 获取HTML内容
    2. 清理无关标签
    3. 智能分块
    4. 提取关键区域
    """

    def __init__(self, settings: Settings):
        """初始化预处理器

        Args:
            settings: 配置对象
        """
        self.settings = settings
        self.chunker = HtmlChunker(
            max_length=settings.max_html_length,
            overlap=settings.chunk_overlap
        )

        logger.info("HTML预处理器初始化完成")

    def fetch_html(self, url: str) -> str:
        """获取URL的HTML内容

        Args:
            url: 目标URL

        Returns:
            HTML字符串
        """
        try:
            logger.info(f"获取HTML: {url}")
            response = requests.get(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                timeout=30
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding

            html = response.text
            logger.info(f"HTML获取成功，长度: {len(html)}")
            return html

        except Exception as e:
            logger.error(f"获取HTML失败: {e}")
            raise

    def process(self, url: str, output_dir: str) -> Dict:
        """处理URL

        Args:
            url: 目标URL
            output_dir: 输出目录

        Returns:
            处理结果字典
        """
        # 1. 获取HTML
        html = self.fetch_html(url)

        # 2. 清理HTML
        cleaned_html = self.chunker.clean_html(html)

        # 3. 提取主要区域
        regions = self.chunker.extract_main_content(cleaned_html)

        # 4. 分块
        chunks = self.chunker.chunk_by_structure(cleaned_html)

        # 5. 保存结果
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 保存原始HTML
        (output_path / "original.html").write_text(html, encoding='utf-8')

        # 保存清理后的HTML
        (output_path / "cleaned.html").write_text(cleaned_html, encoding='utf-8')

        # 保存各个区域
        for region_name, region_html in regions.items():
            (output_path / f"region_{region_name}.html").write_text(
                region_html, encoding='utf-8'
            )

        # 保存分块
        for i, chunk in enumerate(chunks):
            (output_path / f"chunk_{i}.html").write_text(
                chunk['html'], encoding='utf-8'
            )

        result = {
            'url': url,
            'original_html': html,
            'cleaned_html': cleaned_html,
            'regions': regions,
            'chunks': chunks,
            'output_dir': str(output_path)
        }

        logger.info(f"HTML预处理完成 - 区域数: {len(regions)}, 分块数: {len(chunks)}")
        return result

