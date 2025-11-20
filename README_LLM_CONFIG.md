# LLM API 统一配置方案

## 🎯 方案概述

本项目采用**基于场景的 LLM 模型配置**方案，完美适配你使用 OpenAI 中转 key 的需求。

### 核心特性

✅ **统一 API 配置** - 所有模型共用一个 API Key 和 Base URL  
✅ **场景化模型** - 不同工具可使用不同模型（代码生成、视觉理解等）  
✅ **灵活切换** - 只需修改 `.env` 文件中的模型名即可切换  
✅ **简单易用** - 一行代码创建对应场景的 LLM 客户端  

## 📁 文件结构

```
HtmlParserAgent/
├── .env                          # 你的配置文件（已更新）
├── .env.example                  # 配置模板（新增）
├── config/
│   └── settings.py              # Settings 类（已优化）
├── utils/
│   └── llm_client.py            # LLMClient 类（已增强）
├── tools/
│   ├── code_generator.py        # 代码生成工具（已更新）
│   └── visual_understanding.py  # 视觉理解工具（已更新）
├── examples/
│   ├── check_config.py          # 配置检查工具（新增）
│   └── test_llm_config.py       # 完整测试脚本（新增）
└── docs/
    ├── LLM_CONFIG_GUIDE.md      # 详细配置指南（新增）
    └── CONFIG_MIGRATION.md      # 迁移说明（新增）
```

## 🚀 快速开始

### 1. 查看当前配置

```bash
python examples/check_config.py
```

输出示例：
```
✅ 所有配置正常

📌 默认场景 (default)
   model: claude-sonnet-4-5-20250929
   temperature: 0

📌 代码生成 (code_gen)
   model: claude-sonnet-4-5-20250929
   temperature: 0.3

📌 视觉理解 (vision)
   model: qwen-vl-max
   temperature: 0
```

### 2. 在代码中使用

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

### 3. 切换模型

只需编辑 `.env` 文件：

```bash
# 切换代码生成模型为 GPT-4
CODE_GEN_MODEL=gpt-4-turbo-preview

# 切换视觉模型为 GPT-4V
VISION_MODEL=gpt-4-vision-preview
```

## 📋 配置说明

### .env 文件结构

```bash
# ============================================
# 统一 API 配置（所有场景共用）
# ============================================
OPENAI_API_KEY=sk-xxx                    # 你的中转 key
OPENAI_API_BASE=http://xxx/v1            # 中转服务地址

# ============================================
# 场景化模型配置
# ============================================
DEFAULT_MODEL=claude-sonnet-4-5-20250929      # 默认模型
CODE_GEN_MODEL=claude-sonnet-4-5-20250929     # 代码生成
VISION_MODEL=qwen-vl-max                       # 视觉理解
AGENT_MODEL=claude-sonnet-4-5-20250929        # Agent

# 场景参数
CODE_GEN_TEMPERATURE=0.3
CODE_GEN_MAX_TOKENS=8192
VISION_TEMPERATURE=0
VISION_MAX_TOKENS=4096
```

### 支持的场景

| 场景 | 代码 | 用途 | 当前模型 |
|------|------|------|---------|
| 默认 | `for_scenario("default")` | 通用场景 | claude-sonnet-4-5 |
| 代码生成 | `for_scenario("code_gen")` | 生成解析代码 | claude-sonnet-4-5 |
| 视觉理解 | `for_scenario("vision")` | 图片分析 | qwen-vl-max |
| Agent | `for_scenario("agent")` | LangChain Agent | claude-sonnet-4-5 |

## 💡 使用示例

### 示例 1：工具中使用

```python
# tools/code_generator.py
from utils.llm_client import LLMClient

@tool
def generate_code_from_html(html_content: str, target_json: Dict, ...):
    # 自动使用 CODE_GEN_MODEL 配置
    llm = LLMClient.for_scenario("code_gen")
    response = llm.chat_completion(messages=[...])
    return response
```

### 示例 2：自定义模型

```python
# 临时使用特定模型
llm = LLMClient(model="gpt-4-turbo-preview", temperature=0.7)
response = llm.chat_completion(messages=[...])
```

### 示例 3：混合使用

```python
# 代码生成用 Claude
code_llm = LLMClient.for_scenario("code_gen")  # claude-sonnet-4-5

# 视觉理解用 Qwen
vision_llm = LLMClient.for_scenario("vision")  # qwen-vl-max

# 都使用同一个 API Key 和 Base URL
```

## 🔧 工具和文档

### 配置工具

- `examples/check_config.py` - 快速检查配置是否正确
- `examples/test_llm_config.py` - 完整功能测试（需要安装依赖）

### 文档

- `docs/LLM_CONFIG_GUIDE.md` - 详细配置指南
- `docs/CONFIG_MIGRATION.md` - 迁移说明
- `.env.example` - 配置模板

## ✨ 优势

### 1. 完美适配中转服务

```bash
# 只需配置一次 API Key 和 Base URL
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=http://your-proxy.com/v1

# 所有场景自动使用这个配置
```

### 2. 灵活的模型选择

```bash
# 不同场景用不同模型
CODE_GEN_MODEL=claude-sonnet-4-5-20250929  # 代码生成用 Claude
VISION_MODEL=qwen-vl-max                    # 视觉理解用 Qwen
AGENT_MODEL=gpt-4-turbo-preview             # Agent 用 GPT-4
```

### 3. 简洁的代码

```python
# 之前：需要手动配置
llm = LLMClient(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_base=os.getenv("OPENAI_API_BASE"),
    model=os.getenv("VISION_MODEL"),
    temperature=0
)

# 现在：一行搞定
llm = LLMClient.for_scenario("vision")
```

## 📝 常见问题

**Q: 如何切换模型？**  
A: 编辑 `.env` 文件中对应场景的 `*_MODEL` 配置即可。

**Q: 所有场景必须配置吗？**  
A: 不必须。未配置的场景会使用 `DEFAULT_MODEL`。

**Q: 可以为单个调用指定模型吗？**  
A: 可以。使用 `LLMClient(model="xxx")` 直接初始化。

**Q: 旧代码会受影响吗？**  
A: 不会。Settings 类提供了向后兼容。

## 🎉 总结

这个配置方案：

1. ✅ **统一管理** - 一个 API Key，一个 Base URL
2. ✅ **灵活配置** - 不同场景用不同模型
3. ✅ **简单切换** - 只需修改 `.env` 文件
4. ✅ **代码简洁** - 一行代码创建客户端
5. ✅ **完美适配** - 专为 OpenAI 中转服务设计

现在你可以：
- 运行 `python examples/check_config.py` 查看配置
- 在代码中使用 `LLMClient.for_scenario("xxx")` 创建客户端
- 随时修改 `.env` 切换模型

有任何问题，查看 `docs/LLM_CONFIG_GUIDE.md` 获取详细说明！

