"""
获取网页源码工具
使用 DrissionPage 获取网页的HTML源代码
"""
from langchain_core.tools import tool
from DrissionPage import ChromiumPage, ChromiumOptions
from typing import Optional


@tool
def get_webpage_source(url: str, wait_time: int = 3) -> str:
    """
    获取网页的HTML源代码

    Args:
        url: 要获取源码的网页URL
        wait_time: 页面加载等待时间（秒），默认3秒

    Returns:
        网页的HTML源代码字符串

    Examples:
        >>> source = get_webpage_source("https://www.example.com")
        >>> print(source[:100])  # 打印前100个字符
    """
    try:
        # 配置无头模式
        co = ChromiumOptions()
        co.headless(True)

        # 创建页面对象
        page = ChromiumPage(addr_or_opts=co)

        # 访问网页
        page.get(url)

        # 等待页面加载
        page.wait(wait_time)

        # 获取HTML源码
        html_source = page.html

        # 关闭浏览器
        page.quit()

        return html_source

    except Exception as e:
        return f"获取网页源码失败: {str(e)}"


if __name__ == "__main__":
    # 测试工具
    test_url = "https://www.example.com"
    print(f"正在获取 {test_url} 的源码...")
    source = get_webpage_source.invoke({"url": test_url, "wait_time": 2})
    print(f"源码长度: {len(source)} 字符")
    print(f"源码预览:\n{source[:200]}...")

