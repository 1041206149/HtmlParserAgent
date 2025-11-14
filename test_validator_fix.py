"""
测试修复后的验证器
"""
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from agents.validator import ValidationOrchestrator
from config.settings import Settings


def test_evaluate_result():
    """测试评估结果方法"""

    # 创建验证器
    settings = Settings()
    validator = ValidationOrchestrator(settings)

    # 模拟解析结果（新格式 - 包含 type/value/confidence）
    parsed_data = {
        'title': {
            'type': 'string',
            'description': '文章标题',
            'value': 'Secure coding in JavaScript',
            'confidence': 0.98
        },
        'author': {
            'type': 'string',
            'description': '文章作者',
            'value': 'Tanya Janca',
            'confidence': 0.95
        },
        'tags': {
            'type': 'array',
            'description': '文章标签',
            'value': ['javascript', 'security'],
            'confidence': 0.9
        },
        'content': {
            'type': 'string',
            'description': '文章正文内容',
            'value': 'JavaScript is the front-end...',
            'confidence': 0.95
        },
        'images': {
            'type': 'array',
            'description': '文章配图',
            'value': ['https://example.com/image.jpg'],
            'confidence': 0.8
        }
    }

    # 期望结构
    expected_structure = {
        'title': {'type': 'string', 'description': '文章标题'},
        'author': {'type': 'string', 'description': '文章作者'},
        'tags': {'type': 'array', 'description': '文章标签'},
        'content': {'type': 'string', 'description': '文章正文内容'},
        'images': {'type': 'array', 'description': '文章配图'}
    }

    # 评估
    result = validator._evaluate_result(parsed_data, expected_structure)

    print("="*60)
    print("验证器测试结果")
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

    # 验证分数是否合理
    assert result['total_score'] > 0.85, f"总分太低: {result['total_score']}"
    assert all(score > 0.7 for score in result['field_scores'].values()), "某些字段分数太低"

    print("\n" + "="*60)
    print("✅ 测试通过！验证器能够正确处理新格式的解析结果")
    print("="*60)


def test_evaluate_result_with_empty_values():
    """测试空值情况"""

    settings = Settings()
    validator = ValidationOrchestrator(settings)

    # 模拟包含空值的解析结果
    parsed_data = {
        'title': {
            'type': 'string',
            'description': '文章标题',
            'value': 'Test Title',
            'confidence': 0.98
        },
        'author': {
            'type': 'string',
            'description': '文章作者',
            'value': '',  # 空值
            'confidence': 0.0
        },
        'tags': {
            'type': 'array',
            'description': '文章标签',
            'value': [],  # 空数组
            'confidence': 0.5
        }
    }

    expected_structure = {
        'title': {'type': 'string'},
        'author': {'type': 'string'},
        'tags': {'type': 'array'}
    }

    result = validator._evaluate_result(parsed_data, expected_structure)

    print("\n空值测试结果:")
    print(f"总分: {result['total_score']:.2%}")
    print(f"问题数: {len(result['issues'])}")

    # 空数组应该得到部分分数
    assert result['field_scores']['tags'] > 0, "空数组应该得到部分分数"
    # 空字符串应该得 0 分
    assert result['field_scores']['author'] == 0, "空字符串应该得 0 分"

    print("✅ 空值处理正确")


if __name__ == "__main__":
    try:
        test_evaluate_result()
        test_evaluate_result_with_empty_values()

        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

