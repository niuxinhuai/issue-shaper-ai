# 会员页点续费偶现白屏。

## Summary

用户反馈：会员页点续费偶现白屏。

## Severity

- P1 / blocking

## Labels

`bug`, `priority: high`, `area: navigation`, `needs reproduction`

## Environment

- Device: Mate 60
- OS: HarmonyOS 5
- App version: 3.16.8

## Steps To Reproduce

1. 登录老会员账号
2. 进入会员权益页
3. 点击顶部续费提醒

## Actual Result

页面白屏，有时候控制台看到 route not found

## Expected Result

正常进入续费页

## Useful Clues

- Mentioned `route`; check related logs and code paths.
- Mentioned `not found`; check related logs and code paths.
- Mentioned `白屏`; check related logs and code paths.

## Raw Report

```text
用户反馈：会员页点续费偶现白屏。

机型：Mate 60
系统：HarmonyOS 5
版本：3.16.8

步骤：
1. 登录老会员账号
2. 进入会员权益页
3. 点击顶部续费提醒

结果：页面白屏，有时候控制台看到 route not found
期望：正常进入续费页
```

## GitHub CLI

```bash
gh issue create --repo niuxinhuai/example --title '会员页点续费偶现白屏。' --body-file ISSUE.md --label bug --label 'priority: high' --label 'area: navigation' --label 'needs reproduction'
```
