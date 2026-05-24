import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request


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


def render_issue(text):
    steps = numbered_lines(text)
    actual = extract_after(["结果", "实际结果", "actual"], text)
    expected = extract_after(["期望", "预期", "预期结果", "expected"], text)
    device = extract_after(["机型", "设备", "device"], text)
    system = extract_after(["系统", "OS", "os"], text)
    version = extract_after(["版本", "version"], text)

    output = [
        "# %s" % title_from(text),
        "",
        "## Summary",
        "",
        text.strip().splitlines()[0].strip() if text.strip() else "A bug was reported.",
        "",
        "## Severity",
        "",
        "- %s" % severity(text),
        "",
        "## Environment",
        "",
        "- Device: %s" % (device or "Unknown"),
        "- OS: %s" % (system or "Unknown"),
        "- App version: %s" % (version or "Unknown"),
        "",
        "## Steps To Reproduce",
        "",
    ]
    if steps:
        for index, step in enumerate(steps, 1):
            output.append("%d. %s" % (index, step))
    else:
        output.append("1. Need reporter to provide reproduction steps.")
    output.extend([
        "",
        "## Actual Result",
        "",
        actual or "Need reporter to provide the actual result.",
        "",
        "## Expected Result",
        "",
        expected or "Need reporter to provide the expected result.",
        "",
        "## Useful Clues",
        "",
    ])
    clues = []
    for keyword in ["error", "exception", "route", "not found", "崩溃", "白屏", "接口", "超时"]:
        if keyword.lower() in text.lower():
            clues.append("Mentioned `%s`; check related logs and code paths." % keyword)
    if clues:
        output.extend("- %s" % clue for clue in clues)
    else:
        output.append("- No obvious log keywords detected.")
    output.extend(["", "## Raw Report", "", "```text", text.strip(), "```", ""])
    return "\n".join(output)


def call_ai(raw, draft):
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        raise RuntimeError("AI_API_KEY is not set")
    base_url = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("AI_MODEL", "gpt-4o-mini")
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
    parser.add_argument("--ai", action="store_true", help="Use an OpenAI-compatible model to polish the issue")
    parser.add_argument("--output", help="Write result to a file")
    args = parser.parse_args(argv)
    raw = read_text(args.input)
    draft = render_issue(raw)
    result = call_ai(raw, draft) if args.ai else draft
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(result)
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
