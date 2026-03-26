# Global Claude Settings

> This file lives at `~/.claude/CLAUDE.md` and applies to ALL projects.
> Put only personal preferences here — project-specific rules go in project CLAUDE.md.

## Preferences

- **Language:** [Your preferred language for responses]
- **After completing tasks:** update project backlog if active tasks exist
- **Large outputs:** use chunked responses for big files

## Model Selection

- **Architecture, planning, design** — use the most capable model (Opus)
- **Research, exploration** — Sonnet is sufficient
- **Never use** Haiku for any task
- **Second opinion / cross-validation** — use Gemini 3.1 Pro (`gemini-3.1-pro-preview`). Different model family catches blind spots.

## Documentation & Research

When searching for library/API docs:
1. **Context7 first** — `resolve-library-id` -> `query-docs` (structured docs + code snippets)
2. **Web search fallback** — only if Context7 doesn't have the library
3. **WebFetch** — for specific URLs from search results

## Web Fetching — Jina Reader Fallback

When `WebFetch` returns an error (429, permission denied, timeout) — use **Jina Reader** as fallback:

```
WebFetch URL: https://r.jina.ai/{ORIGINAL_URL}
```

Jina Reader converts any web page to clean markdown. Just prepend `https://r.jina.ai/` before the original URL. Works for GitHub, docs, blogs, any public page.

## Claude Code CLI (`claude -p`) Billing

`claude -p` billing depends on environment:
- If `ANTHROPIC_API_KEY` is set -> uses **API credits** (pay-per-use)
- If `ANTHROPIC_API_KEY` is NOT set -> uses **subscription** (Pro/Max, zero incremental cost)

When running `claude -p` in scripts that source `.env` with `ANTHROPIC_API_KEY`:
```python
# Strip API key so claude -p uses subscription
env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
subprocess.run(["claude", "-p", ...], env=env)
```

Key flags:
- `--model sonnet` — cheaper on subscription quota
- `--max-turns N` — limit agent iterations
- `--output-format text|json` — structured output
- `--append-system-prompt "..."` — add system prompt
