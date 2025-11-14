# HtmlParserAgent 使用文档

## 快速开始

### 1. 安装依赖

```bash
cd /Users/brown/Projects/HtmlParserAgent
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，主要配置项：

```env
# 必需配置
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-vision-preview

# 可选配置
OPENAI_TEMPERATURE=0.3
HEADLESS=true
TIMEOUT=30000
```

### 3. 运行示例

#### 方式1：命令行工具

```bash
# 单个URL
python main.py --url "https://example.com/article" --output ./outputs/example

# 多个URL迭代优化
python main.py --urls examples/example_urls.txt --output ./outputs/example --iterate

# 启用详细日志
python main.py --url "https://example.com/article" --log-level DEBUG
```

#### 方式2：Python脚本

```python
from workflows.parser_builder_workflow import ParserBuilderWorkflow

workflow = ParserBuilderWorkflow()

# 单个URL
result = workflow.run(
    url="https://example.com/article",
    output_dir="./outputs/example"
)

# 多URL迭代
result = workflow.run_iterative(
    urls=["url1", "url2", "url3"],
    output_dir="./outputs/example"
)
```

## 工作流程说明

### Stage 1: HTML预处理
- 获取HTML内容
- 清理无关标签（script, style, ads等）
- 智能分块（基于语义标签）
- 提取关键区域

**输出**：
- `original.html` - 原始HTML
- `cleaned.html` - 清理后的HTML
- `region_*.html` - 各个区域
- `chunk_*.html` - 分块HTML

### Stage 2: 视觉理解
- 使用Playwright渲染页面并截图
- 大图自动分块（重叠滑窗）
- 调用VLLM分析图片内容
- 合并多块结果生成结构化JSON

**输出**：
- `screenshot.png` - 完整截图
- `screenshot_chunk_*.png` - 分块截图
- `vision_output.json` - 提取的结构化数据

**示例输出**：
```json
{
  "title": {
    "type": "string",
    "value": "文章标题",
    "confidence": 0.95
  },
  "author": {
    "type": "string",
    "value": "作者名",
    "confidence": 0.90
  },
  "content": {
    "type": "string",
    "value": "正文内容...",
    "confidence": 0.90
  }
}
```

### Stage 3: 代码生成
- 将HTML和目标JSON输入LLM
- 生成Python解析器类
- 包含XPath/CSS选择器
- 添加异常处理和降级策略

**输出**：
- `generated_parser.py` - 解析器代码
- `parser_config.json` - 配置文件

### Stage 4: 验证与迭代（仅迭代模式）
- 在多个URL上测试解析器
- 计算字段级准确率
- 收集失败案例
- 重新生成优化代码
- 循环直到达到目标成功率或最大迭代次数

**输出**：
- `iteration_*/` - 每次迭代的结果
- `validation_report.json` - 验证报告
- `parser.py` - 最终解析器

## 配置参数说明

### API配置
- `OPENAI_API_KEY`: OpenAI API密钥（必需）
- `OPENAI_API_BASE`: API端点URL
- `OPENAI_MODEL`: 使用的模型名称
- `OPENAI_TEMPERATURE`: 生成温度（0-1）

### 浏览器配置
- `HEADLESS`: 无头模式（true/false）
- `TIMEOUT`: 页面加载超时（毫秒）

### 截图配置
- `SCREENSHOT_FULL_PAGE`: 是否全页截图
- `SCREENSHOT_MAX_WIDTH`: 最大宽度（像素）
- `SCREENSHOT_MAX_HEIGHT`: 最大高度（像素）

### HTML处理配置
- `MAX_HTML_LENGTH`: 每块最大字符数
- `CHUNK_OVERLAP`: 块重叠字符数

### 验证配置
- `MIN_SAMPLE_SIZE`: 最小样本数（迭代模式）
- `SUCCESS_THRESHOLD`: 目标成功率（0-1）
- `MAX_ITERATIONS`: 最大迭代次数

## 输出目录结构

```
outputs/
└── example/
    ├── stage1_preprocess/
    │   ├── original.html
    │   ├── cleaned.html
    │   ├── region_*.html
    │   └── chunk_*.html
    ├── stage2_vision/
    │   ├── screenshot.png
    │   ├── screenshot_chunk_*.png
    │   └── vision_output.json
    ├── stage3_codegen/           # 单次模式
    │   ├── generated_parser.py
    │   └── parser_config.json
    └── stage3_4_iterate/         # 迭代模式
        ├── iteration_0/
        │   ├── generated_parser.py
        │   ├── parser_config.json
        │   └── validation_report.json
        ├── iteration_1/
        │   └── ...
        └── parser.py             # 最终版本
```

## 使用生成的解析器

```python
# 导入生成的解析器
from outputs.example.stage3_4_iterate.parser import WebPageParser

parser = WebPageParser()

# 解析HTML
html = """<html>...</html>"""
result = parser.parse(html)

print(result)
# {
#     'title': '标题',
#     'author': '作者',
#     'content': '正文...',
#     ...
# }
```

## 常见问题

### 1. API调用失败
- 检查 `.env` 中的API配置是否正确
- 确认API密钥有效
- 检查网络连接

### 2. 截图超时
- 增加 `TIMEOUT` 值
- 检查目标网站是否可访问
- 尝试非无头模式（`HEADLESS=false`）

### 3. 解析器成功率低
- 增加样本数量（至少5个URL）
- 检查URL是否是相同布局
- 查看 `validation_report.json` 了解失败原因

### 4. HTML过长
- 调整 `MAX_HTML_LENGTH` 参数
- 框架会自动分块处理

## 进阶使用

### 自定义Agent

```python
from agents import HtmlPreprocessor
from config.settings import Settings

settings = Settings()
preprocessor = HtmlPreprocessor(settings)

result = preprocessor.process(
    url="https://example.com",
    output_dir="./custom_output"
)
```

### 批量处理

```python
from workflows.parser_builder_workflow import ParserBuilderWorkflow

workflow = ParserBuilderWorkflow()

domains = {
    'example.com': ['url1', 'url2', 'url3'],
    'another.com': ['url4', 'url5', 'url6']
}

for domain, urls in domains.items():
    result = workflow.run_iterative(
        urls=urls,
        output_dir=f"./outputs/{domain}"
    )
```

## 贡献指南

欢迎提交Issue和PR！

## License

MIT License

