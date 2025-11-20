# 12 - Validation & Retry (验证和重试)

## 核心概念

**验证和重试 = 确保 LLM 应用的可靠性和数据质量**

在生产环境中，需要处理三类问题：
1. **网络错误** - 临时性连接问题（用 `with_retry()`）
2. **模型故障** - 主模型不可用（用 `with_fallbacks()`）
3. **输出质量** - LLM 输出不符合要求（用验证 + 重试循环）

## 基本用法

### 1. with_retry() - 自动重试

处理临时性网络错误：

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("groq:llama-3.3-70b-versatile")

# 添加重试机制
llm_with_retry = model.with_retry(
    retry_if_exception_type=(ConnectionError, TimeoutError),
    wait_exponential_jitter=True,  # 指数退避 + 随机抖动
    stop_after_attempt=3  # 最多重试 3 次
)

response = llm_with_retry.invoke("你好")
```

**工作原理**：
```
第 1 次尝试 → 失败 (ConnectionError)
    ↓ 等待 1s
第 2 次尝试 → 失败 (ConnectionError)
    ↓ 等待 2s
第 3 次尝试 → 成功 ✓
```

### 2. with_fallbacks() - 降级方案

主模型失败时切换到备用模型：

```python
# 主模型
primary_model = init_chat_model("groq:llama-3.3-70b-versatile")

# 备用模型（更可靠/更便宜）
fallback_model = init_chat_model("groq:llama-3.1-8b-instant")

# 配置降级
llm_with_fallbacks = primary_model.with_fallbacks([fallback_model])

response = llm_with_fallbacks.invoke("介绍 Python")
# 主模型正常 → 使用主模型
# 主模型失败 → 自动切换到备用模型
```

### 3. Pydantic 验证

使用 Pydantic 约束确保数据质量：

```python
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    name: str = Field(min_length=2, max_length=20)
    age: int = Field(ge=0, le=150)  # 0-150 岁
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('邮箱必须包含 @')
        return v

# 使用
try:
    user = User(name="张三", age=200, email="invalid")  # 失败
except ValidationError as e:
    print(e.errors())  # 查看错误详情
```

## 核心组件

### 1. with_retry() 参数

| 参数 | 说明 | 默认值 |
|-----|------|-------|
| `retry_if_exception_type` | 哪些异常会触发重试 | `(Exception,)` |
| `stop_after_attempt` | 最大重试次数 | `3` |
| `wait_exponential_jitter` | 是否使用指数退避 + 抖动 | `False` |

**常见重试异常**：
```python
# 网络相关
(ConnectionError, TimeoutError, httpx.ConnectError)

# API 限流
(RateLimitError, )

# 所有异常（谨慎使用）
(Exception, )
```

### 2. with_fallbacks() 参数

```python
primary_model.with_fallbacks(
    fallbacks=[model1, model2],  # 备用模型列表（按顺序尝试）
    exceptions_to_handle=(Exception,)  # 触发降级的异常
)
```

**工作流程**：
```
尝试 primary_model → 失败
    ↓
尝试 model1 → 失败
    ↓
尝试 model2 → 成功 ✓
```

### 3. Pydantic Field 约束

| 约束 | 用途 | 示例 |
|-----|------|------|
| `gt` / `ge` | 数值 > / >= | `Field(gt=0)` |
| `lt` / `le` | 数值 < / <= | `Field(le=100)` |
| `min_length` / `max_length` | 字符串长度 | `Field(min_length=2)` |
| `pattern` | 正则表达式 | `Field(pattern=r'^\d{11}$')` |

```python
class Product(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    price: float = Field(gt=0, description="价格必须 > 0")
    stock: int = Field(ge=0, description="库存 >= 0")
```

### 4. 自定义字段验证

```python
from pydantic import field_validator

class Article(BaseModel):
    title: str
    content: str
    word_count: int

    @field_validator('word_count')
    @classmethod
    def validate_word_count(cls, v, info):
        # info.data 包含其他字段的值
        actual = len(info.data.get('content', ''))
        if abs(v - actual) > actual * 0.1:  # 允许 10% 误差
            raise ValueError(f'字数不匹配: 声称 {v}, 实际 {actual}')
        return v
```

## 实际应用

### 1. LLM 输出验证 + 重试循环

当 LLM 输出不符合验证规则时，重新提示：

```python
from pydantic import ValidationError

class Product(BaseModel):
    name: str = Field(min_length=2)
    price: float = Field(gt=0)

structured_llm = model.with_structured_output(Product)

max_retries = 3
text = "产品价格是 -100 元"  # 负价格会触发验证失败

for attempt in range(1, max_retries + 1):
    try:
        result = structured_llm.invoke(f"提取产品信息：{text}")
        # 验证通过
        break
    except ValidationError as e:
        error_msg = e.errors()[0]['msg']
        # 在提示中加入错误信息
        text = f"{text}\n注意: {error_msg}。请确保价格 > 0"
        if attempt == max_retries:
            raise  # 重试次数用完
```

**工作流程**：
```
第 1 次尝试:
  LLM 输出: price = -100
  验证: ✗ 失败 (price 必须 > 0)

第 2 次尝试（修正提示）:
  提示: "...注意: price 必须 > 0"
  LLM 输出: price = 100
  验证: ✓ 通过
```

### 2. 完整的验证 + 重试函数

封装为可复用函数：

```python
from typing import Optional

def extract_with_validation(
    text: str,
    max_retries: int = 3
) -> Optional[Product]:
    """带验证的提取函数"""
    structured_llm = model.with_structured_output(Product)
    current_text = text

    for attempt in range(1, max_retries + 1):
        try:
            result = structured_llm.invoke(f"提取: {current_text}")
            # 额外的业务验证
            if result.price < 0:
                raise ValueError("价格必须为正数")
            return result
        except (ValidationError, ValueError) as e:
            if attempt < max_retries:
                error_msg = str(e)
                current_text = f"{text}\n错误: {error_msg}"
            else:
                return None  # 失败

# 使用
result = extract_with_validation("产品 A 价格 999 元")
if result:
    print(f"成功: {result.name}, {result.price}")
else:
    print("提取失败")
```

### 3. 组合策略（生产环境推荐）

网络重试 + 模型降级 + 输出验证：

```python
# ⚠️ 重要：调用顺序必须是
# 1. with_structured_output() - 先创建结构化输出
# 2. with_retry() - 再添加重试
# 3. with_fallbacks() - 最后添加降级

# 1. 先创建结构化输出（必须先调用！）
structured_primary = model.with_structured_output(Product)

# 2. 备用模型（也要先创建结构化输出）
fallback_model = init_chat_model("groq:llama-3.1-8b-instant")
structured_fallback = fallback_model.with_structured_output(Product)

# 3. 添加重试（在结构化输出之后）
primary_with_retry = structured_primary.with_retry(
    retry_if_exception_type=(ConnectionError, TimeoutError),
    stop_after_attempt=2
)

# 4. 添加降级（最后一步）
robust_llm = primary_with_retry.with_fallbacks([structured_fallback])

# 使用
result = robust_llm.invoke("提取产品信息...")
# → 输出自动验证（Pydantic）
# → 网络错误会重试
# → 主模型失败会降级
```

**防护层级**：
```
Layer 1: Pydantic 验证 - 确保输出质量
    ↓
Layer 2: with_retry() - 处理临时网络错误
    ↓
Layer 3: with_fallbacks() - 处理模型故障
```

**❌ 错误的调用顺序**：
```python
# ❌ 这样会报错！
primary = model.with_retry(...)
robust_llm = primary.with_fallbacks([fallback])
structured_llm = robust_llm.with_structured_output(Product)
# AttributeError: 'RunnableRetry' object has no attribute 'with_structured_output'
```

**✅ 正确的调用顺序**：
```python
# ✅ 先 structured_output，再 retry，最后 fallbacks
structured = model.with_structured_output(Product)
with_retry = structured.with_retry(...)
final = with_retry.with_fallbacks([...])
```

## 常见问题

### 1. 何时使用 with_retry()？

**适用场景**：
- ✅ 网络波动
- ✅ API 临时限流
- ✅ 超时错误

**不适用场景**：
- ❌ 提示词错误（重试无意义）
- ❌ 参数错误（永远不会成功）
- ❌ 模型不支持某个功能（需要换模型）

### 2. 重试次数设多少合适？

```python
# 推荐配置
with_retry(stop_after_attempt=3)  # 大多数场景

# 高可用场景
with_retry(stop_after_attempt=5)  # 容忍更多失败

# 快速失败
with_retry(stop_after_attempt=1)  # 不重试，立即报错
```

**注意**：重试次数过多会增加延迟。

### 3. 如何避免无限重试循环？

**问题**：
```python
# ❌ 危险！可能无限循环
while True:
    try:
        result = llm.invoke(...)
        break
    except:
        continue  # 永远重试
```

**解决方案**：
```python
# ✅ 限制最大次数
max_retries = 3
for attempt in range(max_retries):
    try:
        result = llm.invoke(...)
        break
    except Exception as e:
        if attempt == max_retries - 1:
            raise  # 用完次数，抛出异常
```

### 4. ValidationError 和普通异常的区别？

```python
try:
    user = User(age=200)  # Pydantic 验证失败
except ValidationError as e:
    # 捕获验证错误
    print(e.errors())  # 详细错误列表

try:
    result = llm.invoke(...)  # 网络错误
except ConnectionError as e:
    # 捕获网络错误
    print(e)
```

**分别处理**：
```python
try:
    result = structured_llm.invoke(...)
except ValidationError as e:
    # 输出验证失败 → 重试循环
    print("数据格式错误，重新提取")
except ConnectionError as e:
    # 网络错误 → with_retry() 已处理
    print("网络问题")
```

### 5. 如何验证嵌套模型？

```python
class Address(BaseModel):
    city: str = Field(min_length=2)
    district: str

class Company(BaseModel):
    name: str
    address: Address  # 嵌套

    @field_validator('address')
    @classmethod
    def validate_address(cls, v):
        # 验证嵌套对象
        if v.city == "未知":
            raise ValueError("城市不能是'未知'")
        return v

# 自动验证整个层级
company = Company(
    name="公司",
    address=Address(city="北京", district="朝阳")
)
```

### 6. with_structured_output() 必须在最前面吗？

**是的！非常重要！**

**错误示例**：
```python
# ❌ 错误：先 retry，后 structured_output
llm_with_retry = model.with_retry(...)
structured = llm_with_retry.with_structured_output(Product)
# AttributeError: 'RunnableRetry' object has no attribute 'with_structured_output'
```

**正确示例**：
```python
# ✅ 正确：先 structured_output，再 retry
structured = model.with_structured_output(Product)
llm_with_retry = structured.with_retry(...)
```

**原因**：
- `with_structured_output()` 是 `ChatModel` 的方法
- `with_retry()` 返回 `RunnableRetry` 对象
- `RunnableRetry` 没有 `with_structured_output()` 方法

**记忆规则**：
```
structured_output → retry → fallbacks
（从内到外包装）
```

## 最佳实践

```python
# 1. 生产环境标准配置（正确的调用顺序）
def create_robust_structured_llm(model_name: str, schema: type[BaseModel]):
    """
    创建鲁棒的结构化 LLM

    正确顺序：structured_output → retry → fallbacks
    """
    # 主模型：先创建结构化输出
    primary_structured = init_chat_model(model_name).with_structured_output(schema)

    # 备用模型：也要先创建结构化输出
    fallback_model = init_chat_model("groq:llama-3.1-8b-instant")
    fallback_structured = fallback_model.with_structured_output(schema)

    # 添加重试和降级
    return (
        primary_structured
        .with_retry(
            retry_if_exception_type=(ConnectionError, TimeoutError),
            stop_after_attempt=3,
            wait_exponential_jitter=True
        )
        .with_fallbacks([fallback_structured])
    )

# 2. 数据提取模板（正确版本）
def extract_with_validation(
    text: str,
    schema: type[BaseModel],
    max_retries: int = 3
) -> Optional[BaseModel]:
    """通用的验证 + 重试提取"""
    # 使用上面的函数创建鲁棒 LLM
    robust_llm = create_robust_structured_llm(
        "groq:llama-3.3-70b-versatile",
        schema
    )

    current_text = text
    for attempt in range(1, max_retries + 1):
        try:
            return robust_llm.invoke(current_text)
        except ValidationError as e:
            if attempt < max_retries:
                error = e.errors()[0]['msg']
                current_text = f"{text}\n错误: {error}"
            else:
                return None
        except Exception as e:
            if attempt < max_retries:
                current_text = f"{text}\n重要: 确保类型正确"
            else:
                return None

# 3. 清晰的错误处理
try:
    result = extract_with_validation(text, Product)
    if result:
        # 成功
        process(result)
    else:
        # 验证失败
        log_error("数据质量问题")
except Exception as e:
    # 其他错误
    log_error(f"系统错误: {e}")
```

## 核心要点

1. **with_retry()** - 处理临时性网络错误
2. **with_fallbacks()** - 模型降级/备用方案
3. **Pydantic Field 约束** - 类型和格式验证
4. **@field_validator** - 自定义字段验证
5. **ValidationError** - 捕获验证失败
6. **重试循环** - LLM 输出验证失败时重新提示
7. **组合策略** - retry + fallbacks + validation = 高可用系统

## 生产环境建议

| 场景 | 策略 |
|-----|------|
| 网络不稳定 | `with_retry(stop_after_attempt=3)` |
| 高可用性要求 | `with_fallbacks([backup_model])` |
| 数据质量要求高 | Pydantic 验证 + 重试循环 |
| 成本敏感 | 主模型（昂贵）+ 备用模型（便宜） |

**推荐组合**：
```python
robust_llm = (
    expensive_model
    .with_retry(stop_after_attempt=2)
    .with_fallbacks([cheap_model])
    .with_structured_output(ValidatedSchema)
)
```

## 下一步

**13_rag_basics** - 学习 RAG 基础（文档加载、向量存储、检索）
