# reddit-intel

A set of Claude Code skills for Reddit competitive intelligence. Discover how your target users describe their pain points, find relevant communities, track posts with real complaints, and extract competitor mentions and unmet needs — all in incrementally-growing JSONL files.

Works for any product. Trellis is included as a real-world example.

---

## What it does

4 independent commands, each a standalone Claude Code skill:

| Command | What it does |
|---------|-------------|
| `/reddit-kw` | Discover how Reddit users describe pain points in your domain |
| `/reddit-sub` | Find subreddits where your target users live |
| `/reddit-fp` | Search for posts with pain points matching your product |
| `/reddit-ac` | Extract competitor mentions, user language, unmet needs from comments |

Plus `/reddit-intel-init` for first-time setup.

Each command is idempotent and incremental. Run it today, run it again next week — data only grows, never overwrites. All output is stored as JSONL (queryable data) and rendered to Markdown (human-readable).

---

## Prerequisites

**Claude Code** with the **Exa MCP server** configured.

Exa is required because Reddit blocks Anthropic's default web crawler.

Add Exa MCP to your `~/.claude.json` or project `.claude/settings.json`:

```json
{
  "mcpServers": {
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": {
        "EXA_API_KEY": "your-exa-api-key"
      }
    }
  }
}
```

Get an Exa API key at [exa.ai](https://exa.ai).

---

## Installation

Clone the repo and symlink each command into your Claude Code skills directory:

```bash
git clone https://github.com/SamCuipogobongo/reddit-intel ~/.claude/skills/reddit-intel

# Symlink each command as a separate skill
ln -s ~/.claude/skills/reddit-intel/commands/reddit-intel-init ~/.claude/skills/reddit-intel-init
ln -s ~/.claude/skills/reddit-intel/commands/reddit-kw ~/.claude/skills/reddit-kw
ln -s ~/.claude/skills/reddit-intel/commands/reddit-sub ~/.claude/skills/reddit-sub
ln -s ~/.claude/skills/reddit-intel/commands/reddit-fp ~/.claude/skills/reddit-fp
ln -s ~/.claude/skills/reddit-intel/commands/reddit-ac ~/.claude/skills/reddit-ac
```

After this, all 5 commands are available in any Claude Code session:
- `/reddit-intel-init` — First-time setup
- `/reddit-kw` — Expand keywords
- `/reddit-sub` — Discover subreddits
- `/reddit-fp` — Find posts (accepts optional topic, e.g., `/reddit-fp context loss`)
- `/reddit-ac` — Analyze comments

---

## Quick Start

### 1. Initialize

```
/reddit-intel-init
```

Creates `.reddit-intel.json` config + `reddit-intel/product-context.md` template.

### 2. Fill in product context

Edit `reddit-intel/product-context.md` with your product info:
- What your product does
- Core value propositions
- Pain categories your product solves

See `examples/trellis/product-context.md` for a complete example.

### 3. Run the commands

```
/reddit-kw              # discover keywords
/reddit-sub             # find communities
/reddit-fp              # search for posts
/reddit-fp context loss # search for posts about a specific topic
/reddit-ac              # analyze comment sections
```

---

## Repo Structure

```
reddit-intel/
├── commands/                          # 5 independent Claude Code skills
│   ├── reddit-intel-init/SKILL.md     # /reddit-intel-init
│   ├── reddit-kw/SKILL.md            # /reddit-kw
│   ├── reddit-sub/SKILL.md           # /reddit-sub
│   ├── reddit-fp/SKILL.md            # /reddit-fp
│   └── reddit-ac/SKILL.md            # /reddit-ac
├── scripts/
│   └── jsonl_ops.py                   # Shared JSONL operations
├── references/
│   ├── step-details.md                # Detailed execution logic per step
│   ├── product-context.template.md    # English product context template
│   └── product-context.template.zh.md # Chinese product context template
├── examples/
│   └── trellis/                       # Real-world example data
│       ├── product-context.md
│       ├── keywords.jsonl             # 45 keywords
│       ├── subreddits.jsonl           # 53 subreddits
│       ├── posts.jsonl                # 44 posts
│       └── comments.jsonl             # 54 comments
├── SKILL.md                           # Full reference (all steps in one file)
├── README.md
└── LICENSE                            # MIT
```

---

## Configuration

`.reddit-intel.json` is created by `/reddit-intel-init` in your project root:

```json
{
  "data_dir": "./reddit-intel/data",
  "product_name": "YourProduct",
  "product_context": "./reddit-intel/product-context.md",
  "language": "en"
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `data_dir` | `./reddit-intel/data` | Where JSONL and Markdown files are stored |
| `product_name` | `MyProduct` | Used in rendered Markdown headers |
| `product_context` | `./reddit-intel/product-context.md` | Path to your filled product context |
| `language` | `en` | Output language: `en` or `zh` |

---

## Data Files

| File | Unique Key | Description |
|------|-----------|-------------|
| `keywords.jsonl` | `keyword` | Pain-point keywords with Reddit usage quotes |
| `subreddits.jsonl` | `name` | Communities with tier, activity, and strategy |
| `posts.jsonl` | `url` | Posts with pain category and product solution |
| `comments.jsonl` | `post_url` + `content[:50]` | Competitor / language / need insights |

---

## Example: Trellis

The `examples/trellis/` directory contains real data from using reddit-intel for [Trellis](https://github.com/mindfold-ai/Trellis), an open-source AI development framework.

- **45 keywords** across pain, tool, scenario, and solution categories
- **53 subreddits** across 4 tiers
- **44 posts** tracking active pain-point discussions
- **54 comment insights** with competitor mentions, user language, and unmet needs

---

## License

MIT License. Copyright 2026 Sam Cui.
