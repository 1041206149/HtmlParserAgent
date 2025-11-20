"""
测试项目设置是否正确
"""
import sys
from pathlib import Path


def test_imports():
    """测试所有模块是否可以正常导入"""
    print("测试模块导入...")
    
    try:
        # 测试配置
        from config.settings import settings
        print("✓ 配置模块导入成功")
        print(f"  - Agent模型: {settings.agent_model}")
        print(f"  - 代码生成模型: {settings.code_gen_model}")
        print(f"  - 视觉模型: {settings.vision_model}")
        
        # 测试工具
        from tools import (
            get_webpage_source,
            capture_webpage_screenshot,
            extract_json_from_image,
            generate_parser_code
        )
        print("✓ 工具模块导入成功")
        
        # 测试Agent
        from agent import (
            AgentPlanner,
            AgentExecutor,
            AgentValidator,
            ParserAgent
        )
        print("✓ Agent模块导入成功")
        
        # 测试LLM客户端
        from utils.llm_client import LLMClient
        print("✓ LLM客户端导入成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """测试配置是否正确"""
    print("\n测试配置...")
    
    try:
        from config.settings import settings
        
        # 检查必要的配置
        assert settings.openai_api_key, "API Key未配置"
        assert settings.openai_api_base, "API Base URL未配置"
        
        print("✓ 配置检查通过")
        print(f"  - API Base: {settings.openai_api_base}")
        print(f"  - 最大迭代次数: {settings.max_iterations}")
        print(f"  - 成功阈值: {settings.success_threshold}")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置检查失败: {str(e)}")
        return False


def test_directories():
    """测试目录结构"""
    print("\n测试目录结构...")
    
    required_dirs = [
        "agent",
        "tools",
        "utils",
        "config",
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✓ {dir_name}/ 存在")
        else:
            print(f"✗ {dir_name}/ 不存在")
            all_exist = False
    
    return all_exist


def test_agent_creation():
    """测试Agent创建"""
    print("\n测试Agent创建...")
    
    try:
        from agent import ParserAgent
        
        agent = ParserAgent(output_dir="test_output")
        print("✓ Agent创建成功")
        print(f"  - 输出目录: {agent.output_dir}")
        
        return True
        
    except Exception as e:
        print(f"✗ Agent创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("="*70)
    print("HtmlParserAgent 设置测试")
    print("="*70)
    
    tests = [
        ("模块导入", test_imports),
        ("配置检查", test_config),
        ("目录结构", test_directories),
        ("Agent创建", test_agent_creation),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    # 总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过! 项目设置正确。")
        print("\n下一步:")
        print("  1. 运行示例: python example.py")
        print("  2. 运行主程序: python main.py")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main())

