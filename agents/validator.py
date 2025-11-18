"""
验证与迭代编排器 Agent
"""
import importlib.util
import json
from pathlib import Path
from typing import Dict, List

from loguru import logger

from agents.code_generator import CodeGeneratorAgent
from agents.preprocessor import HtmlPreprocessor
from config.settings import Settings


class ValidationOrchestrator:
    """验证与迭代编排器

    负责：
    1. 在多个样本上测试生成的解析器
    2. 收集失败案例
    3. 计算评估指标
    4. 触发代码优化迭代
    """

    def __init__(self, settings: Settings):
        """初始化验证编排器

        Args:
            settings: 配置对象
        """
        self.settings = settings
        self.preprocessor = HtmlPreprocessor(settings)
        self.code_generator = CodeGeneratorAgent(settings)

        logger.info("验证编排器初始化完成")

    def validate(
        self,
        parser_path: str,
        test_urls: List[str],
        expected_structure: Dict
    ) -> Dict:
        """验证解析器

        Args:
            parser_path: 解析器文件路径
            test_urls: 测试URL列表
            expected_structure: 期望的结构

        Returns:
            验证报告
        """
        logger.info(f"开始验证解析器，测试URL数: {len(test_urls)}")

        # 动态加载解析器
        parser = self._load_parser(parser_path)

        results = []
        failed_cases = []

        for i, url in enumerate(test_urls):
            logger.info(f"测试 {i+1}/{len(test_urls)}: {url}")

            try:
                # 获取HTML
                html = self.preprocessor.fetch_html(url)

                # 调用解析器
                parsed_data = parser.parse(html)

                # 评估结果
                score = self._evaluate_result(parsed_data, expected_structure)

                result = {
                    'url': url,
                    'success': score['total_score'] >= 0.7,
                    'score': score['total_score'],
                    'field_scores': score['field_scores'],
                    'parsed_data': parsed_data
                }

                results.append(result)

                if not result['success']:
                    failed_cases.append({
                        'url': url,
                        'expected': expected_structure,
                        'actual': parsed_data,
                        'issues': score['issues']
                    })

            except Exception as e:
                logger.error(f"测试失败 {url}: {e}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e)
                })
                failed_cases.append({
                    'url': url,
                    'error': str(e)
                })

        # 计算统计
        success_count = sum(1 for r in results if r.get('success', False))
        success_rate = success_count / len(results) if results else 0

        report = {
            'total': len(results),
            'success': success_count,
            'failed': len(results) - success_count,
            'success_rate': success_rate,
            'results': results,
            'failed_cases': failed_cases
        }

        logger.info(f"验证完成 - 成功率: {success_rate:.2%} ({success_count}/{len(results)})")

        return report

    def iterate(
        self,
        html_content: str,
        target_json: Dict,
        test_urls: List[str],
        output_dir: str,
        max_iterations: int = None
    ) -> Dict:
        """迭代优化解析器

        Args:
            html_content: 初始HTML
            target_json: 目标JSON
            test_urls: 测试URL列表
            output_dir: 输出目录
            max_iterations: 最大迭代次数

        Returns:
            最终结果
        """
        max_iter = max_iterations or self.settings.max_iterations
        threshold = self.settings.success_threshold

        logger.info(f"开始迭代优化 - 最大迭代次数: {max_iter}, 目标成功率: {threshold:.0%}")

        output_path = Path(output_dir)
        failed_cases = []
        best_parser = None
        best_score = 0

        for iteration in range(max_iter):
            logger.info(f"=== 迭代 {iteration + 1}/{max_iter} ===")

            # 生成代码
            result = self.code_generator.process(
                html_content=html_content,
                target_json=target_json,
                output_dir=str(output_path / f"iteration_{iteration}")
            )

            parser_path = result['parser_path']

            # 验证
            report = self.validate(
                parser_path=parser_path,
                test_urls=test_urls,
                expected_structure=target_json
            )

            # 保存报告
            report_path = output_path / f"iteration_{iteration}" / "validation_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            success_rate = report['success_rate']
            logger.info(f"第 {iteration + 1} 次迭代成功率: {success_rate:.2%}")

            # 更新最佳结果
            if success_rate > best_score:
                best_score = success_rate
                best_parser = parser_path

            # 检查是否达到目标
            if success_rate >= threshold:
                logger.info(f"达到目标成功率 {threshold:.0%}，停止迭代")
                break

            # 更新失败案例
            failed_cases = report['failed_cases']

        # 复制最佳解析器到输出目录
        if best_parser:
            final_parser_path = output_path / "parser.py"
            final_parser_path.write_text(
                Path(best_parser).read_text(encoding='utf-8'),
                encoding='utf-8'
            )

            logger.info(f"最佳解析器已保存: {final_parser_path}")

        return {
            'best_parser': str(best_parser) if best_parser else None,
            'best_score': best_score,
            'iterations': iteration + 1,
            'final_report': report
        }

    def _load_parser(self, parser_path: str):
        """动态加载解析器

        Args:
            parser_path: 解析器文件路径

        Returns:
            解析器实例
        """
        try:
            spec = importlib.util.spec_from_file_location("parser", parser_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 查找解析器类
            parser_class = getattr(module, 'WebPageParser', None)
            if not parser_class:
                # 尝试查找其他可能的类名
                for name in dir(module):
                    obj = getattr(module, name)
                    if isinstance(obj, type) and hasattr(obj, 'parse'):
                        parser_class = obj
                        break

            if not parser_class:
                raise ValueError("未找到解析器类")

            return parser_class()

        except Exception as e:
            logger.error(f"加载解析器失败: {e}")
            raise

    def _evaluate_result(self, parsed_data: Dict, expected_structure: Dict) -> Dict:
        """评估解析结果

        Args:
            parsed_data: 解析的数据（可能包含嵌套的 type/value/confidence 结构）
            expected_structure: 期望的结构

        Returns:
            评分字典
        """
        field_scores = {}
        issues = []

        for key, expected in expected_structure.items():
            if key not in parsed_data:
                field_scores[key] = 0.0
                issues.append(f"缺少字段: {key}")
                continue

            parsed_field = parsed_data[key]
            expected_type = expected.get('type', 'string')

            # 提取实际值（支持两种格式）
            if isinstance(parsed_field, dict) and 'value' in parsed_field:
                # 新格式：{'type': 'string', 'value': '...', 'confidence': 0.9}
                value = parsed_field.get('value')
                confidence = parsed_field.get('confidence', 1.0)
            else:
                # 旧格式：直接是值
                value = parsed_field
                confidence = 1.0

            # 检查类型和内容
            if expected_type == 'string':
                if isinstance(value, str) and value.strip():
                    # 使用置信度作为分数的一部分
                    field_scores[key] = confidence
                elif isinstance(value, dict):
                    # 如果是字典但期望字符串，可能是格式问题
                    field_scores[key] = 0.0
                    issues.append(f"字段 {key} 格式错误")
                else:
                    field_scores[key] = 0.0
                    issues.append(f"字段 {key} 为空或类型错误")

            elif expected_type == 'array':
                if isinstance(value, list):
                    # 数组评分：根据是否有内容和置信度
                    if value:
                        field_scores[key] = confidence
                    else:
                        # 空数组给部分分数（可能某些页面确实没有该内容）
                        field_scores[key] = 0.5 * confidence
                else:
                    field_scores[key] = 0.0
                    issues.append(f"字段 {key} 类型错误，期望array")

            elif expected_type == 'object':
                if isinstance(value, dict):
                    field_scores[key] = confidence
                else:
                    field_scores[key] = 0.0
                    issues.append(f"字段 {key} 类型错误，期望object")

            else:
                # 其他类型简单检查是否非空
                if value:
                    field_scores[key] = confidence
                else:
                    field_scores[key] = 0.0
                    issues.append(f"字段 {key} 为空")

        # 计算总分
        total_score = sum(field_scores.values()) / len(field_scores) if field_scores else 0

        return {
            'total_score': total_score,
            'field_scores': field_scores,
            'issues': issues
        }

