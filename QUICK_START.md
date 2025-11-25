# 🚀 快速开始指南

## 安装依赖

```bash
# 确保已安装所有依赖
pip install -r requirements.txt

# 检查是否需要更新
pip list | grep -E "langchain|openai|beautifulsoup"
```

## 配置环境变量

```bash
# 创建 .env 文件或设置环境变量
export OPENAI_API_KEY="sk-your-key-here"
export OPENAI_API_BASE="https://api.openai.com/v1"  # 或使用自定义基地址
```

## 准备URL列表

创建 `urls.txt` 文件：

```
https://example.com/article1
https://example.com/article2
https://example.com/article3
https://example.com/article4
https://example.com/article5
```

## 运行迭代流程

### 方式1：命令行（推荐）

```bash
# 基础运行
python main.py -f urls.txt

# 完整参数
python main.py \
  -f urls.txt \
  -o output/my_project \
  -t article \
  -d example.com

# 监控日志
tail -f logs/agent_*.log
```

### 方式2：Python脚本

```python
from agent import ParserAgent

agent = ParserAgent(output_dir="output/test")

result = agent.run_iterations(
    urls=[
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
    ],
    domain="example.com",
    layout_type="article",
    max_iterations=3,
    accuracy_threshold=0.85
)

print(f"✓ 总轮次: {result['total_rounds']}")
print(f"✓ 最终准确率: {result['overall_accuracy']:.2%}")
print(f"✓ Parser路径: {result['final_parser_path']}")
```

## 查看结果

### 输出文件

```bash
# 查看生成的Parser
cat output/parsers/generated_parser_v1.py

# 查看Schema演变
cat output/parsers/schema_v1.json
cat output/parsers/schema_v2.json
cat output/parsers/schema_v3.json

# 查看截图
open output/screenshots/round_1_sample_1.png

# 查看groundtruth
cat output/groundtruth/12345678.json
```

### 性能指标

```bash
# 查看日志中的准确率
grep "总体准确率\|整体准确率" logs/agent_*.log

# 查看迭代次数
grep "迭代轮次" logs/agent_*.log
```

## 使用生成的Parser

生成的Parser可以独立使用：

```python
import sys
sys.path.insert(0, 'output/parsers')

from generated_parser_v3 import WebPageParser

parser = WebPageParser()

# 从URL解析
import requests
from urllib.parse import urlparse

url = "https://example.com/article"
response = requests.get(url)
result = parser.parse(response.text)

print(result)
# 输出:
# {
#     "title": "...",
#     "date": "...",
#     "content": "...",
#     ...
# }
```

## 常见参数调整

### 提高准确率

```python
# 增加迭代次数
result = agent.run_iterations(
    urls=urls,
    max_iterations=5  # 从3增加到5
)
```

### 加快速度

```python
# 降低准确率阈值
result = agent.run_iterations(
    urls=urls,
    accuracy_threshold=0.75  # 从0.85降低到0.75
)
```

### 只处理部分URL

```python
# 选择前N个URL
result = agent.run_iterations(
    urls=urls[:5],  # 只处理前5个
)
```

## 故障排除

### 问题：API连接失败

```
错误: Failed to connect to OpenAI API

解决:
1. 检查网络连接
2. 检查 OPENAI_API_KEY 是否正确
3. 检查 OPENAI_API_BASE 是否正确
4. 查看详细错误: tail logs/agent_*.log
```

### 问题：内存不足

```
错误: MemoryError

解决:
1. 减少URL数量
2. 降低 max_iterations
3. 检查是否有僵尸进程: ps aux | grep python
```

### 问题：截图失败

```
错误: Screenshot failed

解决:
1. 检查URL是否有效
2. 检查网络连接
3. 尝试手动访问URL
4. 查看 output/screenshots/ 中是否有部分截图
```

## 下一步

- 📖 阅读 [ITERATION_WORKFLOW.md](./ITERATION_WORKFLOW.md) 了解详细的工作流程
- 📖 阅读 [NEW_FLOW_GUIDE.md](./NEW_FLOW_GUIDE.md) 了解新流程的改进
- 🔧 编辑 `config/settings.py` 调整配置
- 🧪 运行 `python test_new_flow.py` 进行测试

## 获取帮助

1. 查看日志文件：`logs/agent_*.log`
2. 检查输出文件：`output/` 目录
3. 查看代码注释：`agent/` 和 `tools/` 目录

---

**提示**：第一次运行可能会较慢，因为需要初始化各种工具和LLM调用。后续轮次会因为基于前一轮优化而更快。

