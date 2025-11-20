# 快速开始指南

## 🚀 5分钟上手

### 第一步：安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt
```

### 第二步：验证安装

```bash
# 运行设置测试
python test_setup.py
```

如果看到 "🎉 所有测试通过!"，说明安装成功。

### 第三步：运行示例

```bash
# 运行示例程序
python example.py
```

这将：
1. 获取示例URL的HTML源码
2. 捕获页面截图
3. 使用视觉模型提取页面结构
4. 生成BeautifulSoup解析代码
5. 验证生成的代码

### 第四步：查看结果

生成的文件位于 `output/` 目录：

```
output/
├── blog/
│   ├── parsers/
│   │   ├── generated_parser.py  # 生成的解析器代码
│   │   └── schema.json          # 字段配置
│   └── screenshots/
│       └── sample_1.png         # 页面截图
```

### 第五步：使用生成的解析器

```bash
# 方式1: 解析URL
python output/blog/parsers/generated_parser.py "https://example.com/article"

# 方式2: 解析本地HTML文件
python output/blog/parsers/generated_parser.py "path/to/file.html"
```

## 💡 常见使用场景

### 场景1: 解析博客文章

```python
from agent import ParserAgent

agent = ParserAgent(output_dir="output/blog")

result = agent.generate_parser(
    urls=["https://blog.example.com/article-1"],
    layout_type="blog_article",
    validate=True
)

print(f"解析器: {result['parser_path']}")
```

### 场景2: 解析电商产品页

```python
from agent import ParserAgent

agent = ParserAgent(output_dir="output/ecommerce")

result = agent.generate_parser(
    urls=[
        "https://shop.example.com/product/123",
        "https://shop.example.com/product/456",
    ],
    layout_type="product_page",
    validate=True
)
```

### 场景3: 批量处理多个URL

```python
from agent import ParserAgent

# 读取URL列表
with open("urls.txt") as f:
    urls = [line.strip() for line in f if line.strip()]

agent = ParserAgent()
result = agent.generate_parser(urls=urls, validate=True)
```

### 场景4: 分步使用工具

```python
from tools import (
    get_webpage_source,
    capture_webpage_screenshot,
    extract_json_from_image,
    generate_parser_code
)

url = "https://example.com"

# 1. 获取HTML
html = get_webpage_source(url)

# 2. 截图
screenshot = capture_webpage_screenshot(url)

# 3. 提取结构
schema = extract_json_from_image(screenshot)

# 4. 生成代码
result = generate_parser_code(html, schema)
```

## 🔧 配置调整

编辑 `.env` 文件来调整配置：

```bash
# 调整最大迭代次数
MAX_ITERATIONS=10

# 调整验证成功阈值
SUCCESS_THRESHOLD=0.9

# 调整最小样本数量
MIN_SAMPLE_SIZE=3
```

## 📊 查看日志

日志文件位于 `logs/` 目录：

```bash
# 查看今天的日志
tail -f logs/agent_$(date +%Y-%m-%d).log
```

## ❓ 常见问题

### Q1: 生成的代码不能正确解析？

**A**: 尝试以下方法：
1. 增加样本URL数量（提供2-3个同类型URL）
2. 手动调整生成的代码
3. 查看验证报告中的错误信息

### Q2: 如何提高解析准确率？

**A**: 
1. 提供更多样本URL
2. 确保URL属于同一布局类型
3. 调整 `SUCCESS_THRESHOLD` 配置

### Q3: 如何处理需要登录的页面？

**A**: 
1. 先手动获取HTML并保存
2. 使用 `generate_parser_code` 直接从HTML生成代码

### Q4: 生成的代码如何集成到项目中？

**A**:
1. 复制 `generated_parser.py` 到你的项目
2. 导入 `WebPageParser` 类
3. 调用 `parse(html)` 方法

## 🎯 下一步

1. 查看 [README.md](README.md) 了解详细功能
2. 查看 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) 了解架构设计
3. 修改 `example.py` 尝试不同的使用方式
4. 根据需求扩展Agent功能

## 💬 获取帮助

- 查看日志文件排查问题
- 运行 `python test_setup.py` 检查环境
- 查看生成代码中的注释

