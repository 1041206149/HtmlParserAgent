"""
截图工具模块
"""
import base64
import os
import time
from pathlib import Path
from typing import Optional, List

from DrissionPage import ChromiumPage, ChromiumOptions
from PIL import Image
from loguru import logger


class ScreenshotTool:
    """网页截图工具"""

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        max_width: int = 1920,
        max_height: int = 10800
    ):
        """初始化截图工具

        Args:
            headless: 是否无头模式
            timeout: 超时时间(毫秒)
            max_width: 最大宽度
            max_height: 最大高度
        """
        self.headless = headless
        self.timeout = timeout
        self.max_width = max_width
        self.max_height = max_height

        logger.info(f"截图工具初始化 - 无头模式: {headless}, 超时: {timeout}ms")


    def capture_url(
        self,
        url: str,
        output_path: Optional[str] = None,
        full_page: bool = True
    ) -> str:
        """截取URL页面或本地HTML文件

        Args:
            url: 目标URL或本地HTML文件路径
            output_path: 输出路径（可选）
            full_page: 是否全页截图

        Returns:
            截图文件路径
        """
        # 配置浏览器选项
        co = ChromiumOptions()

        # macOS 常见 Chrome 路径
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            co.set_browser_path(chrome_path)

        # 设置无头模式
        if self.headless:
            co.headless()

        # 创建浏览器页面对象
        page = ChromiumPage(addr_or_opts=co)

        try:
            # 判断是否为本地文件
            if os.path.isfile(url):
                # 获取 HTML 文件的绝对路径
                abs_path = os.path.abspath(url)
                # 转换为 file:// 协议的 URL
                target_url = f"file://{abs_path}"
                logger.info(f"访问本地HTML文件: {abs_path}")
            else:
                target_url = url
                logger.info(f"访问URL: {url}")

            # 访问目标页面
            page.get(target_url)

            # 等待页面完全加载
            page.wait.load_start()
            time.sleep(2)  # 额外等待确保渲染完成

            # 获取页面实际尺寸
            width = page.run_js("return document.documentElement.scrollWidth")
            height = page.run_js("return document.documentElement.scrollHeight")

            logger.debug(f"页面实际尺寸: {width}x{height}")

            # 设置合理的窗口宽度，高度设为固定值
            page.set.window.size(width if width else self.max_width, 1080)

            # 再次等待渲染
            time.sleep(1)

            # 生成输出路径
            if not output_path:
                output_path = f"screenshot_{hash(url)}.png"

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # 使用 full_page=True 截取完整页面
            page.get_screenshot(path=str(output_file), full_page=full_page)

            logger.info(f"截图保存至: {output_file}")
            return str(output_file)

        finally:
            # 关闭浏览器
            page.quit()


    def split_screenshot(
        self,
        image_path: str,
        chunk_height: int = 2000,
        overlap: int = 200
    ) -> List[str]:
        """分割大截图

        Args:
            image_path: 原始截图路径
            chunk_height: 每块高度
            overlap: 重叠像素

        Returns:
            分割后的图片路径列表
        """
        img = Image.open(image_path)
        width, height = img.size

        if height <= chunk_height:
            return [image_path]

        chunks = []
        base_path = Path(image_path)

        y = 0
        chunk_idx = 0
        while y < height:
            # 计算裁剪区域
            y_end = min(y + chunk_height, height)
            box = (0, y, width, y_end)

            # 裁剪并保存
            chunk_img = img.crop(box)
            chunk_path = base_path.parent / f"{base_path.stem}_chunk_{chunk_idx}{base_path.suffix}"
            chunk_img.save(chunk_path)
            chunks.append(str(chunk_path))

            logger.debug(f"分割截图块 {chunk_idx}: y={y}-{y_end}")

            # 移动到下一块（考虑重叠）
            y = y_end - overlap if y_end < height else height
            chunk_idx += 1

        logger.info(f"截图分割完成，共 {len(chunks)} 块")
        return chunks

    def image_to_base64(self, image_path: str) -> str:
        """将图片转换为Base64编码

        Args:
            image_path: 图片路径

        Returns:
            Base64编码字符串
        """
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

