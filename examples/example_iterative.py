"""
使用示例：多URL迭代优化
"""
from workflows.parser_builder_workflow import ParserBuilderWorkflow
from config.settings import Settings

# 初始化
settings = Settings()
workflow = ParserBuilderWorkflow(settings)

# 多个相同布局的URL
urls = [
    "https://example.com/article1",
    "https://example.com/article2",
    "https://example.com/article3",
    "https://example.com/article4",
    "https://example.com/article5"
]

# 迭代优化处理
result = workflow.run_iterative(
    urls=urls,
    output_dir="./outputs/example_iterative"
)

print(f"迭代次数: {result['iterations']}")
print(f"最佳解析器: {result['parser_path']}")
print(f"最终成功率: {result['success_rate']:.2%}")

# 使用最终的解析器
if result['parser_path']:
    import importlib.util
    spec = importlib.util.spec_from_file_location("parser", result['parser_path'])
    parser_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser_module)

    parser = parser_module.WebPageParser()

    # 在新的URL上测试
    import requests
    test_url = "https://example.com/article6"
    response = requests.get(test_url)

    parsed = parser.parse(response.text)
    print(f"新URL解析结果: {parsed}")

