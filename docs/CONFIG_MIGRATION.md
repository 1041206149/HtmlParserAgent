# LLM 配置优化迁移说明

## 变更概述

本次更新优化了 LLM API 的配置方式，采用**基于场景的模型配置**，使得不同工具可以使用不同的模型，同时保持配置的统一性。

## 主要变更

### 1. 环境变量配置 (.env)

**之前：**
```bash
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=http://xxx/v1
OPENAI_MODEL=claude-sonnet-4-5-20250929
OPENAI_TEMPERATURE=0
VISION_MODEL=qwen-vl-max
```

**现在：**
```bash
# 统一的 API 配置
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=http://xxx/v1

# 场景化模型配置
DEFAULT_MODEL=claude-sonnet-4-5-20250929
CODE_GEN_MODEL=claude-sonnet-4-5-20250929
VISION_MODEL=qwen-vl-max
AGENT_MODEL=claude-sonnet-4-5-20250929

# 场景参数
CODE_GEN_TEMPERATURE=0.3
CODE_GEN_MAX_TOKENS=8192
VISION_TEMPERATURE=0
VISION_MAX_TOKENS=4096
```

### 2. Settings 类 (config/settings.py)

**新增字段：**
- `default_model` / `default_temperature`
- `code_gen_model` / `code_gen_temperature` / `code_gen_max_tokens`
- `vision_model` / `vision_temperature` / `vision_max_tokens`
- `agent_model` / `agent_temperature`

**向后兼容：**
- `settings.openai_model` → 自动映射到 `settings.default_model`
- `settings.openai_temperature` → 自动映射到 `settings.default_temperature`

### 3. LLMClient 类 (utils/llm_client.py)

**新增方法：**
```python
@classmethod
def for_scenario(cls, scenario: ScenarioType = "default") -> LLMClient:
    """根据场景创建 LLM 客户端（推荐使用）"""
```

**支持的场景：**
- `"default"` - 默认场景
- `"code_gen"` - 代码生成场景
- `"vision"` - 视觉理解场景
- `"agent"` - Agent 场景

### 4. 工具更新

#### code_generator.py
**之前：**
```python
llm_client = LLMClient.from_settings(settings)
response = llm_client.chat_completion(
    messages=[...],
    temperature=0.3,
    max_tokens=8192
)
```

**现在：**
```python
llm_client = LLMClient.for_scenario("code_gen")
response = llm_client.chat_completion(
    messages=[...],
    max_tokens=settings.code_gen_max_tokens if settings else int(os.getenv("CODE_GEN_MAX_TOKENS", "8192"))
)
```

#### visual_understanding.py
**之前：**
```python
llm = LLMClient(model=model)
response = llm.vision_completion(
    prompt=prompt,
    image_data=image_data,
    max_tokens=4096
)
```

**现在：**
```python
llm = LLMClient.for_scenario("vision") if not model else LLMClient(model=model)
response = llm.vision_completion(
    prompt=prompt,
    image_data=image_data,
    max_tokens=int(os.getenv("VISION_MAX_TOKENS", "4096"))
)
```

## 迁移步骤

### 1. 更新 .env 文件

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，填入你的配置
# 重点关注：
# - OPENAI_API_KEY
# - OPENAI_API_BASE
# - 各场景的模型配置
```

### 2. 更新代码（如果有自定义工具）

**推荐使用场景化创建：**
```python
# 旧方式
llm = LLMClient(model=os.getenv("OPENAI_MODEL"))

# 新方式（推荐）
llm = LLMClient.for_scenario("default")
```

### 3. 测试配置

```bash
# 运行测试脚本
python examples/test_llm_config.py
```

## 优势

### 1. 灵活性
- ✅ 不同场景使用不同模型
- ✅ 只需修改 .env 文件即可切换模型
- ✅ 支持混合使用多个模型

### 2. 统一性
- ✅ 所有模型共用同一个 API Key 和 Base URL
- ✅ 适合使用 OpenAI 中转服务
- ✅ 配置集中管理

### 3. 可维护性
- ✅ 代码更简洁，减少重复配置
- ✅ 场景化命名，语义清晰
- ✅ 向后兼容，不影响旧代码

### 4. 成本优化
- ✅ 为不同场景配置不同模型
- ✅ 在保证效果的前提下降低成本
- ✅ 灵活调整各场景的参数

## 使用示例

### 示例 1：使用中转服务，所有场景用 Claude

```bash
# .env
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=http://your-proxy.com/v1

DEFAULT_MODEL=claude-sonnet-4-5-20250929
CODE_GEN_MODEL=claude-sonnet-4-5-20250929
VISION_MODEL=qwen-vl-max
AGENT_MODEL=claude-sonnet-4-5-20250929
```

### 示例 2：混合使用不同模型

```bash
# .env
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=http://your-proxy.com/v1

DEFAULT_MODEL=gpt-4-turbo-preview
CODE_GEN_MODEL=claude-sonnet-4-5-20250929  # 代码生成用 Claude
VISION_MODEL=qwen-vl-max                    # 视觉理解用 Qwen
AGENT_MODEL=gpt-4-turbo-preview             # Agent 用 GPT-4
```

### 示例 3：代码中使用

```python
from utils.llm_client import LLMClient

# 代码生成
llm = LLMClient.for_scenario("code_gen")
code = llm.chat_completion(messages=[...])

# 视觉理解
llm = LLMClient.for_scenario("vision")
result = llm.vision_completion(prompt="...", image_data="...")

# Agent
llm = LLMClient.for_scenario("agent")
response = llm.chat_completion(messages=[...])
```

## 文档

- 📖 [完整配置指南](./LLM_CONFIG_GUIDE.md)
- 🧪 [测试脚本](../examples/test_llm_config.py)
- 📝 [配置示例](.env.example)

## 常见问题

**Q: 旧代码会受影响吗？**  
A: 不会。Settings 类提供了向后兼容的属性映射。

**Q: 如何快速切换模型？**  
A: 只需修改 .env 文件中对应场景的 `*_MODEL` 配置即可。

**Q: 可以为某个工具单独指定模型吗？**  
A: 可以。在调用工具时传入 `model` 参数即可覆盖默认配置。

**Q: 如何验证配置是否生效？**  
A: 运行 `python examples/test_llm_config.py` 查看当前配置。

## 反馈

如有问题或建议，请提交 Issue 或 PR。

