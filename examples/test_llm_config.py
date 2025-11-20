"""
测试 LLM 配置的示例脚本
演示如何使用不同场景的 LLM 客户端
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv(project_root / ".env")

from utils.llm_client import LLMClient
from config.settings import Settings


def test_scenario_based_clients():
    """测试基于场景的客户端创建"""
    print("=" * 70)
    print("测试场景化 LLM 客户端")
    print("=" * 70)
    
    scenarios = ["default", "code_gen", "vision", "agent"]
    
    for scenario in scenarios:
        print(f"\n📌 场景: {scenario}")
        llm = LLMClient.for_scenario(scenario)
        print(f"   模型: {llm.model}")
        print(f"   温度: {llm.temperature}")
        print(f"   Base URL: {llm.api_base}")


def test_direct_initialization():
    """测试直接初始化"""
    print("\n" + "=" * 70)
    print("测试直接初始化")
    print("=" * 70)
    
    # 使用默认配置
    llm1 = LLMClient()
    print(f"\n默认配置:")
    print(f"   模型: {llm1.model}")
    print(f"   温度: {llm1.temperature}")
    
    # 指定模型
    llm2 = LLMClient(model="gpt-4-turbo-preview", temperature=0.7)
    print(f"\n自定义配置:")
    print(f"   模型: {llm2.model}")
    print(f"   温度: {llm2.temperature}")


def test_settings_based():
    """测试从 Settings 创建"""
    print("\n" + "=" * 70)
    print("测试从 Settings 创建")
    print("=" * 70)
    
    settings = Settings()
    llm = LLMClient.from_settings(settings)
    print(f"\n从 Settings 创建:")
    print(f"   模型: {llm.model}")
    print(f"   温度: {llm.temperature}")
    
    # 覆盖模型
    llm2 = LLMClient.from_settings(settings, model="custom-model")
    print(f"\n覆盖模型:")
    print(f"   模型: {llm2.model}")


def test_chat_completion():
    """测试聊天完成（可选，需要有效的 API Key）"""
    print("\n" + "=" * 70)
    print("测试聊天完成 API 调用")
    print("=" * 70)
    
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_api_key_here":
        print("\n⚠️  跳过 API 调用测试（未配置有效的 API Key）")
        return
    
    try:
        llm = LLMClient.for_scenario("default")
        print(f"\n使用模型: {llm.model}")
        print("发送测试消息...")
        
        response = llm.chat_completion(
            messages=[
                {"role": "user", "content": "Say 'Hello, World!' in one word."}
            ],
            max_tokens=10
        )
        
        print(f"✅ 响应: {response}")
        
    except Exception as e:
        print(f"❌ API 调用失败: {e}")


def show_current_config():
    """显示当前配置"""
    print("\n" + "=" * 70)
    print("当前环境配置")
    print("=" * 70)
    
    config_keys = [
        "OPENAI_API_KEY",
        "OPENAI_API_BASE",
        "DEFAULT_MODEL",
        "CODE_GEN_MODEL",
        "VISION_MODEL",
        "AGENT_MODEL",
    ]
    
    for key in config_keys:
        value = os.getenv(key, "未设置")
        # 隐藏 API Key
        if "KEY" in key and value != "未设置":
            value = value[:10] + "..." + value[-4:] if len(value) > 14 else "***"
        print(f"   {key}: {value}")


if __name__ == "__main__":
    print("\n🚀 LLM 配置测试脚本\n")
    
    # 显示当前配置
    show_current_config()
    
    # 测试不同的创建方式
    test_scenario_based_clients()
    test_direct_initialization()
    test_settings_based()
    
    # 可选：测试实际 API 调用
    test_chat_completion()
    
    print("\n" + "=" * 70)
    print("✅ 测试完成")
    print("=" * 70)
    print("\n💡 提示:")
    print("   - 修改 .env 文件中的模型配置")
    print("   - 重新运行此脚本查看变化")
    print("   - 查看 docs/LLM_CONFIG_GUIDE.md 了解更多")
    print()

