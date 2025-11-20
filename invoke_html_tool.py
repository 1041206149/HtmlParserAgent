import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 导入网页工具
from tools.webpage_source import get_webpage_source
from tools.webpage_screenshot import capture_webpage_screenshot
from tools.code_generator import generate_code_from_html
from tools.visual_understanding import extract_json_from_image

load_dotenv()

# 使用中转节点
model = ChatOpenAI(
    model="claude-sonnet-4-5-20250929",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="http://35.220.164.252:3888/v1"
)

# 绑定网页工具到模型
webpage_tools = [get_webpage_source, capture_webpage_screenshot, generate_code_from_html, extract_json_from_image]
model_with_tools = model.bind_tools(webpage_tools)


print("="*70)
print(" invoke 方法深入实践")
print("="*70)

# ============================================================================
# 练习 7：网页工具演示 - DrissionPage
# ============================================================================
def exercise_7_webpage_tools():
    """
    练习目标：演示如何使用网页工具
    - 获取网页源码
    - 网页内容分块
    - 网页截图
    """
    print("\n" + "="*70)
    print("练习 7：网页工具演示")
    print("="*70)

    test_url = "https://stackoverflow.blog/2025/10/15/secure-coding-in-javascript/"

    print(f"\n测试网页: {test_url}\n")

    # 工具1：获取网页源码
    print("【工具 1：获取网页源码】")
    print("调用: get_webpage_source.invoke(...)")
    try:
        result1 = get_webpage_source.invoke({"url": test_url, "wait_time": 2})
        if result1.startswith("获取网页源码失败"):
            print(f"❌ {result1}")
        else:
            print(f"✅ 成功获取源码")
            print(f"   源码长度: {len(result1)} 字符")
            print(f"   源码预览: {result1[:150]}...")
    except Exception as e:
        print(f"❌ 错误: {e}")

    print("\n" + "-"*70)

    # 工具2：网页截图
    print("\n【工具 2：网页截图】")
    print("调用: capture_webpage_screenshot.invoke(...)")
    try:
        result2 = capture_webpage_screenshot.invoke({
            "url": test_url,
            "save_path": "./example_demo_screenshot.png",
            "full_page": True
        })
        print(f"✅ {result2}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    print("\n" + "="*70)
    print("💡 提示：")
    print("   1. 这些工具可以单独使用，也可以组合使用")
    print("   2. 可以将工具绑定到模型，让AI自动调用")
    print("   3. 使用 model_with_tools 可以让AI自主选择工具")
    print("="*70)


# ============================================================================
# 练习 8：AI + 网页工具交互演示
# ============================================================================
def exercise_8_ai_with_webpage_tools():
    """
    练习目标：演示如何让AI使用网页工具
    """
    print("\n" + "="*70)
    print("练习 8：AI + 网页工具交互")
    print("="*70)

    print("\n这个演示展示了AI如何理解并使用网页工具")
    print("我们已经将工具绑定到模型上\n")

    # 示例查询
    query = "我想了解 https://stackoverflow.blog/2025/10/15/secure-coding-in-javascript/ 这个网站的内容，请帮我获取它的源码并告诉我大致长度，并给出网页的截图"

    print(f"用户查询: {query}\n")
    print("AI思考中...")

    try:
        response = model_with_tools.invoke(query)

        # 检查AI是否要调用工具
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"\n✅ AI决定调用 {len(response.tool_calls)} 个工具:")
            for i, tool_call in enumerate(response.tool_calls, 1):
                print(f"   {i}. 工具名称: {tool_call['name']}")
                print(f"      参数: {tool_call['args']}")
        else:
            print(f"\nAI回复: {response.content}")
            print("\n💡 提示: AI没有调用工具，可能需要更明确的指令")

    except Exception as e:
        print(f"❌ 错误: {e}")

    print("\n" + "="*70)
    print("💡 关键点：")
    print("   1. 使用 model.bind_tools(tools) 绑定工具")
    print("   2. AI会根据用户需求自动选择合适的工具")
    print("   3. 查看 response.tool_calls 了解AI的工具调用计划")
    print("="*70)


# ============================================================================
# 练习 9：视觉理解工具演示 - 图片转JSON
# ============================================================================
def exercise_9_visual_understanding():
    """
    练习目标：演示如何使用视觉理解工具
    - 从网页截图中提取结构化信息
    - 识别页面字段并生成JSON
    """
    print("\n" + "=" * 70)
    print("练习 9：视觉理解工具演示")
    print("=" * 70)

    test_url = "https://stackoverflow.blog/2025/10/15/secure-coding-in-javascript/"
    screenshot_path = "./example_demo_screenshot.png"

    print(f"\n测试网页: {test_url}\n")

    # 先获取截图
    print("【第一步：获取网页截图】")
    print("调用: capture_webpage_screenshot.invoke(...)")
    try:
        result = capture_webpage_screenshot.invoke({
            "url": test_url,
            "save_path": screenshot_path,
            "full_page": False
        })
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ 错误: {e}")
        return

    print("\n" + "-" * 70)

    # 使用视觉理解工具提取JSON
    print("\n【第二步：从截图中提取结构化信息】")
    print("调用: extract_json_from_image.invoke(...)")
    try:
        result = extract_json_from_image.invoke({
            "image_path": screenshot_path,
            "model": "gpt-4o-mini"
        })
        print(f"✅ 成功提取信息")
        print(f"\n提取的结构化数据:")
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"❌ 错误: {e}")

    print("\n" + "=" * 70)
    print("💡 提示：")
    print("   1. 视觉理解工具可以识别页面类型和关键字段")
    print("   2. 返回的JSON包含字段类型、描述、值和置信度")
    print("   3. 可用于快速理解陌生网页的结构")
    print("=" * 70)


# ============================================================================
# 练习 10：代码生成工具演示 - HTML转解析器
# ============================================================================
def exercise_10_code_generation():
    """
    练习目标：演示如何使用代码生成工具
    - 从HTML源码和目标JSON生成解析器代码
    - 自动生成BeautifulSoup解析逻辑
    """
    print("\n" + "=" * 70)
    print("练习 10：代码生成工具演示")
    print("=" * 70)

    test_url = "https://stackoverflow.blog/2025/10/15/secure-coding-in-javascript/"

    print(f"\n测试网页: {test_url}\n")

    # 第一步：获取HTML源码
    print("【第一步：获取网页源码】")
    print("调用: get_webpage_source.invoke(...)")
    try:
        html_content = get_webpage_source.invoke({
            "url": test_url,
            "wait_time": 2
        })
        if html_content.startswith("获取网页源码失败"):
            print(f"❌ {html_content}")
            return
        print(f"✅ 成功获取源码")
        print(f"   源码长度: {len(html_content)} 字符")
    except Exception as e:
        print(f"❌ 错误: {e}")
        return

    print("\n" + "-" * 70)

    # 第二步：定义目标JSON结构
    print("\n【第二步：定义目标JSON结构】")
    target_json = {
        "title": {
            "type": "string",
            "description": "文章标题"
        },
        "author": {
            "type": "string",
            "description": "文章作者"
        },
        "publish_date": {
            "type": "string",
            "description": "发布日期"
        },
        "content": {
            "type": "string",
            "description": "文章正文内容"
        },
        "tags": {
            "type": "array",
            "description": "文章标签"
        }
    }
    import json
    print(json.dumps(target_json, ensure_ascii=False, indent=2))

    print("\n" + "-" * 70)

    # 第三步：调用代码生成工具
    print("\n【第三步：生成解析器代码】")
    print("调用: generate_code_from_html.invoke(...)")
    try:
        from config.settings import Settings
        settings = Settings()

        output_dir = "./generated_parsers"
        result = generate_code_from_html.invoke({
            "html_content": html_content,
            "target_json": target_json,
            "output_dir": output_dir,
            "settings": settings
        })

        if "error" in result:
            print(f"❌ {result['error']}")
        else:
            print(f"✅ 成功生成解析器")
            print(f"   代码路径: {result['parser_path']}")
            print(f"   配置路径: {result['config_path']}")
            print(f"\n【生成的代码片段】")
            code_snippet = result['code'][:500] + "..." if len(result['code']) > 500 else result['code']
            print(code_snippet)
            print(f"\n【生成的配置】")
            print(json.dumps(result['config'], ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("💡 提示：")
    print("   1. 代码生成工具可自动创建网页解析器")
    print("   2. 生成的代码使用BeautifulSoup和lxml")
    print("   3. 同时生成schema.json配置文件")
    print("   4. 生成的代码可直接运行和修改")
    print("=" * 70)


# ============================================================================
# 运行所有练习
# ============================================================================
def main():
    """运行所有练习"""
    try:
        # exercise_7_webpage_tools()
        # input("\n按 Enter 继续下一个练习...")
        # exercise_8_ai_with_webpage_tools()
        # input("\n按 Enter 继续下一个练习...")
        exercise_9_visual_understanding()
        input("\n按 Enter 继续下一个练习...")
        exercise_10_code_generation()

    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n运行出错：{e}")
        import traceback
        traceback.print_exc()



if __name__ == "__main__":
    main()
