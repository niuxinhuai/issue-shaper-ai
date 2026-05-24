import json
import unittest

from issue_shaper_ai.__main__ import github_command_output, github_create_command, issue_data, labels_for


class IssueShaperTest(unittest.TestCase):
    def test_extracts_issue_fields(self):
        raw = """用户反馈：续费白屏
机型：Mate 60
系统：HarmonyOS 5
版本：1.0.0
1. Open page
结果：route not found
期望：open renewal page
"""
        data = issue_data(raw)
        self.assertEqual(data["environment"]["device"], "Mate 60")
        self.assertIn("area: navigation", data["labels"])
        self.assertEqual(json.loads(json.dumps(data))["severity"], "P1 / blocking")

    def test_labels_for_api(self):
        self.assertIn("area: api", labels_for("接口超时"))

    def test_github_create_command_quotes_title_and_labels(self):
        data = issue_data("用户反馈：续费白屏\n结果：route not found")
        command = github_create_command("owner/repo", data)
        self.assertIn("gh issue create --repo owner/repo", command)
        self.assertIn("--label bug", command)
        self.assertIn("--body-file ISSUE.md", command)

    def test_github_command_output_returns_script_only(self):
        output = github_command_output("owner/repo", "用户反馈：续费白屏")
        self.assertTrue(output.startswith("gh issue create"))
        self.assertNotIn("```", output)


if __name__ == "__main__":
    unittest.main()
