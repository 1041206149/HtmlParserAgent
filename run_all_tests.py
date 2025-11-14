#!/usr/bin/env python3
"""
运行所有测试
"""
import sys
import subprocess
from pathlib import Path


def run_test(test_file):
    """运行单个测试文件"""
    print(f"\n{'='*60}")
    print(f"运行测试: {test_file.name}")
    print('='*60)

    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            cwd=test_file.parent.parent,
            capture_output=True,
            text=True,
            timeout=120
        )

        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"✗ 测试超时: {test_file.name}")
        return False
    except Exception as e:
        print(f"✗ 运行失败: {e}")
        return False


def main():
    """主函数"""
    tests_dir = Path(__file__).parent / "tests"

    # 查找所有测试文件
    test_files = sorted(tests_dir.glob("test_*.py"))

    if not test_files:
        print("未找到测试文件")
        return 1

    print("="*60)
    print(f"HtmlParserAgent 测试套件")
    print(f"找到 {len(test_files)} 个测试文件")
    print("="*60)

    results = []
    for test_file in test_files:
        success = run_test(test_file)
        results.append((test_file.name, success))

    # 输出汇总
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{name}: {status}")

    passed = sum(1 for _, s in results if s)
    total = len(results)

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n✓ 所有测试通过！")
        return 0
    else:
        print(f"\n✗ {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

