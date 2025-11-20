import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 导入网页工具
from tools.webpage_source import get_webpage_source
from tools.webpage_chunker import chunk_webpage
from tools.webpage_screenshot import capture_webpage_screenshot

load_dotenv()

# 使用中转节点
model = ChatOpenAI(
    model="claude-sonnet-4-5-20250929",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="http://35.220.164.252:3888/v1"
)

# 绑定网页工具到模型
webpage_tools = [get_webpage_source, chunk_webpage, capture_webpage_screenshot]
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

    # 工具2：网页分块
    print("\n【工具 2：网页内容分块】")
    print("调用: chunk_webpage.invoke(...)")
    try:
        result2 = chunk_webpage.invoke({
            "url": test_url,
            "chunk_size": 300,
            "method": "paragraph"
        })
        if isinstance(result2, list) and not result2[0].startswith("网页分块失败"):
            print(f"✅ 成功分块")
            print(f"   总块数: {len(result2)}")
            print(f"   第一块预览 ({len(result2[0])} 字符):")
            print(f"   {result2[0][:200]}...")
        else:
            print(f"❌ {result2}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    print("\n" + "-"*70)

    # 工具3：网页截图
    print("\n【工具 3：网页截图】")
    print("调用: capture_webpage_screenshot.invoke(...)")
    try:
        result3 = capture_webpage_screenshot.invoke({
            "url": test_url,
            "save_path": "./example_demo_screenshot.png",
            "full_page": True
        })
        print(f"✅ {result3}")
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
# 运行所有练习
# ============================================================================
def main():
    """运行所有练习"""
    try:
        # exercise_7_webpage_tools()
        #
        # input("\n按 Enter 继续下一个练习...")
        exercise_8_ai_with_webpage_tools()

        print("\n" + "="*70)
        print(" 🎉 所有练习完成！")
        print("="*70)
        print("\n你已经掌握了 invoke 方法的核心用法：")
        print("  ✅ 三种输入格式")
        print("  ✅ 系统提示的作用")
        print("  ✅ 多轮对话的实现")
        print("  ✅ 对话历史的管理")
        print("  ✅ 返回值的解析")
        print("  ✅ Token 使用统计")
        print("  ✅ 网页工具的使用 (DrissionPage)")
        print("  ✅ AI + 工具的集成")
        print("\n建议：")
        print("  1. 重新运行这个文件，仔细观察每个输出")
        print("  2. 修改代码，尝试不同的系统提示")
        print("  3. 尝试修改网页工具的参数")
        print("  4. 阅读 README.md 的详细文档")
        print("  5. 继续学习下一个模块：02_prompt_templates")

    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n运行出错：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
