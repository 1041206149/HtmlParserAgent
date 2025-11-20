"""
HtmlParserAgent 主程序
通过给定URL列表，自动生成网页解析代码
"""
import sys
from pathlib import Path
from loguru import logger
from agent import ParserAgent


def setup_logger():
    """配置日志"""
    logger.remove()  # 移除默认处理器
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/agent_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG"
    )


def main():
    """主函数"""
    setup_logger()
    
    logger.info("="*70)
    logger.info("HtmlParserAgent - 智能网页解析代码生成器")
    logger.info("="*70)
    
    # 示例：解析博客文章
    urls = [
        "https://stackoverflow.blog/2025/10/15/secure-coding-in-javascript/",
        # 可以添加更多同类型的URL
    ]
    
    # 创建Agent
    agent = ParserAgent(output_dir="output")
    
    # 生成解析器
    result = agent.generate_parser(
        urls=urls,
        domain="stackoverflow.blog",
        layout_type="blog_article",
        validate=True  # 是否验证生成的代码
    )
    
    # 输出结果
    if result['success']:
        logger.success("\n✓ 解析器生成成功!")
        logger.info(f"  解析器路径: {result['parser_path']}")
        logger.info(f"  配置路径: {result['config_path']}")
        logger.info("\n使用方法:")
        logger.info(f"  python {result['parser_path']} <url_or_html_file>")
    else:
        logger.error("\n✗ 解析器生成失败")
        if 'error' in result:
            logger.error(f"  错误: {result['error']}")


def example_custom_usage():
    """自定义使用示例"""
    setup_logger()
    
    # 示例1: 解析电商产品页
    urls_ecommerce = [
        "https://example.com/product/123",
        "https://example.com/product/456",
    ]
    
    agent = ParserAgent(output_dir="output/ecommerce")
    result = agent.generate_parser(
        urls=urls_ecommerce,
        layout_type="product_page",
        validate=True
    )
    
    # 示例2: 解析新闻列表页
    urls_news = [
        "https://news.example.com/category/tech",
    ]
    
    agent = ParserAgent(output_dir="output/news")
    result = agent.generate_parser(
        urls=urls_news,
        layout_type="news_list",
        validate=False  # 不验证，直接生成
    )


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 从命令行读取URL
        urls = sys.argv[1:]
        
        setup_logger()
        logger.info(f"从命令行读取 {len(urls)} 个URL")
        
        agent = ParserAgent()
        result = agent.generate_parser(urls=urls, validate=True)
        
        if result['success']:
            print(f"\n✓ 成功! 解析器已保存到: {result['parser_path']}")
        else:
            print(f"\n✗ 失败: {result.get('error', 'Unknown error')}")
    else:
        # 运行默认示例
        main()

