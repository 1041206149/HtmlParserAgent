"""
Agent 执行器
负责执行具体的任务步骤
"""
from typing import Dict, List
from pathlib import Path
from loguru import logger
from tools import (
    get_webpage_source,
    capture_webpage_screenshot,
    extract_json_from_image,
    generate_parser_code
)


class AgentExecutor:
    """Agent执行器，负责执行具体任务"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        self.screenshots_dir = self.output_dir / "screenshots"
        self.parsers_dir = self.output_dir / "parsers"
        self.screenshots_dir.mkdir(exist_ok=True)
        self.parsers_dir.mkdir(exist_ok=True)
    
    def execute_plan(self, plan: Dict) -> Dict:
        """
        执行计划
        
        Args:
            plan: 执行计划
        
        Returns:
            执行结果
        """
        logger.info("开始执行计划...")
        
        results = {
            'plan': plan,
            'samples': [],
            'final_parser': None,
            'success': False,
        }
        
        # 处理每个样本URL
        for idx, url in enumerate(plan['sample_urls'], 1):
            logger.info(f"处理样本 {idx}/{len(plan['sample_urls'])}: {url}")
            
            try:
                sample_result = self._process_url(url, idx)
                results['samples'].append(sample_result)
            except Exception as e:
                logger.error(f"处理URL失败: {str(e)}")
                results['samples'].append({
                    'url': url,
                    'error': str(e),
                    'success': False
                })
        
        # 生成最终的解析器
        if results['samples']:
            results['final_parser'] = self._generate_final_parser(results['samples'], plan)
            results['success'] = results['final_parser'] is not None
        
        return results
    
    def _process_url(self, url: str, idx: int) -> Dict:
        """处理单个URL"""
        result = {
            'url': url,
            'html': None,
            'screenshot': None,
            'schema': None,
            'success': False,
        }
        
        try:
            # 1. 获取HTML源码
            logger.info("  [1/3] 获取HTML源码...")
            result['html'] = get_webpage_source(url)
            
            # 2. 截图
            logger.info("  [2/3] 截图...")
            screenshot_path = str(self.screenshots_dir / f"sample_{idx}.png")
            result['screenshot'] = capture_webpage_screenshot(url, save_path=screenshot_path)
            
            # 3. 提取JSON Schema
            logger.info("  [3/3] 提取JSON Schema...")
            result['schema'] = extract_json_from_image(result['screenshot'])
            
            result['success'] = True
            logger.success(f"  样本处理完成")
            
        except Exception as e:
            logger.error(f"  处理失败: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def _generate_final_parser(self, samples: List[Dict], plan: Dict) -> Dict:
        """生成最终的解析器"""
        logger.info("生成最终解析器...")
        
        # 使用第一个成功的样本生成代码
        successful_sample = None
        for sample in samples:
            if sample.get('success'):
                successful_sample = sample
                break
        
        if not successful_sample:
            logger.error("没有成功的样本，无法生成解析器")
            return None
        
        try:
            # 合并所有样本的schema（简化版：使用第一个）
            merged_schema = successful_sample['schema']
            
            # 生成解析代码
            parser_result = generate_parser_code(
                html_content=successful_sample['html'],
                target_json=merged_schema,
                output_dir=str(self.parsers_dir)
            )
            
            logger.success(f"解析器生成完成: {parser_result['parser_path']}")
            return parser_result
            
        except Exception as e:
            logger.error(f"生成解析器失败: {str(e)}")
            return None

