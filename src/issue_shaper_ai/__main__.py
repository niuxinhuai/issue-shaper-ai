import argparse
import json
import os
import re
import shlex
import sys
import urllib.error
import urllib.request

from . import __version__


def read_text(path):
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def extract_after(labels, text):
    for label in labels:
        match = re.search(r"(?im)^%s[:：]\s*(.+)$" % re.escape(label), text)
        if match:
            return match.group(1).strip()
    return ""


def severity(text):
    lowered = text.lower()
    if any(word in lowered for word in ["crash", "崩溃", "闪退", "panic", "fatal"]):
        return "P0 / crash"
    if any(word in lowered for word in ["白屏", "无法", "not found", "blocked", "阻塞"]):
        return "P1 / blocking"
    if any(word in lowered for word in ["偶现", "偶发", "sometimes", "flaky"]):
        return "P2 / intermittent"
    return "P3 / normal"


def labels_for(text):
    labels = ["bug"]
    lowered = text.lower()
    if any(word in lowered for word in ["crash", "崩溃", "闪退", "白屏", "blocked", "阻塞"]):
        labels.append("priority: high")
    if any(word in lowered for word in ["route", "not found", "跳转", "路由"]):
        labels.append("area: navigation")
    if any(word in lowered for word in ["接口", "api", "timeout", "超时", "网络"]):
        labels.append("area: api")
    if any(word in lowered for word in ["偶现", "偶发", "flaky", "sometimes"]):
        labels.append("needs reproduction")
    return labels


def numbered_lines(text):
    items = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^\d+[.)]\s+", stripped):
            items.append(re.sub(r"^\d+[.)]\s+", "", stripped))
    return items


def title_from(text):
    first = next((line.strip() for line in text.splitlines() if line.strip()), "Bug report")
    first = re.sub(r"^(用户反馈|问题|bug|BUG)[:：]\s*", "", first)
    return first[:80]


def issue_data(text):
    steps = numbered_lines(text)
    clues = []
    for keyword in ["error", "exception", "route", "not found", "崩溃", "白屏", "接口", "超时"]:
        if keyword.lower() in text.lower():
            clues.append("Mentioned `%s`; check related logs and code paths." % keyword)
    return {
        "title": title_from(text),
        "summary": text.strip().splitlines()[0].strip() if text.strip() else "A bug was reported.",
        "severity": severity(text),
        "labels": labels_for(text),
        "environment": {
            "device": extract_after(["机型", "设备", "device"], text) or "Unknown",
            "os": extract_after(["系统", "OS", "os"], text) or "Unknown",
            "app_version": extract_after(["版本", "version"], text) or "Unknown",
        },
        "steps_to_reproduce": steps or ["Need reporter to provide reproduction steps."],
        "actual_result": extract_after(["结果", "实际结果", "actual"], text) or "Need reporter to provide the actual result.",
        "expected_result": extract_after(["期望", "预期", "预期结果", "expected"], text) or "Need reporter to provide the expected result.",
        "useful_clues": clues or ["No obvious log keywords detected."],
        "raw_report": text.strip(),
    }


def github_create_command(repository, data, body_file="ISSUE.md"):
    parts = [
        "gh", "issue", "create",
        "--repo", repository,
        "--title", data["title"],
        "--body-file", body_file,
    ]
    for label in data.get("labels", []):
        parts.extend(["--label", label])
    return " ".join(shlex.quote(part) for part in parts)


def render_issue(text):
    data = issue_data(text)
    output = [
        "# %s" % data["title"],
        "",
        "## Summary",
        "",
        data["summary"],
        "",
        "## Severity",
        "",
        "- %s" % data["severity"],
        "",
        "## Labels",
        "",
        ", ".join("`%s`" % item for item in data["labels"]),
        "",
        "## Environment",
        "",
        "- Device: %s" % data["environment"]["device"],
        "- OS: %s" % data["environment"]["os"],
        "- App version: %s" % data["environment"]["app_version"],
        "",
        "## Steps To Reproduce",
        "",
    ]
    for index, step in enumerate(data["steps_to_reproduce"], 1):
        output.append("%d. %s" % (index, step))
    output.extend([
        "",
        "## Actual Result",
        "",
        data["actual_result"],
        "",
        "## Expected Result",
        "",
        data["expected_result"],
        "",
        "## Useful Clues",
        "",
    ])
    output.extend("- %s" % clue for clue in data["useful_clues"])
    output.extend(["", "## Raw Report", "", "```text", data["raw_report"], "```", ""])
    return "\n".join(output)


def call_ai(raw, draft, model=None, base_url=None):
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        raise RuntimeError("AI_API_KEY is not set")
    base_url = (base_url or os.getenv("AI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
    model = model or os.getenv("AI_MODEL", "gpt-4o-mini")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Return only a GitHub issue in Markdown."},
            {"role": "user", "content": "Polish this rough bug report into a precise issue. Do not invent facts.\n\nRAW:\n%s\n\nDRAFT:\n%s" % (raw[:12000], draft[:8000])},
        ],
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError("AI request failed: %s" % exc)
    return body["choices"][0]["message"]["content"].strip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Turn rough bug text into a GitHub issue.")
    parser.add_argument("input", help="Input file, or '-' for stdin")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--github-url", help="Print a gh issue create command for owner/repo")
    parser.add_argument("--ai", action="store_true", help="Use an OpenAI-compatible model to polish the issue")
    parser.add_argument("--model", help="Override AI_MODEL for --ai")
    parser.add_argument("--base-url", help="Override AI_BASE_URL for --ai")
    parser.add_argument("--output", help="Write result to a file")
    parser.add_argument("--version", action="version", version="issue-shaper-ai %s" % __version__)
    args = parser.parse_args(argv)
    raw = read_text(args.input)
    if args.format == "json":
        draft = json.dumps(issue_data(raw), ensure_ascii=False, indent=2) + "\n"
    else:
        draft = render_issue(raw)
    result = call_ai(raw, draft, args.model, args.base_url) if args.ai else draft
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(result)
    else:
        sys.stdout.write(result)
    if args.github_url:
        data = issue_data(raw)
        sys.stdout.write("\n## GitHub CLI\n\n```bash\n%s\n```\n" % github_create_command(args.github_url, data))


if __name__ == "__main__":
    main()
