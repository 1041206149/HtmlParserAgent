"""
多轮迭代流程测试脚本
验证新的执行流程和验证逻辑
"""
import sys
from loguru import logger
from agent.orchestrator import ParserAgent

# 配置日志
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="DEBUG"
)

def test_multirounds_execution():
    """测试多轮迭代执行"""
    logger.info("="*70)
    logger.info("测试多轮迭代执行流程")
    logger.info("="*70)

    # 示例URL列表（实际使用时需要替换为真实的URL）
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
    ]

    # 创建Agent
    agent = ParserAgent(output_dir="output")

    # 生成解析器（包含多轮执行和groundtruth验证）
    result = agent.generate_parser(
        urls=urls,
        domain="example.com",
        validate=True
    )

    # 打印结果
    logger.info("\n" + "="*70)
    logger.info("生成结果")
    logger.info("="*70)
    logger.info(f"成功: {result['success']}")
    if result['success']:
        logger.info(f"解析器路径: {result['parser_path']}")
        logger.info(f"配置路径: {result['config_path']}")

        if result['validation_result']:
            logger.info(f"\n验证结果:")
            logger.info(f"  平均准确率: {result['validation_result']['success_rate']:.1%}")
            logger.info(f"  验证通过: {result['validation_result']['passed']}")
            logger.info(f"  准确率详情: {result['validation_result']['accuracy_details']}")
    else:
        logger.error(f"生成失败: {result.get('error')}")

    return result

def test_schema_merging():
    """测试Schema增量合并"""
    logger.info("="*70)
    logger.info("测试Schema增量合并")
    logger.info("="*70)

    from agent.executor import AgentExecutor

    executor = AgentExecutor()

    # 测试数据
    old_schema = {
        "title": {"type": "string", "description": "页面标题"},
        "author": {"type": "string", "description": "作者"},
    }

    new_schema = {
        "title": {"type": "string", "description": "页面标题"},
        "date": {"type": "string", "description": "发布日期"},
        "tags": {"type": "array", "description": "标签列表"},
    }

    logger.info(f"旧 Schema: {list(old_schema.keys())}")
    logger.info(f"新 Schema: {list(new_schema.keys())}")

    merged = executor._merge_schemas_incremental(old_schema, new_schema)

    logger.info(f"合并后 Schema: {list(merged.keys())}")
    logger.success(f"合并完成，共 {len(merged)} 个字段")

    return merged

def test_groundtruth_validation():
    """测试Groundtruth对比验证"""
    logger.info("="*70)
    logger.info("测试Groundtruth对比验证")
    logger.info("="*70)

    from agent.validator import AgentValidator

    validator = AgentValidator()

    # 创建模拟的解析器类
    class MockParser:
        def parse(self, html):
            # 模拟解析结果
            return {
                "title": "Test Title",
                "author": "John Doe",
                "date": "2025-11-25"
            }

    # Groundtruth Schema（从图片识别得到）
    groundtruth_schema = {
        "title": {"type": "string"},
        "author": {"type": "string"},
        "date": {"type": "string"},
        "tags": {"type": "array"},  # 解析器未捕获
    }

    html = "<html><body>Test</body></html>"
    parser = MockParser()

    result = validator._compare_with_groundtruth(
        parser,
        html,
        groundtruth_schema,
        round_num=1
    )

    logger.info(f"\n对比结果:")
    logger.info(f"  准确率: {result['accuracy']:.1%}")
    logger.info(f"  匹配字段: {result['matched_fields']}")
    logger.info(f"  缺失字段: {result['missing_fields']}")
    logger.info(f"  额外字段: {result['extra_fields']}")
    logger.success(f"验证完成")

    return result

if __name__ == "__main__":
    logger.info("开始运行多轮迭代流程测试\n")

    try:
        # 测试1: Schema合并
        test_schema_merging()

        # 测试2: Groundtruth验证
        test_groundtruth_validation()

        # 测试3: 完整的多轮执行流程（需要真实URL）
        # test_multirounds_execution()

        logger.success("\n所有测试完成！")
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)

