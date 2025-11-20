# LLM API 统一配置指南

## 概述

本项目采用**基于场景的模型配置**方式，支持在不同场景下使用不同的 LLM 模型，同时保持配置的统一性和灵活性。

## 核心特性

✅ **统一的 API 配置**：所有模型共用同一个 API Key 和 Base URL（适合使用中转服务）  
✅ **场景化模型选择**：为不同使用场景配置不同的模型  
✅ **灵活切换**：只需修改 `.env` 文件即可切换模型  
✅ **向后兼容**：保持与旧代码的兼容性  

## 配置文件说明

### .env 配置结构

```bash
# 1. 统一的 API 配置（所有场景共用）
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# 2. 场景化模型配置
DEFAULT_MODEL=claude-sonnet-4-5-20250929      # 默认模型
CODE_GEN_MODEL=claude-sonnet-4-5-20250929     # 代码生成
VISION_MODEL=qwen-vl-max                       # 视觉理解
AGENT_MODEL=claude-sonnet-4-5-20250929        # Agent
```

### 支持的场景

| 场景 | 环境变量前缀 | 用途 | 推荐模型 |
|------|------------|------|---------|
| `default` | `DEFAULT_*` | 通用场景 | GPT-4 / Claude |
| `code_gen` | `CODE_GEN_*` | 代码生成 | GPT-4 / Claude |
| `vision` | `VISION_*` | 视觉理解 | GPT-4V / Qwen-VL |
| `agent` | `AGENT_*` | LangChain Agent | GPT-4 / Claude |

## 使用方式

### 方式 1：按场景创建（推荐）

```python
from utils.llm_client import LLMClient

# 代码生成场景
llm = LLMClient.for_scenario("code_gen")
response = llm.chat_completion(messages=[...])

# 视觉理解场景
llm = LLMClient.for_scenario("vision")
response = llm.vision_completion(prompt="...", image_data="...")

# Agent 场景
llm = LLMClient.for_scenario("agent")
```

### 方式 2：直接初始化

```python
from utils.llm_client import LLMClient

# 使用默认配置
llm = LLMClient()

# 指定模型
llm = LLMClient(model="gpt-4-turbo-preview")

# 完全自定义
llm = LLMClient(
    api_key="your_key",
    api_base="https://api.openai.com/v1",
    model="gpt-4",
    temperature=0.7
)
```

### 方式 3：从 Settings 创建

```python
from config.settings import Settings
from utils.llm_client import LLMClient

settings = Settings()
llm = LLMClient.from_settings(settings)
```

## 工具中的使用示例

### 代码生成工具

```python
# tools/code_generator.py
from utils.llm_client import LLMClient

@tool
def generate_code_from_html(html_content: str, target_json: Dict, ...):
    # 使用代码生成场景
    llm = LLMClient.for_scenario("code_gen")
    response = llm.chat_completion(messages=[...])
    ...
```

### 视觉理解工具

```python
# tools/visual_understanding.py
from utils.llm_client import LLMClient

@tool
def extract_json_from_image(image_path: str, model: str = None):
    # 使用视觉理解场景
    llm = LLMClient.for_scenario("vision") if not model else LLMClient(model=model)
    response = llm.vision_completion(prompt="...", image_data="...")
    ...
```

## 切换模型示例

### 使用 OpenAI 中转服务

```bash
# .env
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=http://your-proxy.com/v1

# 所有场景使用 Claude
DEFAULT_MODEL=claude-sonnet-4-5-20250929
CODE_GEN_MODEL=claude-sonnet-4-5-20250929
VISION_MODEL=qwen-vl-max
AGENT_MODEL=claude-sonnet-4-5-20250929
```

### 使用官方 OpenAI API

```bash
# .env
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=https://api.openai.com/v1

DEFAULT_MODEL=gpt-4-turbo-preview
CODE_GEN_MODEL=gpt-4-turbo-preview
VISION_MODEL=gpt-4-vision-preview
AGENT_MODEL=gpt-4-turbo-preview
```

### 混合使用不同模型

```bash
# .env
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=http://your-proxy.com/v1

DEFAULT_MODEL=gpt-4-turbo-preview
CODE_GEN_MODEL=claude-sonnet-4-5-20250929  # 代码生成用 Claude
VISION_MODEL=qwen-vl-max                    # 视觉理解用 Qwen
AGENT_MODEL=gpt-4-turbo-preview             # Agent 用 GPT-4
```

## 配置参数说明

### 通用参数

- `OPENAI_API_KEY`: API 密钥（必填）
- `OPENAI_API_BASE`: API 基础 URL（默认：https://api.openai.com/v1）

### 场景参数

每个场景支持以下参数：

- `{SCENARIO}_MODEL`: 模型名称
- `{SCENARIO}_TEMPERATURE`: 温度参数（0-2）
- `{SCENARIO}_MAX_TOKENS`: 最大 token 数（仅部分场景）

## 最佳实践

1. **使用场景化配置**：优先使用 `LLMClient.for_scenario()` 而不是直接初始化
2. **环境变量管理**：不要提交 `.env` 文件到版本控制，使用 `.env.example` 作为模板
3. **模型选择**：根据任务特点选择合适的模型
   - 代码生成：Claude Sonnet / GPT-4
   - 视觉理解：GPT-4V / Qwen-VL-Max
   - 通用对话：GPT-4 / Claude
4. **成本优化**：为不同场景配置不同的模型，在保证效果的前提下降低成本

## 迁移指南

### 从旧配置迁移

旧配置：
```python
llm = LLMClient(model=os.getenv("OPENAI_MODEL"))
```

新配置：
```python
llm = LLMClient.for_scenario("default")
```

### Settings 对象兼容性

旧代码中使用 `settings.openai_model` 的地方会自动映射到 `settings.default_model`，无需修改。

## 故障排查

### 问题：API Key 未加载

**解决方案**：
1. 确认 `.env` 文件存在于项目根目录
2. 检查 `OPENAI_API_KEY` 是否正确设置
3. 重启应用以重新加载环境变量

### 问题：模型不支持

**解决方案**：
1. 检查中转服务是否支持该模型
2. 确认模型名称拼写正确
3. 查看中转服务的模型列表文档

### 问题：温度参数无效

**解决方案**：
1. 确保温度值在 0-2 之间
2. 某些模型可能不支持温度参数
3. 检查 `.env` 文件中的配置格式

