"""
网页截图工具
使用 DrissionPage 捕获网页截图
"""
from langchain_core.tools import tool
from DrissionPage import ChromiumPage   , ChromiumOptions
import os
from datetime import datetime


@tool
def capture_webpage_screenshot(
    url: str,
    save_path: str = None,
    full_page: bool = True,
    width: int = 1920,
    height: int = 1080
) -> str:
    """
    捕获网页截图

    Args:
        url: 要截图的网页URL
        save_path: 截图保存路径，如果为None则自动生成文件名
        full_page: 是否截取整个页面，默认True。False则只截取可视区域
        width: 浏览器窗口宽度，默认1920
        height: 浏览器窗口高度，默认1080

    Returns:
        截图保存的文件路径

    Examples:
        >>> path = capture_webpage_screenshot("https://www.example.com")
        >>> print(f"截图已保存到: {path}")

        >>> path = capture_webpage_screenshot(
        ...     "https://www.example.com",
        ...     save_path="./example_screenshot.png",
        ...     full_page=False
        ... )
    """
    try:
        # 配置浏览器选项
        co = ChromiumOptions()
        co.headless(True)
        co.set_argument('--window-size', f'{width},{height}')

        # 创建页面对象
        page = ChromiumPage(addr_or_opts=co)

        # 设置窗口大小
        page.set.window.size(width, height)

        # 访问网页
        page.get(url)

        # 等待页面加载完成
        page.wait(3)

        # 生成默认保存路径
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 从URL中提取域名作为文件名的一部分
            domain = url.split("//")[-1].split("/")[0].replace(".", "_")
            save_path = f"screenshot_{domain}_{timestamp}.png"

        # 确保保存目录存在
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)

        # 截图
        if full_page:
            # 截取整个页面
            page.get_screenshot(path=save_path, full_page=True)
        else:
            # 只截取可视区域
            page.get_screenshot(path=save_path)

        # 关闭浏览器
        page.quit()

        # 获取绝对路径
        abs_path = os.path.abspath(save_path)

        return f"截图成功保存到: {abs_path}"

    except Exception as e:
        return f"网页截图失败: {str(e)}"


if __name__ == "__main__":
    # 测试工具
    test_url = "https://www.example.com"

    print(f"正在截图 {test_url}...")

    # 测试1: 全页截图（自动文件名）
    result1 = capture_webpage_screenshot.invoke({
        "url": test_url,
        "full_page": True
    })
    print(f"\n测试1 - 全页截图: {result1}")

    # 测试2: 可视区域截图（指定文件名）
    result2 = capture_webpage_screenshot.invoke({
        "url": test_url,
        "save_path": "./example_visible.png",
        "full_page": False
    })
    print(f"\n测试2 - 可视区域截图: {result2}")

    # 测试3: 自定义尺寸
    result3 = capture_webpage_screenshot.invoke({
        "url": test_url,
        "save_path": "./example_mobile.png",
        "width": 375,
        "height": 667,
        "full_page": True
    })
    print(f"\n测试3 - 移动端尺寸截图: {result3}")

