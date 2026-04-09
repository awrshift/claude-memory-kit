# Contributing to Claude Memory Kit

Thank you for your interest in contributing. This project is an OSS starter kit for Claude Code, focused on persistent memory and structured context management.

## Ways to contribute

- **Report a bug** — open an issue with steps to reproduce
- **Propose a feature** — open an issue describing the use case before writing code
- **Improve docs** — PRs for README, CLAUDE.md, or the `/tour` skill are welcome
- **Share a pattern** — open a discussion if you've found a memory or rules pattern that works well

## Pull requests

- Keep PRs focused. One feature or fix per PR.
- Match the existing style (pure Markdown, zero dependencies, stdlib-only Python).
- Test scripts locally before pushing: `python3 .claude/memory/scripts/lint.py` on your changes.
- If you change behavior, update `CHANGELOG.md` and mention the change in the PR description.

## Ground rules

- **Zero dependencies.** Scripts use Python stdlib only. No `pip install`. No external services beyond `claude -p` subprocess.
- **Pure Markdown for content.** Keep the wiki and memory plain `.md` so any editor works.
- **Obsidian remains optional.** Don't add features that require Obsidian to be installed.
- **Be kind in issues and PRs.** Assume good intent.

## License

By contributing, you agree that your contributions will be licensed under the MIT License (see [LICENSE](LICENSE)).
