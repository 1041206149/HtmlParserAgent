# 修复说明：TypeError: unhashable type: 'dict'

## 问题描述

在 Stage 2 视觉理解阶段合并多个图片块的分析结果时，出现了 `TypeError: unhashable type: 'dict'` 错误。

### 错误堆栈
```
File "/Users/brown/Projects/HtmlParserAgent/agents/visual_understanding.py", line 263, in _merge_results
    best['value'] = list(set(all_values))
TypeError: unhashable type: 'dict'
```

### 根本原因

当处理数组类型的字段（如评论列表）时，原代码尝试使用 `set()` 对数组元素进行去重：

```python
# 原始代码（有问题）
if best.get('type') == 'array':
    all_values = []
    for c in candidates:
        if isinstance(c.get('value'), list):
            all_values.extend(c['value'])
    best['value'] = list(set(all_values))  # ❌ 如果 all_values 包含字典，这里会失败
```

Python 的 `set()` 只能处理可哈希的类型（如字符串、数字、元组），但不能处理字典这样的不可哈希类型。

## 解决方案

修改后的代码会根据数组元素的类型采用不同的去重策略：

1. **对于字典列表**：使用 JSON 字符串序列化进行去重
2. **对于简单类型列表**：使用 `set()` 去重
3. **对于无法处理的类型**：保留原值不去重

### 修复后的代码

```python
# 对于数组类型，合并所有非空值
if best.get('type') == 'array':
    all_values = []
    for c in candidates:
        if isinstance(c.get('value'), list):
            all_values.extend(c['value'])
    # 去重（处理字典和普通值）
    if all_values:
        # 检查第一个元素类型
        if isinstance(all_values[0], dict):
            # 对于字典列表，使用JSON字符串去重
            seen = set()
            unique_values = []
            for item in all_values:
                item_str = json.dumps(item, sort_keys=True, ensure_ascii=False)
                if item_str not in seen:
                    seen.add(item_str)
                    unique_values.append(item)
            best['value'] = unique_values
        else:
            # 对于简单类型，直接使用set去重
            try:
                best['value'] = list(set(all_values))
            except TypeError:
                # 如果还是不可哈希，保留原值
                best['value'] = all_values
```

## 测试验证

创建了测试脚本 `test_merge_fix.py` 验证修复：

### 测试用例 1：字典数组去重
```python
# 输入：包含重复字典的评论列表
[
  {'text': 'Show 3 comments', 'count': 3},
  {'text': 'Show 3 comments', 'count': 3},  # 重复
  {'text': 'Comment by Alice', 'count': 1}
]

# 输出：去重后的结果
[
  {'text': 'Show 3 comments', 'count': 3},
  {'text': 'Comment by Alice', 'count': 1}
]
```

### 测试用例 2：字符串数组去重
```python
# 输入：包含重复字符串的标签列表
['Python', 'Web', 'HTML', 'HTML', 'CSS', 'JavaScript']

# 输出：去重后的结果
['Python', 'Web', 'HTML', 'CSS', 'JavaScript']
```

## 影响范围

- **文件**：`/Users/brown/Projects/HtmlParserAgent/agents/visual_understanding.py`
- **方法**：`VisualUnderstandingAgent._merge_results()`
- **影响阶段**：Stage 2 视觉理解的结果合并

## 测试结果

✅ 所有测试通过

```
============================================================
✅ 测试通过！合并结果：
{
  "comments": {
    "type": "array",
    "description": "评论列表",
    "value": [
      {"text": "Show 3 comments", "count": 3},
      {"text": "Comment by Alice", "count": 1}
    ],
    "confidence": 0.75
  }
}

✅ 去重成功：2 个唯一项
============================================================
```

## 后续建议

1. 考虑为数组元素添加类型标注，更明确地处理不同类型
2. 可以添加更多边界情况的单元测试
3. 考虑是否需要对嵌套字典进行深度去重

---

**修复时间**：2025-11-14  
**修复版本**：v1.0.1  
**修复状态**：✅ 已完成并验证

