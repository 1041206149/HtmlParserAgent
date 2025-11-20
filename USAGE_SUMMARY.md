# HtmlParserAgent 使用总结

## 🎯 快速开始

### 1. 命令行使用（推荐）

```bash
# 步骤1: 创建URL文件
cat > urls.txt << EOF
# 博客文章URL列表
https://example.com/article1
https://example.com/article2
https://example.com/article3
EOF

# 步骤2: 生成解析器
python main.py -f urls.txt -o output/blog -t blog_article

# 步骤3: 使用生成的解析器
python output/blog/parsers/generated_parser.py https://example.com/new-article
```

### 2. Python API使用

```python
from agent import ParserAgent

# 从文件读取URL
with open('urls.txt', 'r') as f:
    urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# 生成解析器
agent = ParserAgent(output_dir="output/blog")
result = agent.generate_parser(urls=urls, validate=True)

# 使用解析器
if result['success']:
    import sys
    sys.path.insert(0, 'output/blog/parsers')
    from generated_parser import WebPageParser
    
    parser = WebPageParser()
    data = parser.parse(html)
    print(data)
```

---

## 📋 命令行参数说明

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--file` | `-f` | URL文件路径 | `-f urls.txt` |
| `--output` | `-o` | 输出目录 | `-o output/blog` |
| `--type` | `-t` | 页面类型 | `-t blog_article` |
| `--domain` | `-d` | 域名 | `-d example.com` |
| `--no-validate` | - | 跳过验证 | `--no-validate` |
| `--help` | `-h` | 显示帮助 | `-h` |

---

## 📁 URL文件格式

```text
# URL列表示例
# 每行一个URL，以 # 开头的行为注释

# 博客文章
https://example.com/article1
https://example.com/article2

# 产品页面
https://shop.example.com/product/123
https://shop.example.com/product/456
```

**规则**：
- ✅ 每行一个URL
- ✅ 以 `#` 开头的行为注释
- ✅ 空行会被自动跳过
- ✅ 支持UTF-8编码

---

## 🎨 使用场景

### 场景1: 博客文章解析

```bash
# 创建URL文件
cat > blog_urls.txt << EOF
https://blog.example.com/article1
https://blog.example.com/article2
https://blog.example.com/article3
EOF

# 生成解析器
python main.py -f blog_urls.txt -o output/blog -t blog_article
```

### 场景2: 电商产品页解析

```bash
# 创建URL文件
cat > product_urls.txt << EOF
https://shop.example.com/product/123
https://shop.example.com/product/456
https://shop.example.com/product/789
EOF

# 生成解析器
python main.py -f product_urls.txt -o output/ecommerce -t product_page
```

### 场景3: 新闻列表解析

```bash
# 创建URL文件
cat > news_urls.txt << EOF
https://news.example.com/category/tech
https://news.example.com/category/business
EOF

# 生成解析器
python main.py -f news_urls.txt -o output/news -t news_list
```

---

## 💡 最佳实践

### 1. URL选择

- ✅ 选择同一网站、同一类型的页面
- ✅ 提供2-5个样本URL（更多样本 = 更准确）
- ✅ 选择结构相似但内容不同的页面
- ⚠️ 避免混合完全不同类型的页面

### 2. 文件组织

```
project/
├── urls/
│   ├── blog_urls.txt
│   ├── product_urls.txt
│   └── news_urls.txt
├── output/
│   ├── blog/
│   ├── ecommerce/
│   └── news/
└── scripts/
    ├── generate_blog_parser.sh
    └── generate_product_parser.sh
```

### 3. 自动化脚本

创建 `generate_blog_parser.sh`：

```bash
#!/bin/bash
python main.py \
  -f urls/blog_urls.txt \
  -o output/blog \
  -t blog_article \
  && echo "✓ 博客解析器生成成功"
```

---

## 🔍 输出结构

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

---

## ⚙️ 配置建议

### .env 文件

```bash
# API配置
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=http://your_base_url/v1

# 模型配置
AGENT_MODEL=claude-sonnet-4-5-20250929
CODE_GEN_MODEL=claude-sonnet-4-5-20250929
VISION_MODEL=qwen-vl-max

# Agent配置
MAX_ITERATIONS=5          # 允许5次迭代优化
SUCCESS_THRESHOLD=0.8     # 80%成功率即可
MIN_SAMPLE_SIZE=2         # 至少2个样本
```

---

## 🐛 常见问题

### Q: 如何添加更多URL？

**A**: 直接编辑URL文件，每行添加一个新URL即可。

```bash
echo "https://example.com/new-article" >> urls.txt
python main.py -f urls.txt
```

### Q: 如何为不同项目生成不同的解析器？

**A**: 使用不同的输出目录和URL文件。

```bash
python main.py -f blog_urls.txt -o output/blog
python main.py -f product_urls.txt -o output/ecommerce
```

### Q: 如何跳过验证快速生成？

**A**: 使用 `--no-validate` 参数。

```bash
python main.py -f urls.txt --no-validate
```

---

## 📚 相关文档

- **[README.md](README.md)** - 完整文档
- **[QUICKSTART.md](QUICKSTART.md)** - 快速开始指南
- **[CHANGELOG.md](CHANGELOG.md)** - 更新日志
- **[WORKFLOW_FRAMEWORK.md](WORKFLOW_FRAMEWORK.md)** - 工作流程框架

---

**提示**: 建议使用URL文件管理多个URL，这样更易于维护和版本控制。


