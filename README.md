# HtmlParserAgent

智能HTML解析器生成框架 - 通过多阶段Pipeline自动生成针对特定网站布局的通用解析代码

## 功能特性

- 🔍 **智能HTML预处理**: 自动分析DOM结构，智能分块和去噪
- 👁️ **视觉理解**: 基于VLLM的页面截图分析，提取结构化内容
- 🤖 **代码生成**: 自动生成可复用的解析代码
- 🔄 **迭代优化**: 多样本验证，自动泛化XPath选择器
- 📊 **质量评估**: 完整的测试和评估体系

## 架构设计

```
Stage 1: 内容采集与预处理 (HtmlPreprocessor)
Stage 2: 视觉理解与结构提取 (VisualUnderstandingAgent)  
Stage 3: 代码生成与验证 (CodeGeneratorAgent)
Stage 4: 迭代优化与泛化 (ValidationOrchestrator)
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 配置环境变量

复制 `.env.example` 并配置你的API密钥：

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的API配置
```

### 运行示例

```bash
# 单个URL解析
python main.py --url "https://example.com/article" --output ./outputs/example

# 多URL迭代优化
python main.py --urls urls.txt --output ./outputs/example --iterate
```

## 项目结构

```
HtmlParserAgent/
├── agents/              # 核心Agent模块
│   ├── preprocessor.py  # HTML预处理器
│   ├── visual_understanding.py  # 视觉理解Agent
│   ├── code_generator.py        # 代码生成Agent
│   └── validator.py             # 验证与迭代编排器
├── utils/               # 工具函数
│   ├── html_chunker.py  # HTML分块
│   ├── screenshot.py    # 截图工具
│   ├── xpath_optimizer.py  # XPath优化
│   └── llm_client.py    # LLM客户端封装
├── workflows/           # 工作流编排
│   └── parser_builder_workflow.py
├── templates/           # 代码模板
│   └── parser_template.py.jinja2
├── config/              # 配置文件
│   └── default_config.yaml
├── outputs/             # 输出目录
├── tests/               # 测试用例
├── main.py              # 主入口
└── requirements.txt
```

## 使用示例

```python
from workflows.parser_builder_workflow import ParserBuilderWorkflow

# 初始化工作流
workflow = ParserBuilderWorkflow()

# 单URL处理
result = workflow.run(
    url="https://example.com/article",
    output_dir="./outputs/example"
)

# 多URL迭代优化
result = workflow.run_iterative(
    urls=[
        "https://example.com/article1",
        "https://example.com/article2",
        "https://example.com/article3"
    ],
    output_dir="./outputs/example"
)

# 使用生成的解析器
from outputs.example.parser import ArticleParser
parser = ArticleParser()
data = parser.parse("https://example.com/new-article")
```

## 配置说明

详见 `.env` 文件的配置项说明

## 开发路线图

- [x] 基础框架搭建
- [ ] HTML预处理优化
- [ ] 视觉理解多模型支持
- [ ] XPath泛化算法优化
- [ ] Web UI界面
- [ ] 分布式处理支持

## License

MIT License
