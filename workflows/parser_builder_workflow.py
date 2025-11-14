"""
解析器生成工作流
"""
from typing import List, Dict
from pathlib import Path
from loguru import logger

from agents import (
    HtmlPreprocessor,
    VisualUnderstandingAgent,
    CodeGeneratorAgent,
    ValidationOrchestrator
)
from config.settings import Settings


class ParserBuilderWorkflow:
    """解析器构建工作流

    编排整个流程：
    Stage 1: HTML预处理
    Stage 2: 视觉理解
    Stage 3: 代码生成
    Stage 4: 验证与迭代
    """

    def __init__(self, settings: Settings = None):
        """初始化工作流

        Args:
            settings: 配置对象（可选）
        """
        self.settings = settings or Settings()

        # 初始化各个Agent
        self.preprocessor = HtmlPreprocessor(self.settings)
        self.visual_agent = VisualUnderstandingAgent(self.settings)
        self.code_generator = CodeGeneratorAgent(self.settings)
        self.validator = ValidationOrchestrator(self.settings)

        logger.info("解析器构建工作流初始化完成")

    def run(self, url: str, output_dir: str) -> Dict:
        """运行单次流程

        Args:
            url: 目标URL
            output_dir: 输出目录

        Returns:
            结果字典
        """
        logger.info("="*60)
        logger.info(f"开始处理 URL: {url}")
        logger.info("="*60)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            # Stage 1: HTML预处理
            logger.info("\n[Stage 1/4] HTML预处理...")
            preprocess_result = self.preprocessor.process(
                url=url,
                output_dir=str(output_path / "stage1_preprocess")
            )

            # Stage 2: 视觉理解
            logger.info("\n[Stage 2/4] 视觉理解...")
            vision_result = self.visual_agent.process(
                url=url,
                output_dir=str(output_path / "stage2_vision")
            )

            target_json = vision_result['result']

            # Stage 3: 代码生成
            logger.info("\n[Stage 3/4] 代码生成...")
            code_result = self.code_generator.process(
                html_content=preprocess_result['cleaned_html'],
                target_json=target_json,
                output_dir=str(output_path / "stage3_codegen")
            )

            # Stage 4: 基础验证（单个URL）
            logger.info("\n[Stage 4/4] 基础验证...")
            validation_result = self.validator.validate(
                parser_path=code_result['parser_path'],
                test_urls=[url],
                expected_structure=target_json
            )

            # 汇总结果
            result = {
                'url': url,
                'output_dir': output_dir,
                'parser_path': code_result['parser_path'],
                'config_path': code_result['config_path'],
                'target_structure': target_json,
                'validation': validation_result,
                'success_rate': validation_result['success_rate']
            }

            logger.info("\n" + "="*60)
            logger.info("单次流程完成!")
            logger.info(f"解析器: {result['parser_path']}")
            logger.info(f"成功率: {result['success_rate']:.2%}")
            logger.info("="*60)

            return result

        except Exception as e:
            logger.exception(f"流程执行失败: {e}")
            raise

    def run_iterative(self, urls: List[str], output_dir: str) -> Dict:
        """运行迭代优化流程

        Args:
            urls: URL列表（至少3个）
            output_dir: 输出目录

        Returns:
            结果字典
        """
        if len(urls) < self.settings.min_sample_size:
            logger.warning(
                f"URL数量({len(urls)})少于最小样本数({self.settings.min_sample_size})，"
                "迭代优化效果可能不佳"
            )

        logger.info("="*60)
        logger.info(f"开始迭代优化流程，URL数量: {len(urls)}")
        logger.info("="*60)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            # 使用第一个URL进行初始分析
            primary_url = urls[0]
            logger.info(f"\n使用主URL进行初始分析: {primary_url}")

            # Stage 1: HTML预处理
            logger.info("\n[Stage 1/4] HTML预处理...")
            preprocess_result = self.preprocessor.process(
                url=primary_url,
                output_dir=str(output_path / "stage1_preprocess")
            )

            # Stage 2: 视觉理解
            logger.info("\n[Stage 2/4] 视觉理解...")
            vision_result = self.visual_agent.process(
                url=primary_url,
                output_dir=str(output_path / "stage2_vision")
            )

            target_json = vision_result['result']

            # Stage 3 & 4: 迭代优化
            logger.info("\n[Stage 3-4/4] 代码生成 + 迭代优化...")
            iteration_result = self.validator.iterate(
                html_content=preprocess_result['cleaned_html'],
                target_json=target_json,
                test_urls=urls,
                output_dir=str(output_path / "stage3_4_iterate")
            )

            # 汇总结果
            result = {
                'urls': urls,
                'output_dir': output_dir,
                'parser_path': iteration_result['best_parser'],
                'target_structure': target_json,
                'iterations': iteration_result['iterations'],
                'success_rate': iteration_result['best_score'],
                'report_path': str(output_path / "stage3_4_iterate" / "final_report.json")
            }

            logger.info("\n" + "="*60)
            logger.info("迭代优化流程完成!")
            logger.info(f"迭代次数: {result['iterations']}")
            logger.info(f"最佳解析器: {result['parser_path']}")
            logger.info(f"最终成功率: {result['success_rate']:.2%}")
            logger.info("="*60)

            return result

        except Exception as e:
            logger.exception(f"迭代流程执行失败: {e}")
            raise

