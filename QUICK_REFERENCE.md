# HtmlParserAgent 快速参考

## 一键启动

```bash
cd /Users/brown/Projects/HtmlParserAgent
./setup.sh
```

## 命令速查

### 基础命令

```bash
# 单个URL
python main.py --url "https://example.com/article" --output ./outputs/example

# 多个URL（迭代优化）
python main.py --urls examples/example_urls.txt --output ./outputs/example --iterate

# 调试模式
python main.py --url "URL" --output ./outputs/test --log-level DEBUG
```

### Python API

```python
# 简单使用
from workflows.parser_builder_workflow import ParserBuilderWorkflow

workflow = ParserBuilderWorkflow()
result = workflow.run(url="https://example.com", output_dir="./outputs/test")

# 迭代优化
result = workflow.run_iterative(
    urls=["url1", "url2", "url3"],
    output_dir="./outputs/test"
)
```

## 项目结构速查

```
HtmlParserAgent/
├── agents/           # 4个核心Agent
│   ├── preprocessor.py          # Stage 1: HTML预处理
│   ├── visual_understanding.py  # Stage 2: 视觉理解
│   ├── code_generator.py        # Stage 3: 代码生成
│   └── validator.py             # Stage 4: 验证迭代
├── utils/            # 工具模块
├── workflows/        # 工作流编排
├── config/           # 配置管理
├── main.py           # CLI入口
└── .env              # API配置 ⚠️
```

## 环境变量速查

```env
# 必需配置
OPENAI_API_KEY=your_key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-vision-preview

# 常用配置
HEADLESS=true                    # 无头浏览器
TIMEOUT=30000                    # 超时(毫秒)
MAX_HTML_LENGTH=50000            # HTML最大长度
SUCCESS_THRESHOLD=0.9            # 目标成功率
MAX_ITERATIONS=3                 # 最大迭代次数
```

## 输出目录速查

```
outputs/example/
├── stage1_preprocess/
│   ├── original.html      # 原始HTML
│   ├── cleaned.html       # 清理后HTML
│   └── chunk_*.html       # 分块HTML
├── stage2_vision/
│   ├── screenshot.png     # 截图
│   └── vision_output.json # 提取的结构
├── stage3_codegen/        # 单次模式
│   └── generated_parser.py
└── stage3_4_iterate/      # 迭代模式
    ├── iteration_0/
    │   ├── generated_parser.py
    │   └── validation_report.json
    └── parser.py          # 最终版本 ⭐
```

## 使用生成的解析器

```python
# 导入
from outputs.example.stage3_4_iterate.parser import WebPageParser

# 使用
parser = WebPageParser()
result = parser.parse(html_content)

# 结果
# {
#     'title': '标题',
#     'author': '作者',
#     'content': '正文...',
#     'comments': [...]
# }
```

## 工作流程速查

```
1. HTML预处理
   ↓ 清理、分块、提取区域
2. 视觉理解
   ↓ 截图、VLLM分析、生成JSON
3. 代码生成
   ↓ LLM生成解析代码
4. 验证迭代（可选）
   ↓ 多样本测试、优化、选择最佳
✓ 输出最终解析器
```

## 常见问题速查

### API调用失败
```bash
# 检查配置
cat .env | grep OPENAI

# 测试连接
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     $OPENAI_API_BASE/models
```

### 截图超时
```env
# 增加超时时间
TIMEOUT=60000
```

### 成功率低
```bash
# 增加样本数量（至少5个URL）
# 确保URL是相同布局
# 查看报告了解失败原因
cat outputs/example/stage3_4_iterate/iteration_0/validation_report.json
```

## 测试速查

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_basic.py -v

# 生成覆盖率
pytest tests/ --cov=agents --cov-report=html
```

## 开发速查

### 添加新Agent

```python
# agents/my_agent.py
from config.settings import Settings

class MyAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
    
    def process(self, input_data, output_dir):
        result = {}
        return result
```

### 修改提示词

查看并修改：
- `agents/visual_understanding.py` - 视觉理解提示词
- `agents/code_generator.py` - 代码生成提示词

### 调试单个模块

```python
from agents import HtmlPreprocessor
from config.settings import Settings

settings = Settings()
agent = HtmlPreprocessor(settings)
result = agent.process(url, output_dir)
```

## 依赖速查

```bash
# 核心依赖
playwright          # 浏览器自动化
beautifulsoup4      # HTML解析
openai              # LLM API
pydantic            # 数据验证
loguru              # 日志

# 安装
pip install -r requirements.txt
playwright install chromium
```

## 文档速查

- `README.md` - 项目介绍和快速开始
- `USAGE.md` - 详细使用文档
- `DEVELOPMENT.md` - 开发指南
- `PROJECT_SUMMARY.md` - 项目总结
- `examples/` - 使用示例

## 有用的命令

```bash
# 查看日志
tail -f logs/app_$(date +%Y-%m-%d).log

# 清理输出
rm -rf outputs/*

# 验证结构
python verify_structure.py

# 查看帮助
python main.py --help
```

## 性能参考

- 单个URL处理：约1-2分钟
- 5个URL迭代优化：约5-10分钟
- 主要耗时：LLM调用、页面渲染

## 支持的网站类型

✅ 新闻文章、博客、论坛、电商产品页
❌ 高度动态的SPA、需要登录、实时数据

## 版本信息

- 当前版本：0.1.0
- Python要求：3.8+
- 更新日期：2025-01-14

---

💡 **提示**: 将此文件加入书签，快速查找常用命令和配置！

