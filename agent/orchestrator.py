"""
Agent 编排器
整合规划器、执行器和验证器，提供统一的Agent接口
"""
from typing import List, Dict
from pathlib import Path
from loguru import logger
from .planner import AgentPlanner
from .executor import AgentExecutor
from .validator import AgentValidator
from config.settings import settings


class ParserAgent:
    """
    HTML解析器生成Agent
    
    通过给定一组URL，自动生成能够解析这些页面的Python代码
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        初始化Agent
        
        Args:
            output_dir: 输出目录
        """
        self.planner = AgentPlanner()
        self.executor = AgentExecutor(output_dir)
        self.validator = AgentValidator()
        self.output_dir = Path(output_dir)
        
        logger.info("ParserAgent 初始化完成")
    
    def generate_parser(
        self,
        urls: List[str],
        domain: str = None,
        layout_type: str = None,
        validate: bool = True
    ) -> Dict:
        """
        生成解析器
        
        Args:
            urls: URL列表
            domain: 域名（可选）
            layout_type: 布局类型（可选）
            validate: 是否验证生成的代码
        
        Returns:
            生成结果
        """
        logger.info("="*70)
        logger.info("开始生成解析器")
        logger.info("="*70)
        
        # 第一步：规划
        logger.info("\n[步骤 1/4] 任务规划")
        plan = self.planner.create_plan(urls, domain, layout_type)
        
        # 第二步：执行
        logger.info("\n[步骤 2/4] 执行计划")
        execution_result = self.executor.execute_plan(plan)
        
        if not execution_result['success']:
            logger.error("执行失败，无法生成解析器")
            return {
                'success': False,
                'error': '执行失败',
                'execution_result': execution_result
            }
        
        # 第三步：验证（可选）
        validation_result = None
        if validate:
            logger.info("\n[步骤 3/4] 验证解析器")
            parser_path = execution_result['final_parser']['parser_path']
            validation_result = self.validator.validate_parser(parser_path, urls)
            
            # 如果验证未通过，尝试迭代优化
            if not validation_result['passed']:
                logger.warning("初次验证未通过，尝试优化...")
                validation_result = self._iterate_and_improve(
                    execution_result,
                    validation_result,
                    plan
                )
        
        # 第四步：总结
        logger.info("\n[步骤 4/4] 生成总结")
        summary = self._generate_summary(execution_result, validation_result)
        
        logger.info("="*70)
        logger.success("解析器生成完成!")
        logger.info("="*70)
        
        return {
            'success': True,
            'plan': plan,
            'execution_result': execution_result,
            'validation_result': validation_result,
            'summary': summary,
            'parser_path': execution_result['final_parser']['parser_path'],
            'config_path': execution_result['final_parser']['config_path'],
        }
    
    def _iterate_and_improve(
        self,
        execution_result: Dict,
        validation_result: Dict,
        plan: Dict
    ) -> Dict:
        """迭代优化解析器"""
        max_iterations = plan.get('max_iterations', settings.max_iterations)
        
        for iteration in range(1, max_iterations):
            logger.info(f"\n优化迭代 {iteration}/{max_iterations-1}")
            
            # 获取改进建议
            parser_code = execution_result['final_parser']['code']
            suggestions = self.validator.suggest_improvements(validation_result, parser_code)
            
            logger.info(f"改进建议:\n{suggestions}")
            
            # TODO: 实现基于建议的代码改进
            # 这里可以调用LLM重新生成代码，或者进行针对性修复
            
            logger.warning("自动优化功能待实现，请手动修改代码")
            break
        
        return validation_result
    
    def _generate_summary(self, execution_result: Dict, validation_result: Dict = None) -> str:
        """生成执行总结"""
        lines = []
        lines.append("\n" + "="*70)
        lines.append("执行总结")
        lines.append("="*70)
        
        # 样本处理结果
        samples = execution_result.get('samples', [])
        success_samples = [s for s in samples if s.get('success')]
        lines.append(f"\n样本处理: {len(success_samples)}/{len(samples)} 成功")
        
        # 解析器生成结果
        if execution_result.get('final_parser'):
            parser_path = execution_result['final_parser']['parser_path']
            lines.append(f"解析器路径: {parser_path}")
        
        # 验证结果
        if validation_result:
            success_rate = validation_result.get('success_rate', 0)
            passed = validation_result.get('passed', False)
            lines.append(f"\n验证结果: {'通过' if passed else '未通过'}")
            lines.append(f"成功率: {success_rate:.1%}")
        
        lines.append("="*70)
        
        summary = "\n".join(lines)
        logger.info(summary)
        
        return summary

