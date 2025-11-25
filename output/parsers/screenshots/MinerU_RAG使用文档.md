# MinerU RAG 用户使用文档

## 📦 安装

### 基础安装

```bash
pip install mineru-rag
```

### 完整安装（包含RAG功能）

如果需要使用RAG知识库和LLM功能，需要安装完整版本：

```bash
pip install mineru-rag[rag]
```

### 验证安装

```python
python -c "from mineru_rag import MinerUClient, RAGBuilder, LLMClient; print('✅ 安装成功')"
```

## ⚙️ 配置

### 方式一：环境变量（推荐）

#### Windows PowerShell

```powershell
# MinerU API Token（在线模式需要）
$env:MINERU_API_TOKEN="your-mineru-api-token"

# LLM API配置（RAG功能需要）
$env:OPENAI_API_KEY="your-openai-api-key"
$env:OPENAI_BASE_URL="http://your-api-server/v1/"
$env:OPENAI_MODEL="gpt-3.5-turbo"
$env:OPENAI_TEMPERATURE="0.7"
```

#### Windows CMD

```cmd
set MINERU_API_TOKEN=your-mineru-api-token
set OPENAI_API_KEY=your-openai-api-key
set OPENAI_BASE_URL=http://your-api-server/v1/
set OPENAI_MODEL=gpt-3.5-turbo
set OPENAI_TEMPERATURE=0.7
```

#### Linux/Mac

```bash
export MINERU_API_TOKEN="your-mineru-api-token"
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_BASE_URL="http://your-api-server/v1/"
export OPENAI_MODEL="gpt-3.5-turbo"
export OPENAI_TEMPERATURE="0.7"
```

### 方式二：代码中直接传入

```python
from mineru_rag import MinerUClient, LLMClient

# 直接传入参数
client = MinerUClient(api_token="your-token")
llm = LLMClient(
    api_key="your-key",
    base_url="http://your-api-server/v1/"
)
```

## 🚀 使用场景

### 场景一：使用在线MinerU API处理文档

```python
from mineru_rag import MinerUClient

# 初始化客户端（会自动读取 MINERU_API_TOKEN 环境变量）
client = MinerUClient()

# 处理单个PDF文件
result = client.process_file(
    input_path="document.pdf",
    output_path="./output"
)

if result['success']:
    print(f"✅ 处理成功！")
    print(f"📄 Markdown文件: {result['md_file']}")
    print(f"📁 输出目录: {result['output_path']}")
else:
    print(f"❌ 处理失败: {result['error']}")

# 批量处理多个文件
pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
results = client.process_files_batch(
    file_paths=pdf_files,
    output_dir="./output"
)

print(f"处理完成: {results['success_count']}/{results['total_count']} 成功")
```

### 场景二：使用本地MinerU vLLM后端

```python
from mineru_rag import MinerUClient

# 确保本地MinerU vLLM后端正在运行
# 启动命令示例：mineru vllm-server --port 30000

# 初始化本地模式客户端
client = MinerUClient(
    use_local=True,
    local_url="http://127.0.0.1:30000"  # 本地后端地址
)

# 使用方式与在线模式完全相同
result = client.process_file(
    input_path="document.pdf",
    output_path="./output"
)

if result['success']:
    print(f"✅ 处理成功: {result['md_file']}")
```

### 场景三：构建RAG知识库

```python
from mineru_rag import RAGBuilder
from pathlib import Path

# 初始化RAG构建器
rag = RAGBuilder()

# 从处理后的Markdown文件构建知识库
markdown_files = [
    Path("./output/doc1/full.md"),
    Path("./output/doc2/full.md"),
    Path("./output/doc3/full.md")
]

# 构建向量数据库
rag.build_from_files(
    file_paths=markdown_files,
    library_id="my_papers"  # 知识库ID
)

print("✅ RAG知识库构建完成！")

# 加载已存在的知识库
rag.load_vector_store(library_id="my_papers")
```

### 场景四：查询RAG知识库（仅检索）

```python
from mineru_rag import RAGBuilder

# 初始化RAG构建器并加载知识库
rag = RAGBuilder()
rag.load_vector_store(library_id="my_papers")

# 查询知识库（只检索，不调用LLM）
rag_result = rag.query(
    question="这篇论文的主要贡献是什么？",
    k=4  # 检索4个最相关的文档片段
)

print(f"检索到 {rag_result['num_sources']} 个相关片段")
for i, source in enumerate(rag_result['sources'], 1):
    print(f"{i}. {source['filename']} (片段 {source['chunk_index']+1})")
    print(f"   预览: {source['content_preview']}")
```

### 场景五：使用LLM进行智能问答

```python
from mineru_rag import RAGBuilder, LLMClient

# 初始化LLM客户端（会自动读取环境变量）
llm = LLMClient()

# 加载RAG知识库
rag = RAGBuilder()
rag.load_vector_store(library_id="my_papers")

# 查询并生成答案
rag_result = rag.query("这篇论文的主要贡献是什么？", k=4)
answer = llm.query_with_rag(rag_result)

print(f"❓ 问题: {answer['question']}")
print(f"\n💡 回答:\n{answer['answer']}")
print(f"\n📚 来源 ({answer['num_sources']} 个):")
for i, source in enumerate(answer['sources'], 1):
    print(f"  {i}. {source['filename']} (片段 {source['chunk_index']+1})")
```

### 场景六：完整工作流（从文档处理到智能问答）

```python
from mineru_rag import MinerUClient, RAGBuilder, LLMClient
from pathlib import Path
import os

# 1️⃣ 处理PDF文档
print("步骤1: 处理PDF文档...")
client = MinerUClient()  # 使用在线API
result = client.process_file("paper.pdf", "./output")

if not result['success']:
    print(f"❌ 处理失败: {result['error']}")
    exit(1)

print(f"✅ 处理成功: {result['md_file']}")

# 2️⃣ 构建RAG知识库
print("\n步骤2: 构建RAG知识库...")
rag = RAGBuilder()
md_file = Path(result['md_file'])
rag.build_from_files([md_file], library_id="papers")
print("✅ 知识库构建完成")

# 3️⃣ 智能问答
print("\n步骤3: 智能问答...")
llm = LLMClient()
rag.load_vector_store("papers")

# 可以问多个问题
questions = [
    "这篇论文的主要贡献是什么？",
    "论文中提到了哪些关键技术？",
    "实验结果显示什么？"
]

for question in questions:
    print(f"\n{'='*60}")
    print(f"❓ 问题: {question}")
    print('='*60)
    
    rag_result = rag.query(question, k=4)
    answer = llm.query_with_rag(rag_result)
    
    print(f"\n💡 回答:\n{answer['answer']}")
    print(f"\n📚 参考来源:")
    for i, source in enumerate(answer['sources'], 1):
        print(f"  {i}. {source['filename']} (片段 {source['chunk_index']+1})")
```

## 💻 命令行使用

### 处理文档

```bash
# 在线模式
mineru-rag process document.pdf -o ./output

# 本地模式
mineru-rag process document.pdf -o ./output --local --local-url http://127.0.0.1:30000

# 指定API Token
mineru-rag process document.pdf -o ./output --api-token your-token
```

### 构建RAG知识库

```bash
# 从多个Markdown文件构建
mineru-rag build doc1.md doc2.md doc3.md -l my_library

# 指定输出路径
mineru-rag build doc1.md doc2.md -l my_library -o ./vector_db
```

### 查询知识库

```bash
# 基本查询
mineru-rag query "这篇论文的主要贡献是什么？" -l my_library

# 指定检索数量
mineru-rag query "关键技术有哪些？" -l my_library -k 6

# 限制在特定文件
mineru-rag query "实验方法是什么？" -l my_library --file-id paper1
```

## 📝 完整示例脚本

创建一个 `example.py` 文件：

```python
#!/usr/bin/env python3
"""
MinerU RAG 完整使用示例
"""

import os
from pathlib import Path
from mineru_rag import MinerUClient, RAGBuilder, LLMClient

def main():
    # 检查环境变量
    if not os.environ.get("MINERU_API_TOKEN"):
        print("⚠️  请设置 MINERU_API_TOKEN 环境变量")
        print("   Windows: $env:MINERU_API_TOKEN='your-token'")
        print("   Linux/Mac: export MINERU_API_TOKEN='your-token'")
        return
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  请设置 OPENAI_API_KEY 环境变量（RAG功能需要）")
        return
    
    if not os.environ.get("OPENAI_BASE_URL"):
        print("⚠️  请设置 OPENAI_BASE_URL 环境变量（RAG功能需要）")
        return
    
    print("=" * 60)
    print("MinerU RAG 完整使用示例")
    print("=" * 60)
    
    # 步骤1: 处理文档
    print("\n[1/3] 处理PDF文档...")
    client = MinerUClient()
    
    # 假设有一个paper.pdf文件
    pdf_file = "paper.pdf"
    if not Path(pdf_file).exists():
        print(f"⚠️  文件不存在: {pdf_file}")
        print("   请将PDF文件放在当前目录，或修改pdf_file变量")
        return
    
    result = client.process_file(pdf_file, "./output")
    
    if not result['success']:
        print(f"❌ 处理失败: {result['error']}")
        return
    
    print(f"✅ 处理成功: {result['md_file']}")
    
    # 步骤2: 构建RAG知识库
    print("\n[2/3] 构建RAG知识库...")
    rag = RAGBuilder()
    md_file = Path(result['md_file'])
    
    try:
        rag.build_from_files([md_file], library_id="demo")
        print("✅ 知识库构建完成")
    except Exception as e:
        print(f"❌ 构建失败: {str(e)}")
        return
    
    # 步骤3: 智能问答
    print("\n[3/3] 智能问答...")
    llm = LLMClient()
    rag.load_vector_store("demo")
    
    questions = [
        "这篇论文的主要贡献是什么？",
        "论文中提到了哪些关键技术？"
    ]
    
    for question in questions:
        print(f"\n{'='*60}")
        print(f"❓ 问题: {question}")
        print('='*60)
        
        try:
            rag_result = rag.query(question, k=4)
            answer = llm.query_with_rag(rag_result)
            
            print(f"\n💡 回答:\n{answer['answer']}")
            print(f"\n📚 参考来源 ({answer['num_sources']} 个):")
            for i, source in enumerate(answer['sources'], 1):
                print(f"  {i}. {source['filename']} (片段 {source['chunk_index']+1})")
        except Exception as e:
            print(f"❌ 查询失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ 示例完成！")

if __name__ == "__main__":
    main()
```

运行示例：
```bash
python example.py
```

## 🔍 API 参考

### MinerUClient

#### 初始化

```python
# 在线模式（使用API Token）
client = MinerUClient(api_token="your-token")

# 本地模式（使用vLLM后端）
client = MinerUClient(use_local=True, local_url="http://127.0.0.1:30000")
```

#### 方法

- `process_file(input_path, output_path, ...)` - 处理单个文件
  - `input_path`: 输入文件路径（PDF, PNG, JPG等）
  - `output_path`: 输出目录
  - `is_ocr`: 是否启用OCR（默认True）
  - `enable_formula`: 是否启用公式识别（默认True）
  - `enable_table`: 是否启用表格识别（默认True）
  - `language`: 文档语言（默认"en"）
  - `layout_model`: 布局模型（默认"doclayout_yolo"）

- `process_files_batch(file_paths, output_dir, ...)` - 批量处理文件
  - `file_paths`: 文件路径列表
  - `output_dir`: 输出目录
  - 其他参数同 `process_file`

### RAGBuilder

#### 初始化

```python
rag = RAGBuilder(
    vector_store_path=None,  # 向量数据库存储路径（默认：~/.mineru_rag/vector_db）
    embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
```

#### 方法

- `build_from_files(file_paths, library_id, metadata)` - 构建向量数据库
  - `file_paths`: Markdown文件路径列表
  - `library_id`: 知识库ID（默认"default"）
  - `metadata`: 可选的元数据字典

- `load_vector_store(library_id)` - 加载已存在的向量数据库
  - `library_id`: 知识库ID

- `query(question, k, file_id)` - 查询知识库
  - `question`: 查询问题
  - `k`: 检索文档数量（默认4）
  - `file_id`: 可选，限制在特定文件

### LLMClient

#### 初始化

```python
llm = LLMClient(
    api_key=None,  # LLM API密钥（默认从OPENAI_API_KEY环境变量读取）
    base_url=None,  # LLM API地址（默认从OPENAI_BASE_URL环境变量读取）
    model=None,  # 模型名称（默认从OPENAI_MODEL环境变量读取或"gpt-3.5-turbo"）
    temperature=0.7  # 温度参数
)
```

#### 方法

- `query(question, context)` - 直接查询LLM
  - `question`: 问题
  - `context`: 上下文内容

- `query_with_rag(rag_result)` - 使用RAG结果查询LLM
  - `rag_result`: RAGBuilder.query()的返回结果

## 🔍 常见问题

### Q1: 如何检查环境变量是否设置成功？

**Python代码中检查：**
```python
import os

print("MINERU_API_TOKEN:", "✅ 已设置" if os.environ.get("MINERU_API_TOKEN") else "❌ 未设置")
print("OPENAI_API_KEY:", "✅ 已设置" if os.environ.get("OPENAI_API_KEY") else "❌ 未设置")
print("OPENAI_BASE_URL:", "✅ 已设置" if os.environ.get("OPENAI_BASE_URL") else "❌ 未设置")
```

**命令行检查：**
```bash
# Windows PowerShell
echo $env:MINERU_API_TOKEN
echo $env:OPENAI_API_KEY

# Linux/Mac
echo $MINERU_API_TOKEN
echo $OPENAI_API_KEY
```

### Q2: 本地模式需要什么？

1. 安装MinerU
2. 启动vLLM后端：
```bash
# 确保MinerU vLLM后端在运行
mineru vllm-server --port 30000
```

3. 在代码中使用：
```python
client = MinerUClient(use_local=True, local_url="http://127.0.0.1:30000")
```

### Q3: 如何批量处理多个PDF？

```python
from pathlib import Path
from mineru_rag import MinerUClient

client = MinerUClient()

# 获取目录下所有PDF
pdf_dir = Path("./pdfs")
pdf_files = list(pdf_dir.glob("*.pdf"))

# 批量处理
results = client.process_files_batch(
    file_paths=pdf_files,
    output_dir="./output"
)

print(f"成功: {results['success_count']}/{results['total_count']}")
```

### Q4: 如何只查询特定文档？

```python
rag = RAGBuilder()
rag.load_vector_store("my_library")

# 查询特定文件（需要知道file_id）
rag_result = rag.query(
    question="问题",
    k=4,
    file_id="paper1"  # 限制在这个文件
)
```

### Q5: 向量数据库存储在哪里？

默认位置：`~/.mineru_rag/vector_db/`

可以自定义：
```python
rag = RAGBuilder(vector_store_path="./my_vector_db")
```

### Q6: 安装RAG功能时出错？

确保安装了完整版本：
```bash
pip install mineru-rag[rag]
```

如果仍有问题，可能需要单独安装依赖：
```bash
pip install langchain langchain-openai langchain-community faiss-cpu sentence-transformers
```

### Q7: 如何处理中文文档？

```python
client = MinerUClient()
result = client.process_file(
    input_path="chinese_doc.pdf",
    output_path="./output",
    language="ch"  # 设置为中文
)
```

### Q8: 如何自定义嵌入模型？

```python
rag = RAGBuilder(
    embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
```

## 📚 更多资源

- **PyPI页面**: https://pypi.org/project/mineru-rag/

## 💡 使用提示

1. **首次使用**：建议先处理一个简单的PDF文件测试
2. **环境变量**：推荐使用环境变量配置，避免在代码中硬编码敏感信息
3. **本地模式**：使用本地vLLM后端需要先启动MinerU服务
4. **RAG功能**：需要安装 `mineru-rag[rag]` 才能使用RAG相关功能
5. **向量数据库**：构建一次后可以重复使用，无需每次都重新构建
6. **批量处理**：大量文件建议分批处理，避免超时

## 🆘 获取帮助

如果遇到问题：

1. 检查环境变量是否正确设置
2. 确认已安装所需依赖
3. 查看错误信息中的详细提示
4. 在GitHub Issues中搜索类似问题
5. 提交新的Issue并附上错误信息

