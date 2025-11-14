"""
使用示例：单个URL处理
"""
from workflows.parser_builder_workflow import ParserBuilderWorkflow
from config.settings import Settings

# 初始化
settings = Settings()
workflow = ParserBuilderWorkflow(settings)

# 处理单个URL
result = workflow.run(
    url="https://example.com/article",
    output_dir="./outputs/example"
)

print(f"解析器已生成: {result['parser_path']}")
print(f"成功率: {result['success_rate']:.2%}")

# 使用生成的解析器
import importlib.util
spec = importlib.util.spec_from_file_location("parser", result['parser_path'])
parser_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser_module)

parser = parser_module.WebPageParser()

# 测试解析
test_html = """
<html>
<body>
    <h1>Test Article</h1>
    <div class="content">Article content...</div>
</body>
</html>
"""

parsed = parser.parse(test_html)
print(f"解析结果: {parsed}")

