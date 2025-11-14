"""
XPath优化工具
"""
from typing import List, Dict, Set
from lxml import etree, html
from loguru import logger


class XPathOptimizer:
    """XPath路径优化器"""

    def __init__(self):
        """初始化XPath优化器"""
        logger.info("XPath优化器初始化")

    def extract_xpath(self, html_content: str, target_text: str) -> List[str]:
        """提取目标文本的所有可能XPath

        Args:
            html_content: HTML内容
            target_text: 目标文本

        Returns:
            XPath列表
        """
        tree = html.fromstring(html_content)
        xpaths = []

        # 查找包含目标文本的所有元素
        elements = tree.xpath(f"//*[contains(text(), '{target_text[:50]}')]")

        for elem in elements:
            xpath = tree.getpath(elem)
            xpaths.append(xpath)

        return xpaths

    def generalize_xpaths(self, xpaths_list: List[List[str]]) -> str:
        """从多个样本的XPath中提取通用模式

        Args:
            xpaths_list: 多个HTML样本的XPath列表

        Returns:
            通用化的XPath表达式
        """
        if not xpaths_list:
            return ""

        # 找到所有样本的公共路径模式
        common_patterns = self._find_common_patterns(xpaths_list)

        if common_patterns:
            # 选择最稳定的路径
            return self._select_best_xpath(common_patterns)

        # 如果没有公共模式，返回第一个样本的XPath
        return xpaths_list[0][0] if xpaths_list[0] else ""

    def _find_common_patterns(self, xpaths_list: List[List[str]]) -> List[str]:
        """查找公共路径模式

        Args:
            xpaths_list: XPath列表的列表

        Returns:
            公共模式列表
        """
        if not xpaths_list:
            return []

        # 将XPath分解为段
        segmented = []
        for xpaths in xpaths_list:
            for xpath in xpaths:
                segments = xpath.split('/')
                segmented.append(segments)

        # 找到最长公共前缀
        common = []
        if segmented:
            min_len = min(len(s) for s in segmented)
            for i in range(min_len):
                segments_at_i = [s[i] for s in segmented]
                if len(set(segments_at_i)) == 1:
                    common.append(segments_at_i[0])
                else:
                    # 尝试泛化（去除索引）
                    generalized = self._generalize_segment(segments_at_i)
                    if generalized:
                        common.append(generalized)
                    break

        return ['/'.join(common)] if common else []

    def _generalize_segment(self, segments: List[str]) -> str:
        """泛化路径段

        Args:
            segments: 路径段列表

        Returns:
            泛化后的路径段
        """
        # 移除索引 [1], [2] 等
        import re

        patterns = []
        for seg in segments:
            # 移除数字索引
            pattern = re.sub(r'\[\d+\]', '', seg)
            patterns.append(pattern)

        # 如果去除索引后相同，则返回泛化版本
        if len(set(patterns)) == 1:
            return patterns[0]

        return ""

    def _select_best_xpath(self, xpaths: List[str]) -> str:
        """选择最佳XPath

        Args:
            xpaths: XPath候选列表

        Returns:
            最佳XPath
        """
        if not xpaths:
            return ""

        # 评分标准：
        # 1. 路径越短越好
        # 2. 包含class或id属性的更稳定
        # 3. 避免数字索引

        scored = []
        for xpath in xpaths:
            score = 0

            # 路径长度（越短越好）
            depth = xpath.count('/')
            score -= depth

            # 包含class或id
            if '@class' in xpath or '@id' in xpath:
                score += 10

            # 避免数字索引
            import re
            if not re.search(r'\[\d+\]', xpath):
                score += 5

            scored.append((score, xpath))

        # 返回得分最高的
        scored.sort(reverse=True)
        return scored[0][1]

    def convert_to_css_selector(self, xpath: str) -> str:
        """将XPath转换为CSS选择器

        Args:
            xpath: XPath表达式

        Returns:
            CSS选择器
        """
        # 简单转换逻辑（可以扩展）
        css = xpath

        # 替换基本路径
        css = css.replace('//', ' ')
        css = css.replace('/', ' > ')

        # 处理属性
        import re
        css = re.sub(r'\[@class="([^"]+)"\]', r'.\1', css)
        css = re.sub(r'\[@id="([^"]+)"\]', r'#\1', css)

        return css.strip()

