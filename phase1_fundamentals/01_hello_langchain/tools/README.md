# 网页工具使用指南

本目录包含三个基于 DrissionPage 的网页处理工具。

## 工具列表

### 1. get_webpage_source - 获取网页源码

获取指定URL的HTML源代码。

**参数：**
- `url` (str): 要获取源码的网页URL
- `wait_time` (int): 页面加载等待时间（秒），默认3秒

**返回值：**
- 网页的HTML源代码字符串

**使用示例：**
```python
from tools.webpage_source import get_webpage_source

# 获取网页源码
source = get_webpage_source.invoke({
    "url": "https://www.example.com",
    "wait_time": 2
})

print(f"源码长度: {len(source)} 字符")
print(f"源码预览: {source[:100]}...")
```

---

### 2. chunk_webpage - 网页内容分块

获取网页内容并按段落或固定长度分块，便于后续处理。

**参数：**
- `url` (str): 要处理的网页URL
- `chunk_size` (int): 每个块的最大字符数，默认500
- `method` (str): 分块方法
  - `"paragraph"`: 按段落分块（智能分句）
  - `"fixed"`: 按固定长度分块

**返回值：**
- 分块后的文本列表 (List[str])

**使用示例：**
```python
from tools.webpage_chunker import chunk_webpage

# 按段落分块
chunks = chunk_webpage.invoke({
    "url": "https://www.example.com",
    "chunk_size": 300,
    "method": "paragraph"
})

print(f"共分为 {len(chunks)} 个块")
for i, chunk in enumerate(chunks, 1):
    print(f"\n块 {i}:\n{chunk}")

# 按固定长度分块
chunks = chunk_webpage.invoke({
    "url": "https://www.example.com",
    "chunk_size": 200,
    "method": "fixed"
})
```

---

### 3. capture_webpage_screenshot - 网页截图

捕获网页的截图，支持全页截图和可视区域截图。

**参数：**
- `url` (str): 要截图的网页URL
- `save_path` (str, optional): 截图保存路径，如果为None则自动生成文件名
- `full_page` (bool): 是否截取整个页面，默认True
- `width` (int): 浏览器窗口宽度，默认1920
- `height` (int): 浏览器窗口高度，默认1080

**返回值：**
- 截图保存的文件路径字符串

**使用示例：**
```python
from tools.webpage_screenshot import capture_webpage_screenshot

# 全页截图（自动文件名）
result = capture_webpage_screenshot.invoke({
    "url": "https://www.example.com",
    "full_page": True
})
print(result)

# 可视区域截图（指定文件名）
result = capture_webpage_screenshot.invoke({
    "url": "https://www.example.com",
    "save_path": "./screenshots/example.png",
    "full_page": False
})

# 移动端尺寸截图
result = capture_webpage_screenshot.invoke({
    "url": "https://www.example.com",
    "save_path": "./screenshots/mobile.png",
    "width": 375,
    "height": 667,
    "full_page": True
})
```

---

## 与 LangChain 集成

这些工具已经用 `@tool` 装饰器标记，可以直接绑定到 LangChain 模型上：

```python
from langchain_openai import ChatOpenAI
from tools.webpage_source import get_webpage_source
from tools.webpage_chunker import chunk_webpage
from tools.webpage_screenshot import capture_webpage_screenshot

# 初始化模型
model = ChatOpenAI(
    model="claude-sonnet-4-5-20250929",
    api_key="your-api-key",
    base_url="your-base-url"
)

# 绑定工具
webpage_tools = [get_webpage_source, chunk_webpage, capture_webpage_screenshot]
model_with_tools = model.bind_tools(webpage_tools)

# AI 会根据需求自动选择工具
response = model_with_tools.invoke(
    "请帮我获取 example.com 的内容并截图"
)

# 检查 AI 的工具调用计划
if hasattr(response, 'tool_calls') and response.tool_calls:
    for tool_call in response.tool_calls:
        print(f"工具: {tool_call['name']}")
        print(f"参数: {tool_call['args']}")
```

---

## 安装依赖

使用这些工具前，需要先安装 DrissionPage：

```bash
pip install DrissionPage
```

---

## 注意事项

1. **首次运行**：DrissionPage 首次运行时会自动下载 Chromium 浏览器，可能需要一些时间
2. **无头模式**：所有工具都使用无头模式运行，不会打开可见的浏览器窗口
3. **等待时间**：如果网页加载较慢，可以适当增加 `wait_time` 参数
4. **截图大小**：全页截图可能会生成较大的文件，请注意磁盘空间
5. **错误处理**：所有工具都包含异常处理，失败时会返回错误信息字符串

---

## 高级用法

### 组合使用工具

```python
# 先获取源码分析，再截图
url = "https://www.example.com"

# 1. 获取并分块内容
chunks = chunk_webpage.invoke({
    "url": url,
    "chunk_size": 500,
    "method": "paragraph"
})

print(f"网页内容共 {len(chunks)} 个段落")

# 2. 截图保存
screenshot_path = capture_webpage_screenshot.invoke({
    "url": url,
    "save_path": f"./screenshots/{url.split('//')[-1].replace('.', '_')}.png",
    "full_page": True
})

print(f"截图已保存: {screenshot_path}")

# 3. 获取完整源码
source = get_webpage_source.invoke({
    "url": url,
    "wait_time": 3
})

print(f"源码长度: {len(source)} 字符")
```

### 批量处理网页

```python
urls = [
    "https://www.example.com",
    "https://www.python.org",
    "https://www.github.com"
]

for url in urls:
    print(f"\n处理: {url}")
    
    # 分块
    chunks = chunk_webpage.invoke({
        "url": url,
        "chunk_size": 300,
        "method": "paragraph"
    })
    
    # 截图
    screenshot = capture_webpage_screenshot.invoke({
        "url": url,
        "full_page": True
    })
    
    print(f"  - 分块数: {len(chunks)}")
    print(f"  - {screenshot}")
```

---

## 常见问题

**Q: DrissionPage 无法启动浏览器？**
A: 检查是否有足够的磁盘空间下载 Chromium，或手动指定 Chromium 路径。

**Q: 截图一片空白？**
A: 增加 `wait_time` 参数，给页面更多加载时间。

**Q: 如何截取动态加载的内容？**
A: 增加等待时间，或使用 DrissionPage 的更高级功能等待特定元素。

**Q: 分块结果不理想？**
A: 尝试调整 `chunk_size` 或切换 `method`（paragraph/fixed）。

