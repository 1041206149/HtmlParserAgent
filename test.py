import os

import pytest
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from tools.code_generator import generate_code_from_html
from tools.visual_understanding import extract_json_from_image
from tools.webpage_screenshot import capture_webpage_screenshot
# 导入网页工具
from tools.webpage_source import get_webpage_source

load_dotenv()


@pytest.fixture(scope="session")
def model():
    """创建 ChatOpenAI 模型实例"""
    return ChatOpenAI(
        model="claude-sonnet-4-5-20250929",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="http://35.220.164.252:3888/v1"
    )


@pytest.fixture
def model_with_tools(model):
    """绑定网页工具到模型"""
    webpage_tools = [
        get_webpage_source,
        capture_webpage_screenshot,
        generate_code_from_html,
        extract_json_from_image
    ]
    return model.bind_tools(webpage_tools)


@pytest.fixture
def test_url():
    """测试 URL"""
    return "https://stackoverflow.blog/2025/10/15/secure-coding-in-javascript/"


@pytest.mark.exercise7
def test_webpage_tools_get_source(test_url):
    """练习 7：获取网页源码"""
    print("\n【工具 1：获取网页源码】")
    print(f"调用: get_webpage_source.invoke(...)\n")

    try:
        result = get_webpage_source.invoke({"url": test_url, "wait_time": 2})
        assert not result.startswith("获取网页源码失败"), f"获取源码失败: {result}"
        assert len(result) > 0, "源码为空"
        print(f"✅ 成功获取源码")
        print(f"   源码长度: {len(result)} 字符")
        print(f"   源码预览: {result[:150]}...")
    except Exception as e:
        pytest.fail(f"❌ 错误: {e}")


@pytest.mark.exercise7
def test_webpage_screenshot(test_url, tmp_path):
    """练习 7：网页截图"""
    print("\n【工具 2：网页截图】")
    print(f"调用: capture_webpage_screenshot.invoke(...)\n")

    screenshot_path = tmp_path / "test_screenshot.png"

    try:
        result = capture_webpage_screenshot.invoke({
            "url": test_url,
            "save_path": str(screenshot_path),
            "full_page": True
        })
        print(f"✅ {result}")
        assert screenshot_path.exists() or "成功" in result or "成功" in str(result)
    except Exception as e:
        pytest.fail(f"❌ 错误: {e}")


@pytest.mark.exercise8
def test_ai_with_webpage_tools(model_with_tools):
    """练习 8：AI + 网页工具交互"""
    print("\n【AI + 网页工具交互】\n")

    query = "我想了解 https://stackoverflow.blog/2025/10/15/secure-coding-in-javascript/ 这个网站的内容，请帮我获取它的源码并告诉我大致长度，并给出网页的截图"

    print(f"用户查询: {query}\n")
    print("AI思考中...\n")

    try:
        response = model_with_tools.invoke(query)

        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"✅ AI决定调用 {len(response.tool_calls)} 个工具:")
            for i, tool_call in enumerate(response.tool_calls, 1):
                print(f"   {i}. 工具名称: {tool_call['name']}")
                print(f"      参数: {tool_call['args']}")
            assert len(response.tool_calls) > 0, "AI 没有调用任何工具"
        else:
            print(f"AI回复: {response.content}")
    except Exception as e:
        pytest.fail(f"❌ 错误: {e}")


@pytest.mark.exercise9
def test_visual_understanding(test_url, tmp_path):
    """练习 9：视觉理解工具演示"""
    print("\n【视觉理解工具演示】\n")

    screenshot_path = tmp_path / "visual_test_screenshot.png"

    # 第一步：获取截图
    print("【第一步：获取网页截图】")
    try:
        result = capture_webpage_screenshot.invoke({
            "url": test_url,
            "save_path": str(screenshot_path),
            "full_page": False
        })
        print(f"✅ {result}\n")
    except Exception as e:
        pytest.skip(f"无法获取截图: {e}")

    # 第二步：提取 JSON
    print("【第二步：从截图中提取结构化信息】")
    try:
        result = extract_json_from_image.invoke({
            "image_path": str(screenshot_path),
            "model": "gpt-4o-mini"
        })
        print(f"✅ 成功提取信息")
        assert isinstance(result, dict), "返回结果应为字典"
        print(f"\n提取的结构化数据: {result}")
    except Exception as e:
        pytest.fail(f"❌ 错误: {e}")


@pytest.mark.exercise10
def test_code_generation(test_url, tmp_path):
    """练习 10：代码生成工具演示"""
    print("\n【代码生成工具演示】\n")

    # 第一步：获取 HTML 源码
    print("【第一步：获取网页源码】")
    try:
        html_content = get_webpage_source.invoke({
            "url": test_url,
            "wait_time": 2
        })
        assert not html_content.startswith("获取网页源码失败"), "获取源码失败"
        print(f"✅ 成功获取源码")
        print(f"   源码长度: {len(html_content)} 字符\n")
    except Exception as e:
        pytest.skip(f"无法获取源码: {e}")

    # 第二步：定义目标 JSON
    print("【第二步：定义目标JSON结构】")
    target_json = {
        "title": {"type": "string", "description": "文章标题"},
        "author": {"type": "string", "description": "文章作者"},
        "publish_date": {"type": "string", "description": "发布日期"},
        "content": {"type": "string", "description": "文章正文内容"},
        "tags": {"type": "array", "description": "文章标签"}
    }
    print(f"✅ 目标结构定义完成\n")

    # 第三步：生成解析器
    print("【第三步：生成解析器代码】")
    try:
        from config.settings import Settings
        settings = Settings()

        output_dir = str(tmp_path / "generated_parsers")
        os.makedirs(output_dir, exist_ok=True)

        result = generate_code_from_html.invoke({
            "html_content": html_content,
            "target_json": target_json,
            "output_dir": output_dir,
            "settings": settings
        })

        assert "error" not in result, f"生成失败: {result.get('error')}"
        print(f"✅ 成功生成解析器")
        print(f"   代码路径: {result['parser_path']}")
        print(f"   配置路径: {result['config_path']}")
    except Exception as e:
        pytest.fail(f"❌ 错误: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
