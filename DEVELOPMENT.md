# 开发文档

## 架构设计

### 核心理念

HtmlParserAgent 采用多阶段 Pipeline 架构，将复杂的解析器生成任务分解为4个独立的阶段：

1. **HTML预处理** - 清理和结构化原始HTML
2. **视觉理解** - 通过VLLM识别页面结构
3. **代码生成** - 生成可执行的解析代码
4. **验证迭代** - 通过多样本测试优化代码

### 设计模式

#### 1. Agent模式
每个阶段由独立的Agent负责，Agent具有：
- 明确的职责边界
- 标准的输入输出接口
- 独立的配置和状态

#### 2. Workflow模式
工作流负责编排多个Agent的执行：
- 控制数据流
- 处理异常
- 汇总结果

#### 3. Strategy模式
解析策略支持多种方案：
- XPath选择器
- CSS选择器
- 正则表达式
- 文本特征匹配

### 目录结构详解

```
HtmlParserAgent/
├── agents/                    # Agent模块
│   ├── __init__.py
│   ├── preprocessor.py       # Stage 1: HTML预处理
│   ├── visual_understanding.py  # Stage 2: 视觉理解
│   ├── code_generator.py     # Stage 3: 代码生成
│   └── validator.py          # Stage 4: 验证与迭代
│
├── utils/                     # 工具模块
│   ├── __init__.py
│   ├── llm_client.py         # LLM客户端封装
│   ├── screenshot.py         # 截图工具
│   ├── html_chunker.py       # HTML分块
│   └── xpath_optimizer.py    # XPath优化
│
├── workflows/                 # 工作流模块
│   ├── __init__.py
│   └── parser_builder_workflow.py  # 主工作流
│
├── config/                    # 配置模块
│   ├── __init__.py
│   └── settings.py           # 配置管理
│
├── templates/                 # 模板
│   └── parser_template.py.jinja2  # 解析器模板
│
├── tests/                     # 测试
│   ├── __init__.py
│   └── test_basic.py
│
├── examples/                  # 示例
│   ├── example_single_url.py
│   ├── example_iterative.py
│   └── example_urls.txt
│
├── outputs/                   # 输出目录
├── logs/                      # 日志目录
├── main.py                    # 主入口
├── requirements.txt           # 依赖
├── .env                       # 环境变量
└── README.md                  # 说明文档
```

## 扩展指南

### 1. 添加新的Agent

```python
# agents/my_agent.py
from loguru import logger
from config.settings import Settings

class MyAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        logger.info("MyAgent初始化")
    
    def process(self, input_data, output_dir):
        # 实现处理逻辑
        result = {}
        return result
```

### 2. 自定义LLM客户端

```python
# 继承并扩展LLMClient
from utils.llm_client import LLMClient

class CustomLLMClient(LLMClient):
    def custom_method(self, prompt):
        # 自定义实现
        pass
```

### 3. 添加新的解析策略

在 `xpath_optimizer.py` 中添加新策略：

```python
def strategy_regex(self, html: str, pattern: str):
    """正则表达式策略"""
    import re
    matches = re.findall(pattern, html)
    return matches
```

### 4. 自定义验证指标

```python
# agents/validator.py
def _evaluate_result(self, parsed_data, expected):
    # 自定义评估逻辑
    custom_score = self._calculate_custom_metric(parsed_data)
    return {'score': custom_score}
```

## 性能优化建议

### 1. 并行处理
对于大量URL，可以使用多进程/多线程：

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(workflow.run, url, output) 
               for url in urls]
    results = [f.result() for f in futures]
```

### 2. 缓存机制
对于重复的HTML，可以添加缓存：

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def fetch_html_cached(url):
    return fetch_html(url)
```

### 3. 批量LLM调用
减少API调用次数：

```python
# 合并多个prompt一次调用
combined_prompt = "\n---\n".join(prompts)
response = llm_client.chat_completion(combined_prompt)
```

## 调试技巧

### 1. 启用详细日志

```python
# 代码中
from loguru import logger
logger.add("debug.log", level="DEBUG")

# 命令行
python main.py --log-level DEBUG
```

### 2. 保存中间结果

每个Stage都会保存中间文件到输出目录，便于调试。

### 3. 单独测试Agent

```python
from agents import HtmlPreprocessor
from config.settings import Settings

settings = Settings()
agent = HtmlPreprocessor(settings)
result = agent.process(url, output_dir)
```

## 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_basic.py -v

# 生成覆盖率报告
pytest tests/ --cov=agents --cov-report=html
```

### 添加测试用例

```python
# tests/test_my_feature.py
import pytest
from agents import MyAgent

class TestMyAgent:
    def test_process(self):
        agent = MyAgent(settings)
        result = agent.process(input_data, output_dir)
        assert result is not None
```

## 常见开发问题

### 1. Import错误
确保项目根目录在Python路径中：

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### 2. Playwright安装
```bash
playwright install chromium
```

### 3. 环境变量未加载
在代码入口添加：

```python
from dotenv import load_dotenv
load_dotenv()
```

## 代码规范

### 1. 命名规范
- 类名：PascalCase（如 `HtmlPreprocessor`）
- 函数名：snake_case（如 `fetch_html`）
- 常量：UPPER_CASE（如 `MAX_LENGTH`）

### 2. 文档字符串
使用Google风格：

```python
def function(arg1: str, arg2: int) -> dict:
    """简短描述
    
    Args:
        arg1: 参数1说明
        arg2: 参数2说明
        
    Returns:
        返回值说明
    """
    pass
```

### 3. 类型提示
尽可能使用类型提示：

```python
from typing import List, Dict, Optional

def process(data: List[str]) -> Optional[Dict]:
    pass
```

## 版本发布

### 语义化版本
- `x.0.0` - 主版本（不兼容的API变更）
- `0.x.0` - 次版本（新功能，向后兼容）
- `0.0.x` - 补丁版本（Bug修复）

### 更新日志
维护 `CHANGELOG.md` 记录变更。

## 贡献流程

1. Fork项目
2. 创建特性分支（`git checkout -b feature/AmazingFeature`）
3. 提交更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送分支（`git push origin feature/AmazingFeature`）
5. 提交Pull Request

## 联系方式

- 提Issue: GitHub Issues
- 邮件: your-email@example.com

