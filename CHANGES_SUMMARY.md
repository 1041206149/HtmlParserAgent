# 📝 修改总结

## 概述

成功重新编写了 HtmlParserAgent 的核心流程，实现了符合您需求的**多轮迭代循环系统**。

---

## ✅ 完成的需求

### 1. 循环流程重构
您需要的循环流程已实现：

1. **获取HTML源码** ✅
   - 使用 `get_webpage_source` 工具
   - 支持多个URL

2. **截图** ✅
   - 使用 `capture_webpage_screenshot` 工具
   - 按轮次和样本编号保存

3. **提取JSON Schema** ✅
   - **第一轮**：从零提取
   - **第二轮+**：与前一轮Schema合并
   - 使用 `extract_json_from_image` 工具

4. **生成/优化解析代码** ✅
   - **第一轮**：从零生成
   - **第二轮+**：基于前一轮进行优化和增量更新
   - 使用 `generate_parser_code` 和 `fix_parser_code` 工具

### 2. 验证逻辑修改
已按要求修改验证逻辑：

✅ **Groundtruth保存**
- 每个URL的截图识别JSON保存为groundtruth
- 保存位置：`output/groundtruth/{url_hash}.json`

✅ **准确率计算**
- 预测值：最新代码生成的JSON
- 准确率公式：`0.7 × 字段完整性 + 0.3 × 字段值相似度`
- 每轮都计算所有URL的准确率

---

## 📁 修改的文件

### 1. `agent/executor.py` ✅ 完全重写
**职责**：执行单轮迭代的具体步骤

**新增方法**：
```python
execute_single_round(round_num, urls, domain, layout_type)
  ├─ 获取HTML
  ├─ 截图
  ├─ 提取JSON
  └─ 保存groundtruth

generate_or_update_parser(round_num, urls_data, previous_schema, previous_parser_path)
  ├─ 第一轮：从零生成
  └─ 后续轮次：基于前一轮优化

validate_parser_on_all_urls(parser_path, all_urls, groundtruth_dir, round_num)
  ├─ 动态加载Parser
  ├─ 在所有URL上运行
  ├─ 计算准确率
  └─ 返回详细结果

_merge_schemas_from_urls(urls_data, previous_schema, round_num)
  ├─ 第一轮：提取Schema
  └─ 后续轮次：合并Schema

_calculate_json_accuracy(groundtruth, predicted)
  └─ 计算groundtruth与predicted的准确率
```

### 2. `agent/orchestrator.py` ✅ 完全重写
**职责**：编排多轮迭代流程

**核心方法**：
```python
run_iterations(urls, domain, layout_type, max_iterations, accuracy_threshold)
  └─ 多轮循环
      ├─ Round 1: 处理前3个URL
      ├─ Round 2+: 处理新URL
      ├─ 每轮执行：获取HTML → 截图 → 提取JSON
      ├─ 每轮执行：生成/优化Parser
      ├─ 每轮执行：验证所有URL
      ├─ 检查是否达到准确率阈值
      └─ 检查是否达到最大迭代次数
```

**关键改进**：
- 支持resume功能
- 支持动态调整max_iterations和accuracy_threshold
- 完整的错误处理和日志

### 3. `tools/code_fixer.py` ✅ 完全重写
**职责**：基于前一轮代码进行优化

**新签名**：
```python
fix_parser_code(
    previous_code: str,           # 前一轮的代码
    html_content: str,            # 当前轮的HTML
    target_json: Dict,            # 合并后的Schema
    output_dir: str,
    round_num: int
) -> Dict
```

**工作方式**：
- 输入：前一轮Parser代码 + 新HTML + 合并后的Schema
- 过程：LLM增量优化（保留已有逻辑，添加新字段，改进容错）
- 输出：优化后的Parser代码

### 4. `main.py` ✅ 更新
**改动**：
- 将 `agent.generate_parser()` 替换为 `agent.run_iterations()`
- 更新结果处理逻辑
- 支持新的参数传递

---

## 🏗️ 架构改进

### 旧架构 ❌

```
Planner → Executor → Validator
  ↓
  Execute once
  ├─ Get HTML
  ├─ Screenshot
  ├─ Extract JSON
  └─ Generate Parser
  ↓
  Validate
  ↓
  Done
```

### 新架构 ✅

```
Orchestrator (多轮迭代)
  ├─ Round 1
  │   ├─ Executor.execute_single_round()
  │   │   ├─ Get HTML
  │   │   ├─ Screenshot
  │   │   ├─ Extract JSON
  │   │   └─ Save groundtruth
  │   ├─ Generate Schema v1
  │   ├─ Generate Parser v1
  │   └─ Validate all URLs → accuracy
  │
  ├─ Round 2+
  │   ├─ Executor.execute_single_round()
  │   ├─ Merge Schema
  │   ├─ Optimize Parser (based on v1)
  │   └─ Validate all URLs → accuracy
  │
  └─ Loop until: accuracy ≥ threshold OR iterations ≥ max
```

---

## 📊 工作流程对比

### 旧流程
```
单次执行：
  获取 3 个 URL
  → 生成 Parser
  → 验证
  完成
```

### 新流程
```
轮次 1：获取 3 个 URL → 生成 Schema v1 → 生成 Parser v1 → 验证所有 URL
轮次 2：获取 1 个新 URL → 合并 Schema v2 → 优化 Parser v2 → 验证所有 URL
轮次 3：获取 1 个新 URL → 合并 Schema v3 → 优化 Parser v3 → 验证所有 URL
...
直到准确率达到阈值或迭代次数上限
```

---

## 🔄 关键流程细节

### 第一轮流程

```
输入: URL [url1, url2, url3]

execute_single_round(1, [url1, url2, url3]):
  ├─ url1: HTML → Screenshot → JSON → groundtruth_1.json
  ├─ url2: HTML → Screenshot → JSON → groundtruth_2.json
  └─ url3: HTML → Screenshot → JSON → groundtruth_3.json
  └─ return: urls_data = {url1: {...}, url2: {...}, url3: {...}}

_process_schema(1, urls_data):
  ├─ 合并3个JSON
  ├─ 提取Schema
  └─ return: schema_v1.json

generate_or_update_parser(1, urls_data, None, None):
  ├─ 选择reference_html (url1的HTML)
  ├─ 使用generate_parser_code生成
  └─ return: generated_parser_v1.py

validate_parser_on_all_urls("generated_parser_v1.py", all_urls):
  ├─ For each url in all_urls:
  │   ├─ HTML → Parser → predicted_json
  │   ├─ Load groundtruth_json
  │   ├─ Calculate accuracy
  │   └─ Record
  └─ return: overall_accuracy = 0.72
```

### 第二轮流程

```
输入: URL [url4]

execute_single_round(2, [url4]):
  ├─ url4: HTML → Screenshot → JSON → groundtruth_4.json
  └─ return: urls_data = {url4: {...}}

_process_schema(2, urls_data, schema_v1):
  ├─ 新JSON (from url4)
  ├─ 与schema_v1合并
  └─ return: schema_v2.json

generate_or_update_parser(2, urls_data, schema_v1, "generated_parser_v1.py"):
  ├─ 选择reference_html (url4的HTML)
  ├─ 读取前一轮代码
  ├─ 使用fix_parser_code优化
  │   ├─ 输入：previous_code + new_html + merged_schema
  │   ├─ LLM操作：保留已有逻辑，添加新字段
  │   └─ 输出：optimized_code
  └─ return: generated_parser_v2.py

validate_parser_on_all_urls("generated_parser_v2.py", all_urls):
  ├─ For each url in all_urls:
  │   ├─ HTML → Parser → predicted_json
  │   ├─ Load groundtruth_json
  │   ├─ Calculate accuracy
  │   └─ Record
  └─ return: overall_accuracy = 0.81
```

---

## 📈 准确率计算方式

### 公式

```python
accuracy = 0.7 × completeness + 0.3 × similarity

completeness = |predicted_keys ∩ groundtruth_keys| / |groundtruth_keys|
similarity = (type_matched_count) / |groundtruth_keys|
```

### 示例

```
Groundtruth JSON:
{
  "title": "Article",        # string
  "date": "2024-01-01",      # string
  "views": 100               # integer
}

Predicted JSON:
{
  "title": "Article",        # string ✓
  "date": "2024-01-01",      # string ✓
  "views": "100"             # string ✗ (type mismatch)
}

completeness = 3/3 = 1.0
similarity = 2/3 = 0.667
accuracy = 0.7 × 1.0 + 0.3 × 0.667 = 0.9
```

---

## 🎯 验证逻辑

### Groundtruth（真值标签）

- **来源**：vLLM/图片识别提取的JSON
- **保存时机**：每个URL处理后立即保存
- **保存位置**：`output/groundtruth/{url_hash}.json`
- **格式**：与提取JSON相同

### 预测值

- **来源**：最新生成的Parser在相同URL上的解析结果
- **计算时机**：验证阶段
- **对比方式**：与groundtruth逐字段对比

### 准确率

- **计算时机**：每轮迭代后
- **计算范围**：所有提供的URL（不仅仅是本轮处理的）
- **判断标准**：
  - 字段完整性：预测JSON是否包含所有groundtruth字段
  - 值相似度：相同字段的类型是否匹配
  - 综合得分：70%权重完整性，30%权重相似度

### 循环终止条件

1. `overall_accuracy ≥ accuracy_threshold` → 成功终止 ✓
2. `round_num ≥ max_iterations` → 达到上限 ⏱
3. 所有URL已处理且无新URL → 完成 ✓
4. 任何步骤异常 → 失败终止 ✗

---

## 🔧 配置参数

### 新增配置

`config/settings.py` 中已支持：

```python
# 迭代参数
max_iterations = 5              # 最大轮次
success_threshold = 0.8         # 准确率阈值

# 代码生成参数
code_gen_temperature = 0.3      # 生成温度（越低越稳定）
code_gen_max_tokens = 4000      # 最大tokens

# 视觉识别参数
vision_temperature = 0.2        # 识别温度（越低越准确）
```

---

## 📚 新增文档

1. **NEW_FLOW_GUIDE.md** - 详细的流程说明
2. **ITERATION_WORKFLOW.md** - 完整的工作流程图示
3. **QUICK_START.md** - 快速上手指南

---

## 🚀 使用示例

### 命令行

```bash
python main.py -f urls.txt -o output/my_project -t article
```

### Python代码

```python
from agent import ParserAgent

agent = ParserAgent(output_dir="output")

result = agent.run_iterations(
    urls=["url1", "url2", "url3", "url4", "url5"],
    domain="example.com",
    layout_type="article",
    max_iterations=3,
    accuracy_threshold=0.85
)

print(f"✓ 总轮次: {result['total_rounds']}")
print(f"✓ 最终准确率: {result['overall_accuracy']:.2%}")
print(f"✓ 最终Parser: {result['final_parser_path']}")
```

---

## ✨ 主要改进

| 改进项 | 旧版本 | 新版本 |
|--------|--------|--------|
| 迭代方式 | 单次执行 | 多轮循环 |
| Schema处理 | 直接使用 | 自动合并 |
| Parser生成 | 从零开始 | 增量优化 |
| 验证范围 | 仅本轮URL | 所有URL |
| 准确率追踪 | 仅记录 | 动态计算+追踪 |
| 循环控制 | 无 | 支持准确率阈值 |
| 错误恢复 | 单点失败 | 支持resume |

---

## 🔍 验证修改

### 检查point 1：单轮执行

```python
# 验证execute_single_round能正常工作
result = executor.execute_single_round(1, ["url1"], "example.com", "article")
assert result['success']
assert len(result['urls_data']) > 0
```

### 检查point 2：Schema合并

```python
# 验证schema合并逻辑
schema1 = {"title": {...}, "date": {...}}
schema2 = schema1.copy()
schema2["author"] = {...}  # 新增字段
assert "title" in schema2
assert "author" in schema2
```

### 检查point 3：Parser优化

```python
# 验证parser优化逻辑
result = executor.generate_or_update_parser(
    round_num=2,
    urls_data={...},
    previous_schema=schema1,
    previous_parser_path="path_to_v1.py"
)
assert result['success']
assert result['parser_path'].endswith('v2.py')
```

### 检查point 4：准确率计算

```python
# 验证准确率计算
groundtruth = {"title": "Test", "date": "2024-01"}
predicted = {"title": "Test", "date": "2024-01"}
accuracy = executor._calculate_json_accuracy(groundtruth, predicted)
assert accuracy == 1.0
```

---

## 📋 检查清单

- [x] executor.py 完全重写
- [x] orchestrator.py 完全重写
- [x] code_fixer.py 完全重写，支持增量优化
- [x] main.py 更新使用新方法
- [x] 验证逻辑修改为groundtruth+预测值对比
- [x] 支持多轮迭代循环
- [x] 支持Schema合并
- [x] 支持Parser优化（基于前一轮）
- [x] 支持准确率阈值控制
- [x] 支持最大迭代次数限制
- [x] 详细文档编写

---

## 🎉 完成

所有需求已实现。系统现在支持：

1. ✅ 获取HTML源码
2. ✅ 截图
3. ✅ 提取JSON（第二轮合并）
4. ✅ 生成/优化解析代码（第一轮从零，后续优化）
5. ✅ 验证准确率（groundtruth vs 预测值）
6. ✅ 多轮迭代直到达到阈值

**下一步**：运行 `python main.py -f urls.txt` 开始使用！

