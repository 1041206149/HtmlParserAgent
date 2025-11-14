# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-14

### Added
- 初始版本发布
- 4个核心Agent模块：
  - HtmlPreprocessor - HTML预处理
  - VisualUnderstandingAgent - 视觉理解
  - CodeGeneratorAgent - 代码生成
  - ValidationOrchestrator - 验证与迭代
- 工具模块：
  - LLMClient - LLM客户端封装
  - ScreenshotTool - 截图工具
  - HtmlChunker - HTML分块
  - XPathOptimizer - XPath优化
- ParserBuilderWorkflow - 主工作流
- 命令行工具（main.py）
- 配置管理（Settings）
- 测试框架
- 文档：README, USAGE, DEVELOPMENT, QUICK_REFERENCE
- 示例代码

### Features
- 智能HTML预处理和分块
- 基于VLLM的视觉理解
- LLM驱动的代码生成
- 多样本迭代优化
- 字段级评估
- 完整的日志和报告

## [Unreleased]

### Planned
- Web UI界面
- 支持更多LLM模型
- 性能优化
- 分布式处理
- 增量学习

