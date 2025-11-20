"""
图片 → JSON 结构化信息提取工具
一次性输入整张图片，不做分块。
"""
import os
import json
import base64
import re
from typing import Dict
from langchain_core.tools import tool
from utils.llm_client import LLMClient


def _image_to_base64(image_path: str) -> str:
    """读取图片并转 Base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _build_prompt() -> str:
    """构建视觉模型提示词（来自你原来的 _build_vision_prompt）"""
    return """
请仔细观察整张网页截图，识别并提取页面中的关键信息字段。

你需要：
1. 自主判断页面类型（如：文章页、列表页、商品页、表单页等）
2. 识别页面中存在的关键字段（例如标题、日期、正文等），非关键信息（例如导航栏、页脚、图片广告等）请忽略
3. value字段提取实际值，不要生成页面不存在的内容
4. 为每个识别到的字段提取内容，如果内容过长可以适当截断

返回 JSON 格式如下：

{
  "字段名1": {
    "type": "string|number|array|object",
    "description": "字段语义（中文）",
    "value": "实际提取值",
    "confidence": 0.95
  }
}

要求：
1. 只返回 JSON，无任何解释文本
2. 字段名必须使用英文 snake_case
3. 每个字段必须有 type / description / value / confidence
"""


def _parse_llm_response(response: str) -> Dict:
    """解析模型响应中的 JSON"""
    try:
        match = re.search(r"{.*}", response, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(response)
    except Exception as e:
        return {"error": f"解析模型响应失败: {str(e)}"}


@tool
def extract_json_from_image(image_path: str, model: str = None) -> Dict:
    """
    从图片中提取结构化页面信息（一次性分析整张图）

    Args:
        image_path: 图片文件路径
        model: 使用的视觉模型，默认使用配置文件中的 VISION_MODEL

    Returns:
        dict: 模型解析得到的结构化 JSON
    """
    try:
        # 1. 图片转 base64
        image_data = _image_to_base64(image_path)

        # 2. 构建提示词
        prompt = _build_prompt()

        # 3. 创建 LLM 客户端（使用视觉理解场景）
        if model:
            # 如果指定了模型，使用指定的模型
            llm = LLMClient(model=model)
        else:
            # 否则使用视觉场景的默认配置
            llm = LLMClient.for_scenario("vision")

        # 4. 调用视觉模型
        response = llm.vision_completion(
            prompt=prompt,
            image_data=image_data,
            max_tokens=int(os.getenv("VISION_MAX_TOKENS", "4096"))
        )

        # 5. 提取 JSON
        return _parse_llm_response(response)

    except Exception as e:
        return {"error": f"图片处理失败: {str(e)}"}


if __name__ == "__main__":
    # 本地测试
    path = "test.png"
    result = extract_json_from_image.invoke({"image_path": path})
    print(json.dumps(result, ensure_ascii=False, indent=2))