"""
视觉理解 Agent
"""
import json
from typing import Dict, List  # 移除未使用的 Optional
from pathlib import Path
from loguru import logger

from utils.llm_client import LLMClient
from utils.screenshot import ScreenshotTool
from config.settings import Settings

# 新增: 并行处理所需
from concurrent.futures import ThreadPoolExecutor, as_completed


class VisualUnderstandingAgent:
    """视觉理解Agent

    负责：
    1. 渲染HTML并截图
    2. 分块处理大图
    3. 调用VLLM分析图片
    4. 合并结果生成结构化JSON
    """

    def __init__(self, settings: Settings):
        """初始化视觉理解Agent

        Args:
            settings: 配置对象
        """
        self.settings = settings
        self.llm_client = LLMClient.from_settings(settings, model=settings.vision_model)
        self.screenshot_tool = ScreenshotTool(
            headless=settings.headless,
            timeout=settings.timeout,
            max_width=settings.screenshot_max_width,
            max_height=settings.screenshot_max_height
        )

        logger.info(f"视觉理解Agent初始化完成 - 使用模型: {settings.vision_model}")

    def process(self, url: str, output_dir: str) -> Dict:
        """处理URL的视觉理解

        Args:
            url: 目标URL
            output_dir: 输出目录

        Returns:
            结构化JSON结果
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 1. 截图
        screenshot_path = output_path / "screenshot.png"
        self.screenshot_tool.capture_url(
            url=url,
            output_path=str(screenshot_path),
            full_page=self.settings.screenshot_full_page
        )

        # 2. 检查图片大小，如果过大则分块
        chunks = self.screenshot_tool.split_screenshot(
            image_path=str(screenshot_path),
            chunk_height=2000,
            overlap=200
        )

        # 3. 分析每个图片块（支持并行）
        chunk_results: List[Dict] = []
        if self.settings.vision_parallel and len(chunks) > 1:
            logger.info(f"开始并行分析 {len(chunks)} 个图片块 (max_workers={self.settings.vision_max_workers})")
            # 预分配结果列表，保持索引顺序
            chunk_results = [{} for _ in chunks]
            with ThreadPoolExecutor(max_workers=self.settings.vision_max_workers) as executor:
                future_map = {
                    executor.submit(self._analyze_screenshot, chunk_path, idx): idx
                    for idx, chunk_path in enumerate(chunks)
                }
                for future in as_completed(future_map):
                    idx = future_map[future]
                    try:
                        result = future.result()
                        chunk_results[idx] = result
                        logger.debug(f"图片块 {idx+1} 分析完成")
                    except Exception as e:
                        logger.error(f"图片块 {idx+1} 分析失败: {e}")
            logger.info("并行图片块分析完成")
        else:
            logger.info(f"开始顺序分析 {len(chunks)} 个图片块")
            for i, chunk_path in enumerate(chunks):
                logger.info(f"分析图片块 {i+1}/{len(chunks)}")
                result = self._analyze_screenshot(chunk_path, i)
                chunk_results.append(result)

        # 4. 合并结果
        merged_result = self._merge_results(chunk_results)

        # 5. 保存结果
        output_json_path = output_path / "vision_output.json"
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(merged_result, f, ensure_ascii=False, indent=2)

        logger.info(f"视觉理解完成，结果保存至: {output_json_path}")

        return {
            'url': url,
            'screenshot_path': str(screenshot_path),
            'chunks': chunks,
            'result': merged_result,
            'output_path': str(output_json_path)
        }

    def _analyze_screenshot(self, image_path: str, chunk_index: int) -> Dict:
        """分析单个截图

        Args:
            image_path: 图片路径
            chunk_index: 块索引

        Returns:
            分析结果
        """
        # 转换为Base64
        image_data = self.screenshot_tool.image_to_base64(image_path)

        # 构建提示词
        prompt = self._build_vision_prompt(chunk_index)

        # 调用VLLM
        try:
            response = self.llm_client.vision_completion(
                prompt=prompt,
                image_data=image_data,
                max_tokens=4096
            )

            # 解析JSON响应
            result = self._parse_vision_response(response)
            return result

        except Exception as e:
            logger.error(f"图片分析失败: {e}")
            return {}

    def _build_vision_prompt(self, chunk_index: int) -> str:
        """构建视觉理解提示词

        Args:
            chunk_index: 块索引

        Returns:
            提示词
        """
        prompt = f"""
请仔细观察这张网页截图（第 {chunk_index + 1} 部分），识别并提取页面中的关键信息字段。

你需要：
1. 自主判断页面类型（如：文章页、列表页、商品页、表单页等）
2. 识别页面中存在的关键字段（例如标题、日期、正文等），非关键信息（例如导航栏、页脚、图片等）请忽略
3. value字段提取实际值，不要生成页面不存在的内容
4. 为每个识别到的字段提取内容，如果某个片段过长，可以适当截断


返回JSON格式如下：

{{
  "字段名1": {{
    "type": "string|number|array|object",
    "description": "该字段的语义描述（中文）",
    "value": "提取的实际值",
    "confidence": 0.95
  }},
  "字段名2": {{
    "type": "...",
    "description": "...",
    "value": ...,
    "confidence": 0.90
  }},
  ...
}}

**常见字段参考**（但不限于）：
- 文章类：title, author, publish_time, summary, content, category, tags, views, likes, comments

**要求**：
1. 只返回JSON，不要其他说明文字
2. 字段名使用英文，采用snake_case命名
3. 为每个字段标注type、description、value和confidence(0-1)
4. 如果某部分信息不清晰，降低confidence值
"""
        return prompt

    def _parse_vision_response(self, response: str) -> Dict:
        """解析VLLM响应

        Args:
            response: LLM响应文本

        Returns:
            解析后的字典
        """
        try:
            import re
            # 简化正则，避免不必要的转义警告
            json_match = re.search(r"{.*}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response)
        except Exception as e:
            logger.error(f"解析响应失败: {e}")
            return {}

    def _merge_results(self, chunk_results: List[Dict]) -> Dict:
        """合并多个块的结果

        Args:
            chunk_results: 块结果列表

        Returns:
            合并后的结果
        """
        if not chunk_results:
            return {}

        if len(chunk_results) == 1:
            return chunk_results[0]

        # 合并策略：选择置信度最高的值
        merged = {}
        all_keys = set()
        for result in chunk_results:
            all_keys.update(result.keys())

        for key in all_keys:
            candidates = [
                r[key] for r in chunk_results
                if key in r and r[key].get('value') is not None
            ]

            if not candidates:
                continue

            # 选择置信度最高的
            best = max(candidates, key=lambda x: x.get('confidence', 0))

            # 对于数组类型，合并所有非空值
            if best.get('type') == 'array':
                all_values = []
                for c in candidates:
                    if isinstance(c.get('value'), list):
                        all_values.extend(c['value'])
                # 去重（处理字典和普通值）
                if all_values:
                    # 检查第一个元素类型
                    if isinstance(all_values[0], dict):
                        # 对于字典列表，使用JSON字符串去重
                        import json as _json
                        seen = set()
                        unique_values = []
                        for item in all_values:
                            item_str = _json.dumps(item, sort_keys=True, ensure_ascii=False)
                            if item_str not in seen:
                                seen.add(item_str)
                                unique_values.append(item)
                        best['value'] = unique_values
                    else:
                        # 对于简单类型，直接使用set去重
                        try:
                            best['value'] = list(set(all_values))
                        except TypeError:
                            # 如果还是不可哈希，保留原值
                            best['value'] = all_values

            # 对于字符串类型，如果是content，尝试拼接
            elif best.get('type') == 'string' and key == 'content':
                all_contents = [c['value'] for c in candidates if c.get('value')]
                best['value'] = '\n\n'.join(all_contents)

            merged[key] = best

        logger.info(f"合并 {len(chunk_results)} 个结果完成")
        return merged

