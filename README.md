# Issue Shaper AI

把随手写的 bug 描述、客服反馈、测试日志整理成清晰的 GitHub Issue。

默认使用本地规则提取标题、严重程度、复现步骤、实际结果和补充信息；配置 `AI_API_KEY` 后可以自动补充更自然的描述。

## 快速开始

```bash
python3 -m issue_shaper_ai examples/raw_bug.txt
```

从 stdin 读取：

```bash
cat crash.log | python3 -m issue_shaper_ai -
```

启用 AI 增强：

```bash
export AI_API_KEY="your-key"
python3 -m issue_shaper_ai examples/raw_bug.txt --ai --output ISSUE.md
```

## License

MIT
