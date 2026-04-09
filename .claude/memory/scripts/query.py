"""
Query the knowledge base using index-guided retrieval.

Uses `claude -p` (subscription) to read index.md + relevant articles
and synthesize an answer. With --file-back, saves the answer as a qa/
article for the compounding loop.

Usage:
    python scripts/query.py "How does Memory Kit work?"
    python scripts/query.py "What patterns do I use for Neo4j?" --file-back
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path

from config import (
    CONCEPTS_DIR,
    CONNECTIONS_DIR,
    INDEX_FILE,
    KNOWLEDGE_DIR,
    LOG_FILE,
    QA_DIR,
    ROOT_DIR,
    now_iso,
)


def slugify(text: str) -> str:
    """Convert text to filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:80]  # max 80 chars


def read_wiki_index() -> str:
    if INDEX_FILE.exists():
        return INDEX_FILE.read_text(encoding="utf-8")
    return "(empty index)"


def build_query_prompt(question: str, file_back: bool) -> str:
    """Build the query prompt for claude -p."""
    wiki_index = read_wiki_index()
    timestamp = now_iso()

    file_back_section = ""
    if file_back:
        slug = slugify(question)
        file_back_section = f"""

## File Back Instructions

After answering, also do the following:

1. Create a Q&A article at {QA_DIR}/{slug}.md with this format:

```markdown
---
title: "Q: {question}"
question: "{question}"
consulted:
  - "concepts/article-1"
  - "concepts/article-2"
filed: {timestamp[:10]}
---

# Q: {question}

## Answer

[Synthesized answer with [[wikilinks]] to sources]

## Sources Consulted

- [[concepts/article-1]] — Why relevant
- [[concepts/article-2]] — Why relevant

## Follow-Up Questions

- [Related question 1]
- [Related question 2]
```

2. Update {INDEX_FILE} — add a new row under the "## Q&A" section:
   ```
   | [[qa/{slug}]] | Short summary of answer | {timestamp[:10]} |
   ```

3. Append to {LOG_FILE}:
   ```
   ## [{timestamp}] query (filed) | {question[:60]}
   - Consulted: [[list of articles read]]
   - Filed to: [[qa/{slug}]]
   ```
"""

    return f"""You are a knowledge base query engine. Answer the user's question by consulting
the wiki in `.claude/memory/knowledge/`.

## How to Answer

1. Read the INDEX below to find relevant articles (3-7 articles typically)
2. Use Read tool to read those articles from {CONCEPTS_DIR} and {CONNECTIONS_DIR}
3. Synthesize a clear, thorough answer
4. Cite sources using [[wikilinks]] (e.g., [[concepts/neo4j-patterns]])
5. If the knowledge base doesn't contain relevant information, say so honestly

## Knowledge Base Index

{wiki_index}

## Question

{question}
{file_back_section}
"""


def run_query(question: str, file_back: bool = False) -> bool:
    """Execute the query via claude -p subprocess."""
    prompt = build_query_prompt(question, file_back)

    # Strip ANTHROPIC_API_KEY to use subscription
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}

    tools = ["Read", "Glob", "Grep"]
    if file_back:
        tools.extend(["Write", "Edit"])

    cmd = [
        "claude",
        "-p", prompt,
        "--allowedTools", ",".join(tools),
        "--output-format", "text",
        "--max-turns", "15",
        "--model", "sonnet",
    ]

    print(f"Question: {question}")
    print(f"File back: {'yes' if file_back else 'no'}")
    print("-" * 60)
    print("Querying knowledge base (this may take 20-40s)...\n")

    try:
        result = subprocess.run(
            cmd,
            capture_output=False,  # stream output directly
            text=True,
            env=env,
            cwd=str(ROOT_DIR),
            timeout=180,
        )

        if result.returncode != 0:
            print(f"\nError: claude -p exited with code {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("\nError: query timed out after 3 minutes")
        return False
    except FileNotFoundError:
        print("\nError: 'claude' command not found. Is Claude Code installed?")
        return False

    if file_back:
        qa_count = len(list(QA_DIR.glob("*.md"))) if QA_DIR.exists() else 0
        print(f"\n{'-' * 60}")
        print(f"Answer filed to knowledge/qa/ ({qa_count} Q&A articles total)")

    return True


def main():
    parser = argparse.ArgumentParser(description="Query the personal knowledge base")
    parser.add_argument("question", help="The question to ask")
    parser.add_argument(
        "--file-back",
        action="store_true",
        help="File the answer back as a Q&A article for compounding loop",
    )
    args = parser.parse_args()

    # Ensure qa/ directory exists
    QA_DIR.mkdir(parents=True, exist_ok=True)

    success = run_query(args.question, file_back=args.file_back)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
