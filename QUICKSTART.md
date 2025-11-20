# HtmlParserAgent 快速开始指南

> 5分钟快速上手 HtmlParserAgent

---

## 🚀 快速开始

### 步骤1: 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/HtmlParserAgent.git
cd HtmlParserAgent

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 步骤2: 配置API密钥

编辑 `.env` 文件：

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=http://your_base_url/v1
```

### 步骤3: 运行示例

```bash
# 运行内置示例
python example.py
```

### 步骤4: 使用生成的解析器

```bash
# 使用生成的解析器解析新URL
python output/blog/parsers/generated_parser.py "https://stackoverflow.blog/some-article/"
```

---

## 📝 基本用法

### 命令行使用

```bash
# 查看帮助
python main.py -h

# 单个URL（测试用）
python main.py https://example.com/article

# 多个URL
python main.py https://example.com/article1 https://example.com/article2

# 从文件读取URL列表（推荐）
python main.py -f urls.txt

# 指定输出目录和页面类型
python main.py -f urls.txt -o output/blog -t blog_article
```

### Python API使用

```python
from agent import ParserAgent

# 方式1: 直接指定URL列表
agent = ParserAgent(output_dir="output/blog")
urls = [
    "https://example.com/article1",
    "https://example.com/article2",
    "https://example.com/article3",
]
result = agent.generate_parser(urls=urls, validate=True)

# 方式2: 从文件读取URL
with open('urls.txt', 'r') as f:
    urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
result = agent.generate_parser(urls=urls, validate=True)

# 查看结果
if result['success']:
    print(f"✓ 解析器: {result['parser_path']}")
    print(f"✓ 成功率: {result['validation_result']['success_rate']:.1%}")
```

---

## 🎯 常见场景

### 场景1: 解析博客文章

```python
from agent import ParserAgent

agent = ParserAgent(output_dir="output/blog")

urls = [
    "https://blog.example.com/article1",
    "https://blog.example.com/article2",
]

result = agent.generate_parser(
    urls=urls,
    layout_type="blog_article",
    validate=True
)
```

### 场景2: 解析电商产品页

```python
from agent import ParserAgent

agent = ParserAgent(output_dir="output/ecommerce")

urls = [
    "https://shop.example.com/product/123",
    "https://shop.example.com/product/456",
]

result = agent.generate_parser(
    urls=urls,
    layout_type="product_page",
    validate=True
)
```

### 场景3: 解析新闻列表

```python
from agent import ParserAgent

agent = ParserAgent(output_dir="output/news")

urls = [
    "https://news.example.com/category/tech",
    "https://news.example.com/category/business",
]

result = agent.generate_parser(
    urls=urls,
    layout_type="news_list",
    validate=True
)
```

---

## 💡 最佳实践

### 1. URL选择

- ✅ 选择同一网站、同一类型的页面
- ✅ 提供2-5个样本URL（更多样本 = 更准确）
- ✅ 选择结构相似但内容不同的页面
- ⚠️ 避免混合完全不同类型的页面

### 2. 配置优化

```bash
# .env 文件推荐配置
MAX_ITERATIONS=5          # 允许5次迭代优化
SUCCESS_THRESHOLD=0.8     # 80%成功率即可
MIN_SAMPLE_SIZE=2         # 至少2个样本
```

### 3. 验证建议

- ✅ 首次使用建议启用验证 (`validate=True`)
- ✅ 检查生成的代码质量
- ✅ 在更多URL上测试生成的解析器

---

## 🔍 查看结果

### 输出目录结构

```
output/
└── blog/
    ├── screenshots/              # 页面截图
    │   ├── sample_1.png
    │   ├── sample_2.png
    │   └── sample_3.png
    ├── parsers/                  # 生成的解析器
    │   └── generated_parser.py
    └── configs/                  # 配置文件
        └── schema.json
```

### 使用生成的解析器

```python
# 导入生成的解析器
import sys
sys.path.insert(0, 'output/blog/parsers')
from generated_parser import WebPageParser

# 创建解析器实例
parser = WebPageParser()

# 解析HTML
html = """<html>...</html>"""
data = parser.parse(html)
print(data)
```

---

## 🐛 常见问题

### Q1: API调用失败

**问题**: `Error: Invalid API key`

**解决**:
1. 检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确
2. 检查 `OPENAI_API_BASE` 是否包含 `/v1` 后缀

### Q2: 浏览器启动失败

**问题**: `Error: Chrome not found`

**解决**:
1. 确保已安装 Chrome 或 Chromium 浏览器
2. 检查浏览器路径是否正确

### Q3: 验证失败

**问题**: 成功率低于阈值

**解决**:
1. 检查URL是否可访问
2. 增加样本数量（提供更多URL）
3. 降低成功率阈值（修改 `.env` 中的 `SUCCESS_THRESHOLD`）

---

## 📚 更多资源

- **[完整文档](README.md)** - 详细的使用说明
- **[工作流程框架](WORKFLOW_FRAMEWORK.md)** - 系统架构详解
- **[多URL迭代指南](MULTI_URL_ITERATION_GUIDE.md)** - 高级功能说明
- **[实现总结](IMPLEMENTATION_SUMMARY.md)** - 技术实现细节

---

## 🎉 下一步

1. ✅ 运行 `python example.py` 查看完整演示
2. ✅ 尝试解析你自己的网页
3. ✅ 查看生成的代码并根据需要调整
4. ✅ 阅读完整文档了解更多功能

**祝你使用愉快！** 🚀


