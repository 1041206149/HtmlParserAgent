"""
代码生成工具
输入json 和 html 生成解析代码
"""
import os
import json
from pathlib import Path
from typing import Dict
from langchain_core.tools import tool
from loguru import logger
from config.settings import Settings
from utils.llm_client import LLMClient


def _build_code_generation_prompt(html_content: str, target_json: Dict) -> str:
    """构建代码生成提示词"""
    if len(html_content) > 30000:
        html_content = html_content[:30000] + "\n... (截断)"

    prompt = f"""
你是一个专业的HTML解析代码生成器。请根据以下信息生成一个Python类，用于解析同类网页。

## 目标结构
需要提取以下字段（JSON格式）：
```json
{json.dumps(target_json, ensure_ascii=False, indent=2)}
```

## HTML示例
```html
{html_content}
```

## 要求
1. 生成一个名为 `WebPageParser` 的Python类
2. 使用 BeautifulSoup 和 lxml 进行解析
3. 实现 `parse(html: str) -> dict` 方法
4. 为每个字段编写提取逻辑，使用XPath或CSS选择器
5. 尽量使用类名、ID等稳定属性，避免使用绝对索引
6. 代码尽量简洁，减少冗余

## 输出格式
请直接输出完整的Python代码，不要包含markdown代码块标记（不要用 ```python 或 ```），不要包含其他说明文字。
代码应该可以直接保存为.py文件运行。
确保代码完整，所有方法和函数都要有完整的实现。

## 使用示例要求
在 `if __name__ == '__main__'` 部分，生成一个灵活的使用示例：
1. 支持从命令行参数接收 HTML 文件路径或 URL
2. 如果是 URL，使用 DrissionPage 的 ChromiumPage 获取 HTML 内容
3. 如果是文件路径，直接读取文件
4. 默认参数示例：使用命令行参数 sys.argv[1]，默认为当前目录的 'sample.html'
"""

    return prompt

@tool
def generate_code_from_html(html_content: str, target_json: Dict, output_dir: str, settings: Settings ) -> Dict:
    """ 从HTML和目标JSON生成解析代码
    Args:
        html_content: HTML内容
        target_json: 目标JSON结构
        output_dir: 输出目录
        settings: 配置对象

    Returns:
        生成结果，包括代码路径和配置路径
    """
    try:
        # 初始化 LLM 客户端（使用代码生成场景）
        llm_client = LLMClient.for_scenario("code_gen")

        # 构建提示词
        prompt = _build_code_generation_prompt(html_content, target_json)

        # 调用 LLM 生成代码
        logger.info("调用LLM生成解析代码...")
        response = llm_client.chat_completion(
            messages=[
                {"role": "system", "content": "你是一个专业的Python代码生成助手。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=settings.code_gen_max_tokens if settings else int(os.getenv("CODE_GEN_MAX_TOKENS", "8192"))
        )

        # 提取生成的代码
        generated_code = response.strip()

        # 保存生成的代码
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        parser_path = output_path / "generated_parser.py"
        parser_path.write_text(generated_code, encoding='utf-8')

        # 生成配置文件
        config = {
            'version': '1.0',
            'fields': {
                key: {
                    'type': value.get('type', 'string'),
                    'description': value.get('description', ''),
                    'required': True
                }
                for key, value in target_json.items()
            },
            'options': {
                'encoding': 'utf-8',
                'timeout': 30,
                'retry': 3
            }
        }
        config_path = output_path / "schema.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        logger.info(f"代码生成完成: {parser_path}")

        return {
            'parser_path': str(parser_path),
            'config_path': str(config_path),
            'code': generated_code,
            'config': config
        }

    except Exception as e:
        logger.error(f"代码生成失败: {str(e)}")
        return {"error": f"代码生成失败: {str(e)}"}
