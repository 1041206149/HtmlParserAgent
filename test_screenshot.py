"""
测试截图功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.screenshot import ScreenshotTool
from config.settings import Settings
from loguru import logger

def test_screenshot():
    """测试截图工具"""
    try:
        logger.info("测试截图工具初始化...")
        settings = Settings()

        screenshot_tool = ScreenshotTool(
            headless=settings.headless,
            timeout=settings.timeout,
            max_width=settings.screenshot_max_width,
            max_height=settings.screenshot_max_height
        )

        logger.success("✓ 截图工具初始化成功！")

        # 测试简单的截图
        logger.info("测试截图功能...")
        test_url = "https://example.com"
        output_path = "./test_output/screenshot.png"

        result = screenshot_tool.capture_url(
            url=test_url,
            output_path=output_path,
            full_page=True
        )

        logger.success(f"✓ 截图成功！保存至: {result}")

        # 检查文件是否存在
        if Path(result).exists():
            logger.success(f"✓ 截图文件确认存在，大小: {Path(result).stat().st_size} 字节")
        else:
            logger.error("✗ 截图文件不存在")
            return False

        return True

    except Exception as e:
        logger.error(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_screenshot()
    sys.exit(0 if success else 1)

