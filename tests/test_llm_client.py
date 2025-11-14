"""
LLM客户端测试
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.llm_client import LLMClient
from config.settings import Settings
from loguru import logger


def test_llm_client_initialization():
    """测试LLM客户端初始化"""
    try:
        logger.info("测试LLM客户端初始化...")
        settings = Settings()

        client = LLMClient.from_settings(settings)

        logger.success("✓ LLM客户端初始化成功！")
        return True

    except Exception as e:
        logger.error(f"✗ 初始化失败: {e}")
        return False


def test_llm_chat_completion():
    """测试LLM聊天功能"""
    try:
        logger.info("测试LLM聊天功能...")
        settings = Settings()

        client = LLMClient.from_settings(settings)

        messages = [
            {"role": "user", "content": "请用一句话回答：什么是HTML？"}
        ]

        response = client.chat_completion(messages=messages, max_tokens=100)

        assert response, "响应不能为空"
        assert len(response) > 0, "响应长度必须大于0"

        logger.success(f"✓ API调用成功！响应: {response[:100]}...")
        return True

    except Exception as e:
        logger.error(f"✗ 聊天测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vision_model_config():
    """测试视觉模型配置"""
    try:
        logger.info("测试视觉模型配置...")
        settings = Settings()

        logger.info(f"默认模型: {settings.openai_model}")
        logger.info(f"视觉模型: {settings.vision_model}")

        assert settings.vision_model, "视觉模型配置不能为空"

        logger.success("✓ 视觉模型配置正确！")
        return True

    except Exception as e:
        logger.error(f"✗ 配置测试失败: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("LLM客户端测试套件")
    print("="*60)

    tests = [
        ("初始化测试", test_llm_client_initialization),
        ("视觉模型配置测试", test_vision_model_config),
        ("聊天功能测试", test_llm_chat_completion),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n运行: {name}")
        print("-"*60)
        result = test_func()
        results.append((name, result))

    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n✓ 所有测试通过！")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} 个测试失败")
        sys.exit(1)

