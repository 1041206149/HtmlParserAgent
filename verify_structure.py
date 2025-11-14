#!/usr/bin/env python3
"""
项目结构验证脚本
检查所有必要文件是否存在
"""

from pathlib import Path
from typing import List, Tuple

def check_files() -> List[Tuple[str, bool]]:
    """检查必要文件是否存在"""

    base_path = Path(__file__).parent

    required_files = [
        # 核心文件
        "main.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "README.md",
        "USAGE.md",
        "DEVELOPMENT.md",
        "PROJECT_SUMMARY.md",
        "setup.sh",

        # 配置模块
        "config/__init__.py",
        "config/settings.py",

        # Agent模块
        "agents/__init__.py",
        "agents/preprocessor.py",
        "agents/visual_understanding.py",
        "agents/code_generator.py",
        "agents/validator.py",

        # 工具模块
        "utils/__init__.py",
        "utils/llm_client.py",
        "utils/screenshot.py",
        "utils/html_chunker.py",
        "utils/xpath_optimizer.py",

        # 工作流模块
        "workflows/__init__.py",
        "workflows/parser_builder_workflow.py",

        # 模板
        "templates/parser_template.py.jinja2",

        # 测试
        "tests/__init__.py",
        "tests/test_basic.py",

        # 示例
        "examples/example_single_url.py",
        "examples/example_iterative.py",
        "examples/example_urls.txt",

        # 目录标记
        "outputs/.gitkeep",
        "logs/.gitkeep",
    ]

    results = []
    for file_path in required_files:
        full_path = base_path / file_path
        exists = full_path.exists()
        results.append((file_path, exists))

    return results


def main():
    """主函数"""
    print("=" * 60)
    print("HtmlParserAgent 项目结构验证")
    print("=" * 60)
    print()

    results = check_files()

    missing = [f for f, exists in results if not exists]
    existing = [f for f, exists in results if exists]

    print(f"✓ 已存在: {len(existing)} 个文件")
    print(f"✗ 缺失: {len(missing)} 个文件")
    print()

    if missing:
        print("缺失的文件:")
        for file_path in missing:
            print(f"  ✗ {file_path}")
        print()

    # 检查模块导入
    print("检查模块导入...")
    try:
        from config.settings import Settings
        print("  ✓ config.settings")
    except Exception as e:
        print(f"  ✗ config.settings: {e}")

    try:
        from agents import HtmlPreprocessor, VisualUnderstandingAgent, CodeGeneratorAgent, ValidationOrchestrator
        print("  ✓ agents")
    except Exception as e:
        print(f"  ✗ agents: {e}")

    try:
        from utils import LLMClient, ScreenshotTool, HtmlChunker, XPathOptimizer
        print("  ✓ utils")
    except Exception as e:
        print(f"  ✗ utils: {e}")

    try:
        from workflows import ParserBuilderWorkflow
        print("  ✓ workflows")
    except Exception as e:
        print(f"  ✗ workflows: {e}")

    print()

    # 总结
    if missing:
        print("⚠ 项目结构不完整，请检查缺失的文件")
        return 1
    else:
        print("✓ 项目结构完整！")
        print()
        print("下一步:")
        print("1. 配置 .env 文件")
        print("2. 运行 setup.sh 安装依赖")
        print("3. 运行测试: pytest tests/ -v")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

