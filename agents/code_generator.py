"""
代码生成 Agent
"""
import json
from typing import Dict, List
from pathlib import Path
from jinja2 import Template
from loguru import logger

from utils.llm_client import LLMClient
from config.settings import Settings


class CodeGeneratorAgent:
    """代码生成Agent

    负责：
    1. 根据HTML和目标JSON生成解析代码
    2. 生成XPath/CSS选择器
    3. 处理异常和降级策略
    """

    def __init__(self, settings: Settings):
        """初始化代码生成Agent

        Args:
            settings: 配置对象
        """
        self.settings = settings
        self.llm_client = LLMClient(
            api_key=settings.openai_api_key,
            api_base=settings.openai_api_base,
            model=settings.openai_model,
            temperature=settings.openai_temperature
        )

        logger.info("代码生成Agent初始化完成")

    def process(
        self,
        html_content: str,
        target_json: Dict,
        output_dir: str,
        failed_cases: List[Dict] = None
    ) -> Dict:
        """生成解析代码

        Args:
            html_content: HTML内容
            target_json: 目标JSON结构
            output_dir: 输出目录
            failed_cases: 失败案例（用于迭代优化）

        Returns:
            生成结果
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 1. 构建提示词
        prompt = self._build_code_generation_prompt(
            html_content, target_json, failed_cases
        )

        # 2. 调用LLM生成代码
        logger.info("调用LLM生成解析代码...")
        generated_code = self._generate_code(prompt)

        # 3. 保存生成的代码
        parser_path = output_path / "generated_parser.py"
        parser_path.write_text(generated_code, encoding='utf-8')

        # 4. 生成配置文件
        config = self._generate_config(target_json)
        config_path = output_path / "parser_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        logger.info(f"代码生成完成: {parser_path}")

        return {
            'parser_path': str(parser_path),
            'config_path': str(config_path),
            'code': generated_code,
            'config': config
        }

    def _build_code_generation_prompt(
        self,
        html_content: str,
        target_json: Dict,
        failed_cases: List[Dict] = None
    ) -> str:
        """构建代码生成提示词

        Args:
            html_content: HTML内容
            target_json: 目标JSON
            failed_cases: 失败案例

        Returns:
            提示词
        """
        # 截断过长的HTML
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
5. 添加异常处理和降级策略
6. 尽量使用类名、ID等稳定属性，避免使用绝对索引
7. 添加详细注释说明提取逻辑

"""

        # 如果有失败案例，添加优化提示
        if failed_cases:
            prompt += f"""
## 失败案例（需要优化）
以下是之前版本在其他页面上的失败情况，请针对性优化：
```json
{json.dumps(failed_cases[:3], ensure_ascii=False, indent=2)}
```

优化建议：
- 使用更通用的选择器
- 添加多个候选路径
- 增强容错处理
"""

        prompt += """
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

示例代码框架：
```python
if __name__ == '__main__':
    import sys
    
    # 获取输入源（URL 或文件路径）
    source = sys.argv[1] if len(sys.argv) > 1 else 'sample.html'
    
    # 判断是 URL 还是文件
    if source.startswith('http://') or source.startswith('https://'):
        # 使用 DrissionPage 获取 HTML
        from DrissionPage import ChromiumPage
        page = ChromiumPage()
        page.get(source)
        html_content = page.html
        page.quit()
    else:
        # 读取本地文件
        with open(source, 'r', encoding='utf-8') as f:
            html_content = f.read()
    
    # 解析并输出结果
    parser = WebPageParser()
    result = parser.parse(html_content)
    print(json.dumps(result, indent=2, ensure_ascii=False))
```
"""

        return prompt

    def _generate_code(self, prompt: str) -> str:
        """调用LLM生成代码

        Args:
            prompt: 提示词

        Returns:
            生成的代码
        """
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的Python代码生成助手，擅长编写HTML解析代码。请直接输出纯Python代码，不要使用markdown代码块标记。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.llm_client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=8192  # 增加token限制以避免截断
        )

        # 提取代码块
        code = self._extract_code_block(response)

        # 验证代码完整性
        if not self._validate_code_completeness(code):
            logger.warning("生成的代码可能不完整，正在尝试补全...")
            # 可以在这里添加重试逻辑

        return code

    def _extract_code_block(self, response: str) -> str:
        """从响应中提取代码块

        Args:
            response: LLM响应

        Returns:
            代码
        """
        import re

        # 去除首尾空白
        response = response.strip()

        # 尝试提取 ```python ... ``` 代码块
        pattern = r'```python\s*\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            logger.debug("从 ```python 代码块中提取代码")
            return matches[0].strip()

        # 尝试提取 ``` ... ``` 代码块
        pattern = r'```\s*\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            logger.debug("从 ``` 代码块中提取代码")
            return matches[0].strip()

        # 如果响应以 ```python 或 ``` 开头但没有结束标记（代码被截断）
        if response.startswith('```python\n') or response.startswith('```\n'):
            logger.warning("检测到代码块开始标记但没有结束标记，可能被截断")
            # 移除开头的标记
            code = re.sub(r'^```python\s*\n', '', response)
            code = re.sub(r'^```\s*\n', '', code)
            return code.strip()

        # 如果响应以 ```python 或 ``` 开头（没有换行）
        if response.startswith('```python'):
            code = response[9:].strip()  # 移除 ```python
            return code
        if response.startswith('```'):
            code = response[3:].strip()  # 移除 ```
            return code

        # 如果没有代码块标记，返回整个响应
        logger.debug("未找到代码块标记，返回整个响应")
        return response

    def _validate_code_completeness(self, code: str) -> bool:
        """验证代码完整性

        Args:
            code: 生成的代码

        Returns:
            是否完整
        """
        # 基本检查：代码是否包含必要的类定义和方法
        if 'class WebPageParser' not in code:
            logger.error("代码缺少 WebPageParser 类定义")
            return False

        if 'def parse(' not in code:
            logger.error("代码缺少 parse 方法")
            return False

        # 检查是否有未完成的语句（以 = 结尾且后面没有值）
        lines = code.strip().split('\n')
        last_line = lines[-1].strip() if lines else ""
        if last_line.endswith('=') or last_line.endswith(','):
            logger.error(f"代码可能不完整，最后一行: {last_line}")
            return False

        # 检查括号匹配
        open_parens = code.count('(') - code.count(')')
        open_brackets = code.count('[') - code.count(']')
        open_braces = code.count('{') - code.count('}')

        if open_parens != 0 or open_brackets != 0 or open_braces != 0:
            logger.error(f"括号不匹配: () {open_parens}, [] {open_brackets}, {{}} {open_braces}")
            return False

        return True

    def _generate_config(self, target_json: Dict) -> Dict:
        """生成配置文件

        Args:
            target_json: 目标JSON

        Returns:
            配置字典
        """
        config = {
            'version': '1.0',
            'fields': {},
            'options': {
                'encoding': 'utf-8',
                'timeout': 30,
                'retry': 3
            }
        }

        # 提取字段定义
        for key, value in target_json.items():
            if isinstance(value, dict) and 'type' in value:
                config['fields'][key] = {
                    'type': value['type'],
                    'description': value.get('description', ''),
                    'required': True
                }

        return config

