"""
HTML分块工具
"""
from typing import List, Dict, Tuple
from bs4 import BeautifulSoup, Tag
from loguru import logger


class HtmlChunker:
    """HTML智能分块工具"""

    def __init__(
        self,
        max_length: int = 50000,
        overlap: int = 500
    ):
        """初始化HTML分块工具

        Args:
            max_length: 每块最大字符数
            overlap: 重叠字符数
        """
        self.max_length = max_length
        self.overlap = overlap

        # HTML5语义标签优先级
        self.semantic_tags = [
            'article', 'main', 'section',
            'header', 'footer', 'nav', 'aside'
        ]

        logger.info(f"HTML分块工具初始化 - 最大长度: {max_length}, 重叠: {overlap}")

    def clean_html(self, html: str) -> str:
        """清理HTML，移除无关内容

        Args:
            html: 原始HTML

        Returns:
            清理后的HTML
        """
        soup = BeautifulSoup(html, 'lxml')

        # 移除无用标签
        for tag in soup.find_all(['script', 'style', 'noscript', 'iframe']):
            tag.decompose()

        # 移除常见广告和追踪
        ad_patterns = ['ad', 'advertisement', 'banner', 'tracking', 'analytics']
        for pattern in ad_patterns:
            for tag in soup.find_all(class_=lambda c: c and pattern in c.lower()):
                tag.decompose()
            for tag in soup.find_all(id=lambda i: i and pattern in i.lower()):
                tag.decompose()

        logger.debug("HTML清理完成")
        return str(soup)

    def extract_main_content(self, html: str) -> Dict[str, str]:
        """提取主要内容区域

        Args:
            html: HTML字符串

        Returns:
            包含不同区域的字典
        """
        soup = BeautifulSoup(html, 'lxml')
        regions = {}

        # 尝试提取语义标签
        for tag_name in self.semantic_tags:
            tag = soup.find(tag_name)
            if tag:
                regions[tag_name] = str(tag)
                logger.debug(f"提取到 <{tag_name}> 标签内容")

        # 如果没有找到语义标签，尝试其他方法
        if not regions:
            # 查找文本密度最高的区域
            body = soup.find('body')
            if body:
                regions['body'] = str(body)

        return regions

    def chunk_by_structure(self, html: str) -> List[Dict[str, any]]:
        """基于结构分块HTML

        Args:
            html: HTML字符串

        Returns:
            分块列表，每块包含HTML和元数据
        """
        soup = BeautifulSoup(html, 'lxml')
        chunks = []

        # 先提取主要区域
        regions = self.extract_main_content(html)

        for region_name, region_html in regions.items():
            if len(region_html) <= self.max_length:
                chunks.append({
                    'html': region_html,
                    'region': region_name,
                    'position': len(chunks),
                    'length': len(region_html)
                })
            else:
                # 区域过大，进一步分块
                sub_chunks = self._split_large_region(region_html, region_name)
                chunks.extend(sub_chunks)

        logger.info(f"HTML分块完成，共 {len(chunks)} 块")
        return chunks

    def _split_large_region(self, html: str, region_name: str) -> List[Dict[str, any]]:
        """分割大区域

        Args:
            html: 区域HTML
            region_name: 区域名称

        Returns:
            子块列表
        """
        soup = BeautifulSoup(html, 'lxml')
        chunks = []
        current_chunk = []
        current_length = 0

        # 遍历所有段落级元素
        for element in soup.find_all(['p', 'div', 'section', 'article']):
            element_html = str(element)
            element_length = len(element_html)

            if current_length + element_length > self.max_length and current_chunk:
                # 保存当前块
                chunk_html = ''.join(current_chunk)
                chunks.append({
                    'html': chunk_html,
                    'region': f"{region_name}_part{len(chunks)}",
                    'position': len(chunks),
                    'length': len(chunk_html)
                })

                # 开始新块（保留重叠）
                if self.overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-1][-self.overlap:]
                    current_chunk = [overlap_text]
                    current_length = len(overlap_text)
                else:
                    current_chunk = []
                    current_length = 0

            current_chunk.append(element_html)
            current_length += element_length

        # 保存最后一块
        if current_chunk:
            chunk_html = ''.join(current_chunk)
            chunks.append({
                'html': chunk_html,
                'region': f"{region_name}_part{len(chunks)}",
                'position': len(chunks),
                'length': len(chunk_html)
            })

        return chunks

    def get_xpath_context(self, html: str, target_text: str) -> str:
        """获取目标文本的XPath上下文

        Args:
            html: HTML字符串
            target_text: 目标文本

        Returns:
            XPath表达式
        """
        # TODO: 实现XPath定位
        soup = BeautifulSoup(html, 'lxml')
        # 这里需要实现更复杂的XPath生成逻辑
        return ""

