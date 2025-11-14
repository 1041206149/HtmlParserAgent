#!/bin/bash

# HtmlParserAgent 快速启动脚本

echo "=================================="
echo "HtmlParserAgent 项目初始化"
echo "=================================="

# 检查Python版本
echo "检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python版本: $python_version"

# 创建虚拟环境（可选）
read -p "是否创建虚拟环境? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ 虚拟环境已激活"
fi

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt
echo "✓ Python依赖安装完成"

# 安装Playwright
echo "安装Playwright浏览器..."
playwright install chromium
echo "✓ Playwright安装完成"

# 配置环境变量
if [ ! -f .env ]; then
    echo "配置环境变量..."
    cp .env.example .env
    echo "⚠ 请编辑 .env 文件，填入你的API配置"
    echo "  主要配置项："
    echo "  - OPENAI_API_KEY"
    echo "  - OPENAI_API_BASE"
    echo "  - OPENAI_MODEL"
else
    echo "✓ .env 文件已存在"
fi

# 创建必要的目录
echo "创建目录结构..."
mkdir -p outputs logs
echo "✓ 目录创建完成"

echo ""
echo "=================================="
echo "初始化完成！"
echo "=================================="
echo ""
echo "下一步："
echo "1. 编辑 .env 文件，配置API密钥"
echo "2. 运行测试: pytest tests/ -v"
echo "3. 运行示例: python main.py --url 'https://stackoverflow.blog/2025/10/15/secure-coding-in-javascript/' --output ./outputs/test"
echo ""
echo "更多信息请查看："
echo "- README.md - 项目介绍"
echo "- USAGE.md - 使用文档"
echo "- DEVELOPMENT.md - 开发文档"
echo ""

