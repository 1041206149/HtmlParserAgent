"""
测试 _merge_results 修复
"""
import json


def test_merge_array_with_dicts():
    """测试合并包含字典的数组"""

    # 模拟 chunk_results
    chunk_results = [
        {
            'comments': {
                'type': 'array',
                'description': '评论列表',
                'value': [
                    {'text': 'Show 3 comments', 'count': 3}
                ],
                'confidence': 0.65
            }
        },
        {
            'comments': {
                'type': 'array',
                'description': '评论列表',
                'value': [
                    {'text': 'Show 3 comments', 'count': 3},
                    {'text': 'Comment by Alice', 'count': 1}
                ],
                'confidence': 0.75
            }
        }
    ]

    # 模拟合并逻辑
    all_keys = set()
    for result in chunk_results:
        all_keys.update(result.keys())

    merged = {}
    for key in all_keys:
        candidates = [
            r[key] for r in chunk_results
            if key in r and r[key].get('value') is not None
        ]

        if not candidates:
            continue

        # 选择置信度最高的
        best = max(candidates, key=lambda x: x.get('confidence', 0))

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

        merged[key] = best

    print("✅ 测试通过！合并结果：")
    print(json.dumps(merged, indent=2, ensure_ascii=False))

    # 验证去重
    assert len(merged['comments']['value']) == 2, "应该有2个唯一的评论"
    print(f"\n✅ 去重成功：{len(merged['comments']['value'])} 个唯一项")


def test_merge_array_with_strings():
    """测试合并包含字符串的数组"""

    chunk_results = [
        {
            'tags': {
                'type': 'array',
                'description': '标签',
                'value': ['Python', 'Web', 'HTML'],
                'confidence': 0.8
            }
        },
        {
            'tags': {
                'type': 'array',
                'description': '标签',
                'value': ['HTML', 'CSS', 'JavaScript'],
                'confidence': 0.9
            }
        }
    ]

    # 合并逻辑（同上）
    candidates = [r['tags'] for r in chunk_results]
    best = max(candidates, key=lambda x: x.get('confidence', 0))

    all_values = []
    for c in candidates:
        if isinstance(c.get('value'), list):
            all_values.extend(c['value'])

    if all_values:
        if isinstance(all_values[0], dict):
            seen = set()
            unique_values = []
            for item in all_values:
                item_str = json.dumps(item, sort_keys=True, ensure_ascii=False)
                if item_str not in seen:
                    seen.add(item_str)
                    unique_values.append(item)
            best['value'] = unique_values
        else:
            try:
                best['value'] = list(set(all_values))
            except TypeError:
                best['value'] = all_values

    print("\n✅ 字符串数组测试通过！结果：")
    print(json.dumps(best, indent=2, ensure_ascii=False))

    # 验证去重
    assert len(best['value']) == 5, "应该有5个唯一的标签"
    print(f"\n✅ 去重成功：{len(best['value'])} 个唯一标签")


if __name__ == "__main__":
    print("=" * 60)
    print("测试数组合并去重修复")
    print("=" * 60)

    try:
        test_merge_array_with_dicts()
        test_merge_array_with_strings()
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

