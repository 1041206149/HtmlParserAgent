# HtmlParserAgent 工作流程框架

> 本文档详细描述了 HtmlParserAgent 的完整工作流程，包括每个步骤的细节、输入输出、使用的技术和可优化点。

---

## 📊 整体架构

```
用户输入 URLs
    ↓
┌─────────────────────────────────────────────────────────┐
│  ParserAgent (Orchestrator)                             │
│  ├─ AgentPlanner    (任务规划)                          │
│  ├─ AgentExecutor   (任务执行)                          │
│  └─ AgentValidator  (代码验证)                          │
└─────────────────────────────────────────────────────────┘
    ↓
生成的 Python 解析器代码
```

---

## 🔄 完整工作流程

### 阶段 0: 初始化

**文件**: `agent/orchestrator.py` - `ParserAgent.__init__()`

**执行内容**:
```python
1. 创建 AgentPlanner 实例
2. 创建 AgentExecutor 实例
3. 创建 AgentValidator 实例
4. 设置输出目录
```

**使用的资源**:
- 配置文件: `config/settings.py`
- 环境变量: `.env`

**可优化点**:
- [ ] 添加配置验证（检查 API key 是否有效）
- [ ] 支持自定义工具注册
- [ ] 添加缓存机制（避免重复处理相同 URL）

---

### 阶段 1: 任务规划 (Planning)

**文件**: `agent/planner.py` - `AgentPlanner.create_plan()`

**输入**:
- `urls`: List[str] - 待解析的 URL 列表
- `domain`: str (可选) - 域名
- `layout_type`: str (可选) - 布局类型（如 blog, article, product）

**执行流程**:

#### 1.1 提取域名
```python
def _extract_domain(url: str) -> str
```
- 从 URL 中解析域名
- 使用 `urllib.parse.urlparse()`

**可优化点**:
- [ ] 支持子域名识别
- [ ] 自动识别网站类型（电商、新闻、博客等）

#### 1.2 构建规划提示词
```python
def _build_planning_prompt(urls, domain, layout_type) -> str
```
- 生成给 LLM 的提示词
- 包含: 域名、布局类型、URL 数量、示例 URL

**提示词内容**:
- 任务目标描述
- URL 信息
- 要求 LLM 分析并制定计划

**可优化点**:
- [ ] 提示词过于简单，LLM 返回的计划未被充分利用
- [ ] 可以要求 LLM 返回结构化的 JSON 计划
- [ ] 添加更多上下文（如历史成功案例）
- [ ] 支持 Few-shot 示例

#### 1.3 调用 LLM 生成计划
```python
messages = [
    {"role": "system", "content": "你是一个专业的网页解析任务规划助手。"},
    {"role": "user", "content": prompt}
]
response = self.llm.invoke(messages)
```

**使用的模型**:
- 模型: `settings.agent_model` (默认: claude-sonnet-4-5-20250929)
- Temperature: `settings.agent_temperature` (默认: 0)

**可优化点**:
- [ ] **当前问题**: LLM 的分析结果未被使用，直接创建了固定计划
- [ ] 让 LLM 返回结构化计划（JSON 格式）
- [ ] 根据 URL 数量动态调整样本数量
- [ ] 添加计划验证逻辑

#### 1.4 解析计划
```python
def _parse_plan(response, urls, domain, layout_type) -> Dict
```

**当前实现**: 忽略 LLM 响应，直接创建固定计划

**返回的计划结构**:
```python
{
    'domain': str,              # 域名
    'layout_type': str,         # 布局类型
    'total_urls': int,          # 总 URL 数
    'sample_urls': List[str],   # 样本 URL（最多3个）
    'steps': [                  # 执行步骤
        'fetch_html',
        'capture_screenshot',
        'extract_schema',
        'generate_code',
        'validate_code'
    ],
    'llm_analysis': str,        # LLM 的分析（未使用）
    'max_iterations': int,      # 最大迭代次数
    'success_threshold': float  # 成功率阈值
}
```

**可优化点**:
- [ ] **重要**: 实际使用 LLM 的分析结果
- [ ] 动态生成步骤列表（而非固定）
- [ ] 支持并行处理多个 URL
- [ ] 添加智能采样策略（选择最具代表性的 URL）

---

### 阶段 2: 任务执行 (Execution)

**文件**: `agent/executor.py` - `AgentExecutor.execute_plan()`

**输入**:
- `plan`: Dict - 来自 Planner 的执行计划

**执行流程**:

#### 2.1 处理每个样本 URL

**循环处理**: `plan['sample_urls']` 中的每个 URL

对每个 URL 执行 `_process_url(url, idx)`:

##### 步骤 2.1.1: 获取 HTML 源码

**工具**: `tools/webpage_source.py` - `get_webpage_source`

**技术栈**:
- DrissionPage (ChromiumPage)
- 无头浏览器模式

**执行细节**:
```python
1. 配置无头浏览器选项
2. 创建 ChromiumPage 实例
3. 访问 URL
4. 等待页面加载 (默认 3 秒)
5. 获取 HTML 源码
6. 关闭浏览器
```

**输出**: HTML 字符串

**可优化点**:
- [ ] 等待时间固定为 3 秒，应该动态调整
- [ ] 缺少智能等待（等待特定元素加载完成）
- [ ] 没有处理动态加载内容（AJAX、懒加载）
- [ ] 缺少反爬虫对策（User-Agent、代理等）
- [ ] 每次都创建新浏览器实例，性能低
- [ ] 建议: 使用浏览器池复用实例
- [ ] 建议: 添加页面加载完成检测
- [ ] 建议: 支持滚动加载更多内容

##### 步骤 2.1.2: 捕获网页截图

**工具**: `tools/webpage_screenshot.py` - `capture_webpage_screenshot`

**技术栈**:
- DrissionPage (ChromiumPage)
- 全页截图

**执行细节**:
```python
1. 配置浏览器选项（窗口大小: 1920x1080）
2. 创建 ChromiumPage 实例
3. 访问 URL
4. 等待 3 秒
5. 截取全页截图
6. 保存到指定路径
7. 关闭浏览器
```

**输出**: 截图文件的绝对路径

**可优化点**:
- [ ] **重复访问**: 与步骤 2.1.1 重复访问同一 URL，浪费时间
- [ ] **建议**: 合并步骤 2.1.1 和 2.1.2，一次访问同时获取 HTML 和截图
- [ ] 窗口大小固定，应该支持响应式测试
- [ ] 缺少移动端视图支持
- [ ] 截图质量和格式不可配置
- [ ] 建议: 支持截取特定区域
- [ ] 建议: 支持多分辨率截图

##### 步骤 2.1.3: 提取 JSON Schema

**工具**: `tools/visual_understanding.py` - `extract_json_from_image`

**技术栈**:
- 视觉语言模型 (VLM)
- Base64 图片编码
- LangChain ChatOpenAI

**执行细节**:
```python
1. 读取截图并转换为 Base64
2. 构建视觉理解提示词
3. 创建 ChatOpenAI 实例（vision_model）
4. 发送多模态消息（文本 + 图片）
5. 解析 LLM 返回的 JSON
6. 提取字段信息
```

**提示词要求**:
- 识别页面类型
- 提取关键字段（忽略导航、页脚等）
- 返回 JSON 格式：
  ```json
  {
    "field_name": {
      "type": "string|number|array|object",
      "description": "字段描述",
      "value": "实际值",
      "confidence": 0.95
    }
  }
  ```

**使用的模型**:
- 模型: `settings.vision_model` (默认: qwen-vl-max)
- Temperature: `settings.vision_temperature` (默认: 0)

**输出**: Dict - 结构化的字段信息

**可优化点**:
- [ ] VLM 可能识别不准确，缺少人工审核机制
- [ ] 没有利用 HTML 结构辅助识别
- [ ] 建议: 结合 HTML 和截图双重验证
- [ ] 建议: 添加字段重要性排序
- [ ] 建议: 支持用户交互式调整字段
- [ ] 建议: 添加字段去重和合并逻辑
- [ ] 提示词可以更详细（提供示例）
- [ ] 缺少对复杂布局的处理（表格、列表等）

#### 2.2 生成最终解析器

**方法**: `_generate_final_parser(samples, plan)`

**执行细节**:
```python
1. 选择第一个成功的样本
2. 使用该样本的 HTML 和 Schema
3. 调用代码生成工具
```

**可优化点**:
- [ ] **只使用第一个样本**: 应该合并多个样本的 Schema
- [ ] 没有分析样本之间的差异
- [ ] 建议: 提取所有样本的公共字段
- [ ] 建议: 识别可选字段和必需字段
- [ ] 建议: 生成更通用的解析逻辑

##### 步骤 2.2.1: 生成解析代码

**工具**: `tools/code_generator.py` - `generate_parser_code`

**技术栈**:
- LangChain ChatOpenAI
- BeautifulSoup 代码生成

**执行细节**:
```python
1. 构建代码生成提示词
   - 包含目标 JSON 结构
   - 包含 HTML 示例（截断到 30000 字符）
2. 调用 LLM 生成代码
3. 清理 markdown 标记
4. 保存代码到文件
5. 生成配置文件 (schema.json)
```

**提示词要求**:
- 生成 `WebPageParser` 类
- 使用 BeautifulSoup + lxml
- 实现 `parse(html: str) -> dict` 方法
- 使用 CSS 选择器或 XPath
- 添加错误处理
- **严格要求**: 不使用 markdown 标记

**使用的模型**:
- 模型: `settings.code_gen_model` (默认: claude-sonnet-4-5-20250929)
- Temperature: `settings.code_gen_temperature` (默认: 0.3)

**输出**:
```python
{
    'parser_path': str,    # 生成的代码路径
    'config_path': str,    # 配置文件路径
    'code': str,           # 生成的代码内容
    'config': dict         # 配置内容
}
```

**可优化点**:
- [ ] HTML 截断可能丢失重要信息
- [ ] 建议: 智能截断（保留关键部分）
- [ ] 生成的代码质量依赖 LLM，不稳定
- [ ] 缺少代码模板和最佳实践注入
- [ ] 建议: 使用 Few-shot 示例提高质量
- [ ] 建议: 添加代码格式化（black、autopep8）
- [ ] 建议: 添加类型注解
- [ ] 建议: 生成单元测试
- [ ] 配置文件功能有限，可以扩展

---

### 阶段 3: 代码验证 (Validation)

**文件**: `agent/validator.py` - `AgentValidator.validate_parser()`

**输入**:
- `parser_path`: str - 生成的解析器代码路径
- `test_urls`: List[str] - 测试 URL 列表

**执行流程**:

#### 3.1 加载解析器

**方法**: `_load_parser(parser_path)`

**执行细节**:
```python
1. 使用 importlib.util 动态加载模块
2. 查找 WebPageParser 类
3. 实例化解析器
```

**可优化点**:
- [ ] 缺少语法检查（在加载前）
- [ ] 建议: 使用 ast.parse() 预检查
- [ ] 建议: 添加沙箱环境执行
- [ ] 缺少依赖检查
- [ ] 建议: 捕获 import 错误并提示缺失的包

#### 3.2 测试每个 URL

**方法**: `_test_url(parser, url)`

**执行细节**:
```python
1. 获取 URL 的 HTML（再次访问）
2. 调用 parser.parse(html)
3. 检查返回结果是否为非空字典
4. 记录成功/失败
```

**可优化点**:
- [ ] **再次访问 URL**: 应该复用之前获取的 HTML
- [ ] 验证逻辑过于简单（只检查非空）
- [ ] 建议: 验证字段类型是否正确
- [ ] 建议: 验证提取的值是否合理
- [ ] 建议: 与预期 Schema 对比
- [ ] 建议: 添加数据质量评分
- [ ] 缺少性能测试（解析速度）
- [ ] 缺少异常处理测试

#### 3.3 计算成功率

```python
success_rate = success_count / len(test_urls)
passed = success_rate >= settings.success_threshold
```

**阈值**: `settings.success_threshold` (默认: 0.8 = 80%)

**可优化点**:
- [ ] 成功率计算过于粗糙
- [ ] 建议: 考虑字段级别的成功率
- [ ] 建议: 加权评分（重要字段权重更高）

#### 3.4 问题诊断

**方法**: `diagnose_issues(validation_result)`

**执行细节**:
```python
1. 统计失败测试的错误类型
2. 生成问题列表
```

**可优化点**:
- [ ] 诊断信息过于简单
- [ ] 建议: 分析错误模式
- [ ] 建议: 提供具体的修复建议
- [ ] 建议: 识别常见问题（选择器失效、编码问题等）

#### 3.5 改进建议

**方法**: `suggest_improvements(validation_result, parser_code)`

**执行细节**:
```python
1. 收集诊断问题
2. 构建提示词（包含问题和代码片段）
3. 调用 LLM 分析并给出建议
```

**可优化点**:
- [ ] **建议未被使用**: 只是打印出来，没有自动修复
- [ ] 代码片段只取前 1000 字符，可能不够
- [ ] 建议: 实现自动修复功能
- [ ] 建议: 提供多个修复方案供选择
- [ ] 建议: 记录历史问题和解决方案

---

### 阶段 4: 迭代优化 (Iteration)

**文件**: `agent/orchestrator.py` - `_iterate_and_improve()`

**当前状态**: ⚠️ **未实现**

**设计意图**:
```python
1. 获取改进建议
2. 基于建议重新生成代码
3. 再次验证
4. 重复直到达到成功率或最大迭代次数
```

**可优化点**:
- [ ] **核心功能缺失**: 需要实现完整的迭代逻辑
- [ ] 建议: 实现基于 LLM 的代码修复
- [ ] 建议: 实现基于规则的代码修复
- [ ] 建议: 添加人工介入选项
- [ ] 建议: 记录每次迭代的改进效果
- [ ] 建议: 实现 A/B 测试（保留多个版本）

---

### 阶段 5: 生成总结 (Summary)

**文件**: `agent/orchestrator.py` - `_generate_summary()`

**执行细节**:
```python
1. 统计样本处理结果
2. 记录解析器路径
3. 显示验证结果和成功率
4. 输出总结信息
```

**输出示例**:
```
======================================================================
执行总结
======================================================================

样本处理: 1/1 成功
解析器路径: output/blog/parsers/generated_parser.py

验证结果: 通过
成功率: 100.0%
======================================================================
```

**可优化点**:
- [ ] 总结信息过于简单
- [ ] 建议: 添加性能指标（耗时、资源使用）
- [ ] 建议: 添加质量评分
- [ ] 建议: 生成详细报告（HTML/PDF）
- [ ] 建议: 提供使用建议和注意事项
- [ ] 建议: 添加可视化（字段覆盖率图表等）

---

## 🛠️ 工具详解

### 工具 1: get_webpage_source

**文件**: `tools/webpage_source.py`

**功能**: 获取网页 HTML 源码

**依赖**: DrissionPage

**参数**:
- `url`: str - 网页 URL
- `wait_time`: int - 等待时间（默认 3 秒）

**返回**: str - HTML 源码

**优化建议**:
- [ ] 添加重试机制
- [ ] 支持自定义 User-Agent
- [ ] 支持代理设置
- [ ] 添加缓存机制
- [ ] 支持 Cookie 管理
- [ ] 支持 JavaScript 执行等待

### 工具 2: capture_webpage_screenshot

**文件**: `tools/webpage_screenshot.py`

**功能**: 捕获网页截图

**依赖**: DrissionPage

**参数**:
- `url`: str - 网页 URL
- `save_path`: str - 保存路径
- `full_page`: bool - 是否全页截图
- `width`: int - 窗口宽度
- `height`: int - 窗口高度

**返回**: str - 截图文件路径

**优化建议**:
- [ ] 支持多分辨率
- [ ] 支持移动端模拟
- [ ] 添加水印或标注
- [ ] 支持截图压缩
- [ ] 支持截取特定元素

### 工具 3: extract_json_from_image

**文件**: `tools/visual_understanding.py`

**功能**: 从截图提取结构化信息

**依赖**: LangChain, VLM

**参数**:
- `image_path`: str - 图片路径

**返回**: Dict - 结构化字段信息

**优化建议**:
- [ ] 支持多图片输入（对比分析）
- [ ] 添加置信度阈值过滤
- [ ] 支持字段优先级设置
- [ ] 结合 HTML 结构验证
- [ ] 添加人工标注接口

### 工具 4: generate_parser_code

**文件**: `tools/code_generator.py`

**功能**: 生成解析器代码

**依赖**: LangChain, LLM

**参数**:
- `html_content`: str - HTML 内容
- `target_json`: Dict - 目标结构
- `output_dir`: str - 输出目录

**返回**: Dict - 生成结果

**优化建议**:
- [ ] 支持多种解析库（Scrapy、lxml、pyquery）
- [ ] 添加代码模板系统
- [ ] 支持增量生成（只生成特定字段）
- [ ] 添加代码审查和优化
- [ ] 生成配套的测试代码

---

## 📊 数据流图

```
用户输入
  ↓
URLs → [Planner] → Plan
                      ↓
                   [Executor]
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
    Sample 1      Sample 2      Sample 3
        ↓             ↓             ↓
   get_webpage_source (HTML)
        ↓             ↓             ↓
   capture_webpage_screenshot (PNG)
        ↓             ↓             ↓
   extract_json_from_image (Schema)
        ↓             ↓             ↓
        └─────────────┼─────────────┘
                      ↓
              Merge Schemas
                      ↓
          generate_parser_code
                      ↓
              Parser Code (.py)
                      ↓
              [Validator]
                      ↓
         Test with URLs
                      ↓
            Validation Result
                      ↓
         ┌────────────┴────────────┐
         ↓                         ↓
      Passed                   Failed
         ↓                         ↓
      Return                  [Iterate]
                                   ↓
                          suggest_improvements
                                   ↓
                          Regenerate Code
                                   ↓
                          (循环直到通过)
```

---

## ⚡ 性能瓶颈分析

### 1. 重复访问 URL

**问题**:
- 步骤 2.1.1 访问 URL 获取 HTML
- 步骤 2.1.2 再次访问同一 URL 截图
- 步骤 3.2 验证时又访问一次

**影响**: 每个 URL 访问 3 次，浪费大量时间

**解决方案**:
- [ ] 合并步骤 2.1.1 和 2.1.2，一次访问同时获取 HTML 和截图
- [ ] 缓存 HTML 内容，验证时复用
- [ ] 使用浏览器池，保持连接

### 2. 串行处理样本

**问题**: 样本按顺序逐个处理

**影响**: 处理 N 个样本需要 N 倍时间

**解决方案**:
- [ ] 并行处理多个样本
- [ ] 使用异步 I/O
- [ ] 使用多进程/多线程

### 3. LLM 调用延迟

**问题**:
- 规划阶段调用 LLM
- 视觉理解调用 VLM
- 代码生成调用 LLM
- 改进建议调用 LLM

**影响**: 每次调用可能需要几秒到几十秒

**解决方案**:
- [ ] 批量处理请求
- [ ] 使用流式输出
- [ ] 添加本地缓存
- [ ] 优化提示词减少 token 数

### 4. 浏览器启动开销

**问题**: 每次获取 HTML 或截图都创建新浏览器实例

**影响**: 启动浏览器需要 1-2 秒

**解决方案**:
- [ ] 使用浏览器池
- [ ] 复用浏览器实例
- [ ] 使用远程浏览器服务

---

## 🎯 关键优化建议（按优先级）

### 🔴 高优先级（核心功能缺失）

1. **实现迭代优化逻辑**
   - 当前只打印建议，不会自动修复
   - 需要实现基于 LLM 的代码修复

2. **实际使用 Planner 的分析结果**
   - 当前 LLM 的规划被忽略
   - 应该让 LLM 返回结构化计划并使用

3. **合并多个样本的 Schema**
   - 当前只使用第一个样本
   - 应该分析所有样本找出公共字段

4. **合并 HTML 获取和截图步骤**
   - 避免重复访问 URL
   - 显著提升性能

### 🟡 中优先级（质量提升）

5. **增强验证逻辑**
   - 不仅检查非空，还要验证字段类型和值
   - 添加数据质量评分

6. **智能等待页面加载**
   - 不使用固定 3 秒等待
   - 检测页面加载完成状态

7. **提升代码生成质量**
   - 使用 Few-shot 示例
   - 添加代码模板
   - 生成单元测试

8. **添加缓存机制**
   - 缓存 HTML 内容
   - 缓存 LLM 响应
   - 避免重复工作

### 🟢 低优先级（体验优化）

9. **添加进度显示**
   - 实时显示处理进度
   - 估算剩余时间

10. **生成详细报告**
    - HTML/PDF 格式报告
    - 包含可视化图表

11. **支持人工交互**
    - 字段选择和调整
    - 代码审查和修改

12. **添加更多工具**
    - 支持 API 接口解析
    - 支持 PDF 解析
    - 支持表格数据提取

---

## 📝 配置参数说明

**文件**: `config/settings.py` 和 `.env`

### API 配置
```bash
OPENAI_API_KEY=sk-xxx          # API 密钥
OPENAI_API_BASE=http://xxx/v1  # API 端点（必须包含 /v1）
```

### 模型配置
```bash
# Agent 模型（用于规划和改进建议）
AGENT_MODEL=claude-sonnet-4-5-20250929
AGENT_TEMPERATURE=0

# 代码生成模型
CODE_GEN_MODEL=claude-sonnet-4-5-20250929
CODE_GEN_TEMPERATURE=0.3
CODE_GEN_MAX_TOKENS=8192

# 视觉理解模型
VISION_MODEL=qwen-vl-max
VISION_TEMPERATURE=0
VISION_MAX_TOKENS=4096
```

### Agent 配置
```bash
MAX_ITERATIONS=5          # 最大迭代次数
SUCCESS_THRESHOLD=0.8     # 成功率阈值（80%）
MIN_SAMPLE_SIZE=2         # 最小样本数量
```

### 浏览器配置
```bash
HEADLESS=true                    # 无头模式
TIMEOUT=30000                    # 超时时间（毫秒）
SCREENSHOT_FULL_PAGE=true        # 全页截图
```

---

## 🚀 使用示例

### 基本用法
```python
from agent import ParserAgent

agent = ParserAgent(output_dir="output/blog")

result = agent.generate_parser(
    urls=["https://example.com/article"],
    domain="example.com",
    layout_type="article",
    validate=True
)

print(f"解析器: {result['parser_path']}")
```

### 分步使用工具
```python
from tools import (
    get_webpage_source,
    capture_webpage_screenshot,
    extract_json_from_image,
    generate_parser_code
)

# 1. 获取 HTML
html = get_webpage_source.invoke({"url": "https://example.com"})

# 2. 截图
screenshot = capture_webpage_screenshot.invoke({
    "url": "https://example.com",
    "save_path": "screenshot.png"
})

# 3. 提取 Schema
schema = extract_json_from_image.invoke({"image_path": screenshot})

# 4. 生成代码
result = generate_parser_code.invoke({
    "html_content": html,
    "target_json": schema,
    "output_dir": "output"
})
```

---

## 📚 相关文档

- [LangChain 1.0 迁移报告](LANGCHAIN_1.0_MIGRATION.md)
- [架构文档](ARCHITECTURE.md)
- [README](README.md)
- [LangChain 官方文档](https://docs.langchain.com/)

---

## 🎉 总结

HtmlParserAgent 是一个创新的 AI 驱动的网页解析器生成工具，通过结合视觉理解和代码生成能力，自动化了传统需要手工编写的解析代码。

**核心优势**:
- ✅ 自动化程度高
- ✅ 使用 LangChain 1.0 现代架构
- ✅ 支持多种模型
- ✅ 模块化设计

**主要挑战**:
- ⚠️ 迭代优化功能未实现
- ⚠️ 性能有优化空间
- ⚠️ 验证逻辑较简单
- ⚠️ 缺少人工交互

**未来方向**:
- 🎯 实现完整的迭代优化
- 🎯 提升代码生成质量
- 🎯 优化性能和资源使用
- 🎯 增强用户体验

