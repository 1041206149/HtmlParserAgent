"""
主入口文件
"""
import argparse
import sys
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

from workflows.parser_builder_workflow import ParserBuilderWorkflow
from config.settings import Settings


def setup_logger(log_level: str = "INFO"):
    """配置日志"""
    logger.remove()
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    )
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="HtmlParserAgent - 智能HTML解析器生成工具")

    parser.add_argument(
        "--url",
        type=str,
        help="单个URL地址"
    )

    parser.add_argument(
        "--urls",
        type=str,
        help="包含多个URL的文本文件路径（每行一个URL）"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="./outputs/default",
        help="输出目录路径"
    )

    parser.add_argument(
        "--iterate",
        action="store_true",
        help="是否启用多样本迭代优化"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="日志级别"
    )

    parser.add_argument(
        "--config",
        type=str,
        help="自定义配置文件路径"
    )

    args = parser.parse_args()

    # 加载环境变量
    load_dotenv()

    # 配置日志
    setup_logger(args.log_level)

    # 加载配置
    settings = Settings(config_file=args.config) if args.config else Settings()

    logger.info("HtmlParserAgent 启动")
    logger.info(f"输出目录: {args.output}")

    try:
        # 初始化工作流
        workflow = ParserBuilderWorkflow(settings=settings)

        # 准备URL列表
        urls = []
        if args.url:
            urls = [args.url]
        elif args.urls:
            urls_file = Path(args.urls)
            if not urls_file.exists():
                logger.error(f"URL文件不存在: {args.urls}")
                return 1
            with open(urls_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        else:
            logger.error("请提供 --url 或 --urls 参数")
            parser.print_help()
            return 1

        logger.info(f"待处理URL数量: {len(urls)}")

        # 执行工作流
        if args.iterate and len(urls) > 1:
            logger.info("启用迭代优化模式")
            result = workflow.run_iterative(
                urls=urls,
                output_dir=args.output
            )
        else:
            logger.info("单次运行模式")
            result = workflow.run(
                url=urls[0],
                output_dir=args.output
            )

        # 输出结果
        logger.info("=" * 60)
        logger.info("处理完成!")
        logger.info(f"解析器文件: {result.get('parser_path', 'N/A')}")
        logger.info(f"配置文件: {result.get('config_path', 'N/A')}")
        logger.info(f"测试报告: {result.get('report_path', 'N/A')}")
        logger.info(f"成功率: {result.get('success_rate', 0):.2%}")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.exception(f"执行失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

