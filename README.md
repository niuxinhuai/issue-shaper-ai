# Issue Shaper AI

[中文文档](README.zh-CN.md)

Turn rough bug reports, customer feedback, and logs into clean GitHub issues.

Issue Shaper AI works without a model by extracting known fields and producing a structured issue. With `AI_API_KEY`, it can polish the draft without inventing missing facts.

## Features

- Extracts title, summary, severity, environment, reproduction steps, actual result, and expected result.
- Infers useful labels such as `bug`, `priority: high`, `area: navigation`, and `needs reproduction`.
- Supports Markdown and JSON output.
- Reads from files or stdin.
- Optional AI polishing through OpenAI-compatible APIs.

## Install

```bash
python3 -m pip install -e .
```

## Usage

```bash
issue-shaper-ai examples/raw_bug.txt
issue-shaper-ai examples/raw_bug.txt --format json
cat crash.log | issue-shaper-ai -
```

Use AI polishing:

```bash
export AI_API_KEY="your-key"
issue-shaper-ai examples/raw_bug.txt --ai --output ISSUE.md
```

## Development

```bash
python3 -m pip install -e .
python3 -m unittest discover -s tests
```

## License

MIT
