"""
简单的配置检查脚本
不依赖项目代码，直接读取 .env 文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
load_dotenv(env_file)


def show_config():
    """显示当前配置"""
    print("=" * 70)
    print("LLM API 配置检查")
    print("=" * 70)
    
    print(f"\n📁 配置文件: {env_file}")
    print(f"   存在: {'✅' if env_file.exists() else '❌'}")
    
    print("\n" + "=" * 70)
    print("统一 API 配置")
    print("=" * 70)
    
    api_key = os.getenv("OPENAI_API_KEY", "未设置")
    api_base = os.getenv("OPENAI_API_BASE", "未设置")
    
    # 隐藏 API Key
    if api_key != "未设置" and len(api_key) > 14:
        api_key_display = api_key[:10] + "..." + api_key[-4:]
    else:
        api_key_display = "***" if api_key != "未设置" else "未设置"
    
    print(f"\nOPENAI_API_KEY: {api_key_display}")
    print(f"OPENAI_API_BASE: {api_base}")
    
    print("\n" + "=" * 70)
    print("场景化模型配置")
    print("=" * 70)
    
    scenarios = {
        "默认场景 (default)": {
            "model": "DEFAULT_MODEL",
            "temperature": "DEFAULT_TEMPERATURE",
        },
        "代码生成 (code_gen)": {
            "model": "CODE_GEN_MODEL",
            "temperature": "CODE_GEN_TEMPERATURE",
            "max_tokens": "CODE_GEN_MAX_TOKENS",
        },
        "视觉理解 (vision)": {
            "model": "VISION_MODEL",
            "temperature": "VISION_TEMPERATURE",
            "max_tokens": "VISION_MAX_TOKENS",
        },
        "Agent (agent)": {
            "model": "AGENT_MODEL",
            "temperature": "AGENT_TEMPERATURE",
        },
    }
    
    for scenario_name, params in scenarios.items():
        print(f"\n📌 {scenario_name}")
        for param_name, env_key in params.items():
            value = os.getenv(env_key, "未设置")
            print(f"   {param_name}: {value}")
    
    print("\n" + "=" * 70)
    print("其他配置")
    print("=" * 70)
    
    other_configs = [
        "EMBEDDING_MODEL",
        "TOP_K",
        "SIMILARITY_THRESHOLD",
        "VISION_PARALLEL",
        "VISION_MAX_WORKERS",
    ]
    
    for key in other_configs:
        value = os.getenv(key, "未设置")
        print(f"   {key}: {value}")


def validate_config():
    """验证配置"""
    print("\n" + "=" * 70)
    print("配置验证")
    print("=" * 70)
    
    issues = []
    
    # 检查必需配置
    if not os.getenv("OPENAI_API_KEY"):
        issues.append("❌ OPENAI_API_KEY 未设置")
    else:
        print("✅ OPENAI_API_KEY 已设置")
    
    if not os.getenv("OPENAI_API_BASE"):
        issues.append("⚠️  OPENAI_API_BASE 未设置（将使用默认值）")
    else:
        print("✅ OPENAI_API_BASE 已设置")
    
    # 检查模型配置
    model_keys = ["DEFAULT_MODEL", "CODE_GEN_MODEL", "VISION_MODEL", "AGENT_MODEL"]
    for key in model_keys:
        if not os.getenv(key):
            issues.append(f"⚠️  {key} 未设置（将使用默认值）")
        else:
            print(f"✅ {key} 已设置")
    
    if issues:
        print("\n发现以下问题:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✅ 所有配置正常")


def show_usage_examples():
    """显示使用示例"""
    print("\n" + "=" * 70)
    print("使用示例")
    print("=" * 70)
    
    print("""
# 方式 1: 按场景创建（推荐）
from utils.llm_client import LLMClient

llm = LLMClient.for_scenario("code_gen")
response = llm.chat_completion(messages=[...])

# 方式 2: 直接初始化
llm = LLMClient(model="gpt-4-turbo-preview")

# 方式 3: 从 Settings 创建
from config.settings import Settings
settings = Settings()
llm = LLMClient.from_settings(settings)
""")


if __name__ == "__main__":
    print("\n🚀 LLM 配置检查工具\n")
    
    show_config()
    validate_config()
    show_usage_examples()
    
    print("\n" + "=" * 70)
    print("💡 提示")
    print("=" * 70)
    print("""
1. 如果配置有问题，请编辑 .env 文件
2. 可以参考 .env.example 文件
3. 查看 docs/LLM_CONFIG_GUIDE.md 了解详细说明
4. 修改配置后重新运行此脚本验证
""")

