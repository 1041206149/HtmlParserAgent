"""
快速测试脚本 - 验证LLM客户端
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.llm_client import LLMClient
from config.settings import Settings
from loguru import logger

def test_llm_client():
    """测试LLM客户端"""
    try:
        logger.info("测试LLM客户端初始化...")
        settings = Settings()

        logger.info(f"API Key: {settings.openai_api_key[:20]}...")
        logger.info(f"API Base: {settings.openai_api_base}")
        logger.info(f"Model: {settings.openai_model}")

        client = LLMClient(
            api_key=settings.openai_api_key,
            api_base=settings.openai_api_base,
            model=settings.openai_model,
            temperature=settings.openai_temperature
        )

        logger.success("✓ LLM客户端初始化成功！")

        # 测试简单的聊天
        logger.info("测试简单的聊天...")
        messages = [
            {"role": "user", "content": "请用一句话回答：什么是HTML？"}
        ]

        response = client.chat_completion(messages=messages, max_tokens=100)
        logger.success(f"✓ API调用成功！响应: {response[:100]}...")

        return True

    except Exception as e:
        logger.error(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_llm_client()
    sys.exit(0 if success else 1)

