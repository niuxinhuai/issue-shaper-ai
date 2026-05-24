# Issue Shaper AI

[![CI](https://github.com/niuxinhuai/issue-shaper-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/niuxinhuai/issue-shaper-ai/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

[English](README.md)

把粗糙 bug 描述、客服反馈、测试日志整理成清晰的 GitHub Issue。

Issue Shaper AI 不配置模型也能用规则提取字段并生成结构化 issue；配置 `AI_API_KEY` 后，可以在不编造事实的前提下做润色。

## 功能

- 提取标题、摘要、严重程度、环境、复现步骤、实际结果、预期结果
- 自动推断 `bug`、`priority: high`、`area: navigation`、`needs reproduction` 等标签
- 可输出可直接执行的 `gh issue create` 命令
- 支持 Markdown 和 JSON 输出
- 支持从文件或 stdin 读取
- 可选 AI 润色，兼容 OpenAI-compatible 接口

## 安装

```bash
python3 -m pip install -e .
```

## 使用

```bash
issue-shaper-ai examples/raw_bug.txt
issue-shaper-ai examples/raw_bug.txt --github-url owner/repo
issue-shaper-ai examples/raw_bug.txt --format json
cat crash.log | issue-shaper-ai -
```

可以直接查看生成示例：[`examples/output.md`](examples/output.md) 和 [`examples/output.json`](examples/output.json)。

启用 AI 润色：

```bash
export AI_API_KEY="your-key"
issue-shaper-ai examples/raw_bug.txt --ai --output ISSUE.md
```

## 开发

```bash
python3 -m pip install -e .
python3 -m unittest discover -s tests
```

## License

MIT
