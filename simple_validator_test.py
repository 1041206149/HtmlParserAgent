#!/usr/bin/env python3
"""
简单的验证测试
"""
import json

# 模拟验证器的评估逻辑
def evaluate_result(parsed_data, expected_structure):
    """评估解析结果"""
    field_scores = {}
    issues = []

    for key, expected in expected_structure.items():
        if key not in parsed_data:
            field_scores[key] = 0.0
            issues.append(f"缺少字段: {key}")
            continue

        parsed_field = parsed_data[key]
        expected_type = expected.get('type', 'string')

        # 提取实际值（支持两种格式）
        if isinstance(parsed_field, dict) and 'value' in parsed_field:
            # 新格式：{'type': 'string', 'value': '...', 'confidence': 0.9}
            value = parsed_field.get('value')
            confidence = parsed_field.get('confidence', 1.0)
        else:
            # 旧格式：直接是值
            value = parsed_field
            confidence = 1.0

        # 检查类型和内容
        if expected_type == 'string':
            if isinstance(value, str) and value.strip():
                field_scores[key] = confidence
            else:
                field_scores[key] = 0.0
                issues.append(f"字段 {key} 为空或类型错误")

        elif expected_type == 'array':
            if isinstance(value, list):
                if value:
                    field_scores[key] = confidence
                else:
                    field_scores[key] = 0.5 * confidence
            else:
                field_scores[key] = 0.0
                issues.append(f"字段 {key} 类型错误，期望array")

        else:
            if value:
                field_scores[key] = confidence
            else:
                field_scores[key] = 0.0
                issues.append(f"字段 {key} 为空")

    # 计算总分
    total_score = sum(field_scores.values()) / len(field_scores) if field_scores else 0

    return {
        'total_score': total_score,
        'field_scores': field_scores,
        'issues': issues
    }


# 测试数据
parsed_data = {
    'title': {
        'type': 'string',
        'value': 'Secure coding in JavaScript',
        'confidence': 0.98
    },
    'author': {
        'type': 'string',
        'value': 'Tanya Janca',
        'confidence': 0.95
    },
    'tags': {
        'type': 'array',
        'value': ['javascript', 'security'],
        'confidence': 0.9
    }
}

expected_structure = {
    'title': {'type': 'string'},
    'author': {'type': 'string'},
    'tags': {'type': 'array'}
}

# 执行评估
result = evaluate_result(parsed_data, expected_structure)

print("="*60)
print("验证器测试")
print("="*60)
print(f"\n总分: {result['total_score']:.2%}")
print(f"\n字段评分:")
for field, score in result['field_scores'].items():
    print(f"  {field}: {score:.2%}")

if result['issues']:
    print(f"\n问题:")
    for issue in result['issues']:
        print(f"  - {issue}")
else:
    print("\n✅ 无问题")

if result['total_score'] > 0.85:
    print("\n✅ 测试通过！")
else:
    print(f"\n❌ 测试失败：分数太低 {result['total_score']:.2%}")

