# reddit-intel

Turn Reddit into a competitive intelligence machine — right from your terminal.

reddit-intel is a set of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills that automatically discover how real users talk about problems your product solves, what communities they hang out in, which competitors get mentioned, and what needs remain unmet.

All data accumulates in git-friendly JSONL files. Run today, run next week — it only grows.

---

## How it works

```
/reddit-kw                        /reddit-sub
  Discover pain-point keywords  →   Find relevant subreddits
  from Reddit user language         where your users live
        │                                  │
        └──────────┬───────────────────────┘
                   ▼
             /reddit-fp
               Search tier 1/2 subreddits
               for posts matching keywords
                   │
                   ▼
             /reddit-ac
               Analyze comment sections:
               • Competitor mentions + sentiment
               • Verbatim user quotes (copy material)
               • Unmet needs your product could solve
                   │
                   ▼
         JSONL (data) + Markdown (display)
         ── git tracked, always growing ──
```

4 independent commands. Each is a standalone Claude Code skill — call any one at any time, in any order.

---

## What you get

**keywords.jsonl** — How Reddit users actually phrase their pain:
```json
{"keyword": "context loss", "category": "pain", "reddit_usage": "Claude keeps forgetting my project context", "source": "r/ClaudeAI"}
```

**subreddits.jsonl** — Where to find them, rated by tier:
```json
{"name": "r/ClaudeAI", "tier": 1, "members": "451K", "promo_policy": "discussion OK", "strategy": "Pain-point replies"}
```

**posts.jsonl** — Active discussions about problems you solve:
```json
{"title": "200K context just ain't cutting it", "subreddit": "r/ClaudeAI", "upvotes": 85, "pain_category": "context_loss", "product_solution": "Layered context architecture"}
```

**comments.jsonl** — Competitive intelligence from comment sections:
```json
{"type": "competitor", "content": "I switched to Cursor when hitting token limits", "competitor": "Cursor", "sentiment": "positive", "insight": "Cursor used as fallback"}
{"type": "language", "content": "compacting process straight-up nukes crucial context", "insight": "Users frame compaction as lossy compression"}
{"type": "need", "content": "Need persistent memory across sessions", "insight": "Core unmet need — file-based injection solves this"}
```

Every JSONL file also renders to a Markdown report for human reading.

---

## Prerequisites

1. **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** installed
2. **[Exa](https://exa.ai) MCP server** — required because Reddit blocks Anthropic's default crawler

Add Exa to your Claude Code config (`~/.claude.json` or `.claude/settings.json`):

```json
{
  "mcpServers": {
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": { "EXA_API_KEY": "your-key-from-exa.ai" }
    }
  }
}
```

---

## Installation

```bash
# Clone
git clone https://github.com/SamCuipogobongo/reddit-intel ~/.claude/skills/reddit-intel

# Symlink each command as a standalone skill
for cmd in reddit-intel-init reddit-kw reddit-sub reddit-fp reddit-ac; do
  ln -s ~/.claude/skills/reddit-intel/commands/$cmd ~/.claude/skills/$cmd
done
```

Done. Five slash commands are now available in every Claude Code session.

---

## Quick start

**Step 1** — Initialize in your project:
```
/reddit-intel-init
```
Creates `.reddit-intel.json` + a `product-context.md` template.

**Step 2** — Fill in `product-context.md` with your product's pain points, value props, and target users. See [`examples/trellis/product-context.md`](examples/trellis/product-context.md) for a real example.

**Step 3** — Run:
```
/reddit-kw                 # discover keywords
/reddit-sub                # find communities
/reddit-fp                 # search for posts
/reddit-fp context loss    # ...or focus on a specific topic
/reddit-ac                 # analyze comment sections
```

Each command reads existing data, searches for new entries, deduplicates, appends, and re-renders. Repeat as often as you like.

---

## Repo structure

```
reddit-intel/
├── commands/                          # 5 standalone Claude Code skills
│   ├── reddit-intel-init/SKILL.md     # /reddit-intel-init
│   ├── reddit-kw/SKILL.md            # /reddit-kw
│   ├── reddit-sub/SKILL.md           # /reddit-sub
│   ├── reddit-fp/SKILL.md            # /reddit-fp
│   └── reddit-ac/SKILL.md            # /reddit-ac
├── scripts/
│   └── jsonl_ops.py                   # Shared: append, render, stats, init
├── references/
│   ├── step-details.md                # Detailed search strategies per step
│   ├── product-context.template.md    # English template
│   └── product-context.template.zh.md # Chinese template
├── examples/
│   └── trellis/                       # Real-world example (see below)
├── SKILL.md                           # Full reference (all steps in one doc)
└── LICENSE                            # MIT
```

---

## Configuration

`.reddit-intel.json` — created by `/reddit-intel-init`:

```json
{
  "data_dir": "./reddit-intel/data",
  "product_name": "YourProduct",
  "product_context": "./reddit-intel/product-context.md",
  "language": "en"
}
```

| Field | Description |
|-------|-------------|
| `data_dir` | Where JSONL + Markdown files live |
| `product_name` | Appears in rendered Markdown headers |
| `product_context` | Your filled-in product context file |
| `language` | `en` or `zh` — all output labels adapt |

---

## Real-world example: Trellis

[`examples/trellis/`](examples/trellis/) contains actual data from running reddit-intel for [Trellis](https://github.com/mindfold-ai/Trellis), an open-source AI development framework for Claude Code.

After several weeks of incremental runs:

| Data | Count | What it revealed |
|------|-------|-----------------|
| Keywords | 45 | "context rot", "AI amnesia", "compacting nukes context" — real user language |
| Subreddits | 53 | r/ClaudeAI, r/ClaudeCode, r/ChatGPTCoding as tier 1; r/LocalLLaMA, r/cursor as tier 2 |
| Posts | 44 | context_loss is the #1 pain category; 1M context window didn't solve it |
| Comments | 54 | Cursor, Obsidian vaults, devctx MCP, Ember MCP as competitors; "quality tanks at 250-500K tokens" |

This is the kind of intelligence base that accumulates — each run adds more signal.

---

## License

MIT — Sam Cui, 2026
