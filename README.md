# HtmlParserAgent

智能网页解析代码生成器 - 通过AI自动生成网页解析代码

## 🌟 项目简介

HtmlParserAgent 是一个基于大语言模型的智能Agent系统，能够自动分析网页结构并生成Python解析代码。只需提供几个示例URL，Agent就能：

1. 📸 自动获取网页源码和截图
2. 🔍 使用视觉模型分析页面结构
3. 💻 生成可直接使用的BeautifulSoup解析代码
4. ✅ 自动验证生成代码的正确性
5. 🔄 迭代优化直到满足要求

## 🎯 核心特性

- **智能规划**: Agent自动分析任务并制定执行计划
- **自动化流程**: 从URL到可用代码，全程自动化
- **视觉理解**: 使用qwen-vl-max模型理解页面布局
- **代码生成**: 使用Claude生成高质量解析代码
- **自动验证**: 验证生成代码的正确性并给出改进建议
- **可扩展**: 模块化设计，易于扩展和定制

## 📦 安装

### 环境要求

- Python 3.8+
- Chrome/Chromium 浏览器

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

复制 `.env` 文件并配置API密钥：

```bash
# API配置已在.env中预设，如需修改请编辑.env文件
```

## 🚀 快速开始

### 方式1: 使用Agent（推荐）

```python
from agent import ParserAgent

# 创建Agent
agent = ParserAgent(output_dir="output")

# 提供URL列表
urls = [
    "https://stackoverflow.blog/2025/10/15/secure-coding-in-javascript/",
]

# 生成解析器
result = agent.generate_parser(
    urls=urls,
    domain="stackoverflow.blog",
    layout_type="blog_article",
    validate=True  # 自动验证
)

# 使用生成的解析器
if result['success']:
    print(f"解析器路径: {result['parser_path']}")
```

### 方式2: 命令行使用

```bash
# 单个URL
python main.py "https://example.com/article"

# 多个URL
python main.py "https://example.com/article1" "https://example.com/article2"
```

### 方式3: 分步使用工具

```python
from tools import (
    get_webpage_source,
    capture_webpage_screenshot,
    extract_json_from_image,
    generate_parser_code
)

# 1. 获取HTML
html = get_webpage_source("https://example.com")

# 2. 截图
screenshot = capture_webpage_screenshot("https://example.com")

# 3. 提取结构
schema = extract_json_from_image(screenshot)

# 4. 生成代码
result = generate_parser_code(html, schema)
```

## 📁 项目结构

```
HtmlParserAgent/
├── agent/                  # Agent核心模块
│   ├── planner.py         # 任务规划器
│   ├── executor.py        # 任务执行器
│   ├── validator.py       # 代码验证器
│   └── orchestrator.py    # Agent编排器
├── tools/                  # 工具模块
│   ├── webpage_source.py      # 网页源码获取
│   ├── webpage_screenshot.py  # 网页截图
│   ├── visual_understanding.py # 视觉理解
│   └── code_generator.py      # 代码生成
├── utils/                  # 工具类
│   └── llm_client.py      # LLM客户端封装
├── config/                 # 配置模块
│   └── settings.py        # 配置管理
├── main.py                # 主程序入口
├── example.py             # 使用示例
└── .env                   # 环境配置
```

## 🔧 配置说明

`.env` 文件中的主要配置项：

```bash
# API配置
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=http://your_base_url/v1

# 模型配置
AGENT_MODEL=claude-sonnet-4-5-20250929      # Agent使用的模型
CODE_GEN_MODEL=claude-sonnet-4-5-20250929   # 代码生成模型
VISION_MODEL=qwen-vl-max                     # 视觉理解模型

# Agent配置
MAX_ITERATIONS=5          # 最大迭代次数
SUCCESS_THRESHOLD=0.8     # 验证成功阈值
MIN_SAMPLE_SIZE=2         # 最小样本数量
```

## 📖 使用示例

查看 `example.py` 获取更多使用示例：

```bash
python example.py
```

## 🏗️ 架构设计

### Agent工作流程

```
1. 规划阶段 (Planner)
   ├── 分析URL列表
   ├── 确定域名和布局类型
   └── 生成执行计划

2. 执行阶段 (Executor)
   ├── 获取网页源码
   ├── 捕获页面截图
   ├── 提取JSON Schema
   └── 生成解析代码

3. 验证阶段 (Validator)
   ├── 测试生成的代码
   ├── 计算成功率
   └── 诊断问题

4. 优化阶段 (可选)
   ├── 分析失败原因
   ├── 生成改进建议
   └── 迭代优化代码
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

