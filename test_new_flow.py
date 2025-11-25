#!/usr/bin/env python
"""
测试脚本 - 验证新的迭代流程
"""
import sys
from loguru import logger
from agent import ParserAgent

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="DEBUG"
)

def test_iteration_flow():
    """测试迭代流程"""

    # 测试URL（可根据需要修改）
    test_urls = [
        "https://example.com",
        "https://example.org",
    ]

    logger.info("开始测试新的迭代流程...")
    logger.info(f"测试URL数: {len(test_urls)}")

    # 创建Agent
    agent = ParserAgent(output_dir="test_output")

    # 运行迭代
    result = agent.run_iterations(
        urls=test_urls,
        domain="example.com",
        layout_type="test_page",
        max_iterations=2,
        accuracy_threshold=0.8
    )

    # 输出结果
    logger.info("\n测试结果:")
    logger.info(f"  Success: {result['success']}")
    logger.info(f"  Total Rounds: {result['total_rounds']}")
    logger.info(f"  Final Parser Path: {result['final_parser_path']}")
    logger.info(f"  Overall Accuracy: {result['overall_accuracy']:.2%}")

    if result['history']:
        for i, metadata in enumerate(result['history'], 1):
            logger.info(f"\n  Round {i}:")
            logger.info(f"    URLs: {len(metadata['round_urls'])}")
            logger.info(f"    Schema Path: {metadata['schema_path']}")
            logger.info(f"    Parser Path: {metadata['parser_path']}")
            logger.info(f"    Accuracy: {metadata['overall_accuracy']:.2%}")

if __name__ == "__main__":
    test_iteration_flow()

