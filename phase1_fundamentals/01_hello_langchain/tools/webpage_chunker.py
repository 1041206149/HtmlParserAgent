"""
网页分块工具
将网页内容按段落或固定长度分块
"""
from langchain_core.tools import tool
from DrissionPage import ChromiumPage, ChromiumOptions
from typing import List
import re


@tool
def chunk_webpage(url: str, chunk_size: int = 500, method: str = "paragraph") -> List[str]:
    """
    获取网页内容并分块

    Args:
        url: 要处理的网页URL
        chunk_size: 每个块的最大字符数，默认500
        method: 分块方法，可选 "paragraph"(按段落) 或 "fixed"(固定长度)，默认 "paragraph"

    Returns:
        分块后的文本列表

    Examples:
        >>> chunks = chunk_webpage("https://www.example.com", chunk_size=300)
        >>> print(f"共分为 {len(chunks)} 个块")
        >>> print(chunks[0])  # 打印第一个块
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
        page.wait(3)

        # 获取页面纯文本内容
        # 使用 page.ele('body') 获取 body 元素，然后获取其文本内容
        body_element = page.ele('body')
        if body_element:
            text_content = body_element.text
        else:
            # 如果无法获取 body 元素，尝试获取整个页面的文本
            text_content = page.html
            # 使用简单的 HTML 标签清理来获取纯文本
            text_content = re.sub(r'<[^>]+>', ' ', text_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()

        # 关闭浏览器
        page.quit()

        # 清理文本：移除多余空白
        text_content = re.sub(r'\s+', ' ', text_content).strip()

        chunks = []

        if method == "paragraph":
            # 按段落分块（按句号、问号、感叹号分割）
            sentences = re.split(r'[。！？\.\!\?]\s*', text_content)
            current_chunk = ""

            for sentence in sentences:
                if not sentence.strip():
                    continue

                if len(current_chunk) + len(sentence) + 1 <= chunk_size:
                    current_chunk += sentence + "。"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + "。"

            if current_chunk:
                chunks.append(current_chunk.strip())

        elif method == "fixed":
            # 按固定长度分块
            for i in range(0, len(text_content), chunk_size):
                chunk = text_content[i:i + chunk_size]
                chunks.append(chunk)

        else:
            return [f"不支持的分块方法: {method}，请使用 'paragraph' 或 'fixed'"]

        return chunks if chunks else ["网页内容为空"]

    except Exception as e:
        return [f"网页分块失败: {str(e)}"]


if __name__ == "__main__":
    # 测试工具
    test_url = "https://www.example.com"
    print(f"正在获取并分块 {test_url}...")

    # 测试段落分块
    chunks_para = chunk_webpage.invoke({
        "url": test_url,
        "chunk_size": 300,
        "method": "paragraph"
    })
    print(f"\n段落分块结果: 共 {len(chunks_para)} 个块")
    for i, chunk in enumerate(chunks_para[:3], 1):
        print(f"\n块 {i} ({len(chunk)} 字符):\n{chunk}")

    # 测试固定长度分块
    chunks_fixed = chunk_webpage.invoke({
        "url": test_url,
        "chunk_size": 200,
        "method": "fixed"
    })
    print(f"\n\n固定长度分块结果: 共 {len(chunks_fixed)} 个块")
    for i, chunk in enumerate(chunks_fixed[:3], 1):
        print(f"\n块 {i} ({len(chunk)} 字符):\n{chunk}")
