# Issue Shaper AI

[![CI](https://github.com/niuxinhuai/issue-shaper-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/niuxinhuai/issue-shaper-ai/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

[中文文档](README.zh-CN.md)

Turn rough bug reports, customer feedback, and logs into clean GitHub issues.

Issue Shaper AI works without a model by extracting known fields and producing a structured issue. With `AI_API_KEY`, it can polish the draft without inventing missing facts.

## Features

- Extracts title, summary, severity, environment, reproduction steps, actual result, and expected result.
- Infers useful labels such as `bug`, `priority: high`, `area: navigation`, and `needs reproduction`.
- Can print a ready-to-run `gh issue create` command.
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
issue-shaper-ai examples/raw_bug.txt --github-url owner/repo
issue-shaper-ai examples/raw_bug.txt --format json
cat crash.log | issue-shaper-ai -
```

See generated examples in [`examples/output.md`](examples/output.md) and [`examples/output.json`](examples/output.json).

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

## Release

Tagged releases build Python packages and create a GitHub Release through GitHub Actions. PyPI publishing is disabled by default; to enable it, configure PyPI Trusted Publishing for this repository and set the repository variable , then push a tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

## License

MIT
