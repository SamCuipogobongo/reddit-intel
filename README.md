# reddit-intel

A Claude Code skill for Reddit competitive intelligence. Discover how your target users describe their pain points, find relevant communities, track posts with real complaints, and extract competitor mentions and unmet needs — all in incrementally-growing JSONL files.

Works for any product. Trellis is included as a real-world example.

---

## What it does

`reddit-intel` runs 4 incremental steps:

| Step | Command | What it finds |
|------|---------|---------------|
| expand-keywords | `/reddit-intel kw` | How Reddit users describe pain points in your product domain |
| expand-subreddits | `/reddit-intel sub` | Which communities your target users live in |
| find-posts | `/reddit-intel fp` | Posts with active pain points matching your product |
| analyze-comments | `/reddit-intel ac` | Competitor mentions, real user language, unmet needs |

Each step is idempotent and incremental. Run it today, run it again next week — data only grows, never overwrites. All output is stored as JSONL (queryable data) and rendered to Markdown (human-readable).

---

## Prerequisites

**Claude Code** with the **Exa MCP server** configured.

Exa is required because Reddit blocks Anthropic's default web crawler. The skill enforces using Exa for all Reddit searches.

To add Exa MCP to Claude Code, add this to your `~/.claude.json` or project `.claude/settings.json`:

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

Add this skill to Claude Code:

```bash
# Option 1: clone and add locally
git clone https://github.com/YOUR_USERNAME/reddit-intel
# then add the skill path to your Claude Code skills config

# Option 2: install via Claude Code skills CLI (if supported)
npx skills add reddit-intel
```

Once installed, the `/reddit-intel` command is available in any Claude Code session.

---

## Quick Start

### 1. Initialize

In your project directory, run:

```
/reddit-intel init
```

Claude will ask for your product name and preferred language (en/zh), then create:
- `.reddit-intel.json` — config file at your project root
- `reddit-intel/product-context.md` — fill this in with your product info
- `reddit-intel/data/` — empty data directory

### 2. Fill in product context

Edit `reddit-intel/product-context.md` with:
- What your product does (one-liner)
- Core value propositions
- Target users
- Pain categories your product solves (used to classify posts)

See `examples/trellis/product-context.md` for a complete example.

### 3. Run the steps

```
/reddit-intel expand-keywords
/reddit-intel expand-subreddits
/reddit-intel find-posts
/reddit-intel analyze-comments
```

Or run `/reddit-intel` with no arguments to see a menu with current stats.

---

## Step Descriptions

### expand-keywords (kw)

Searches Reddit for how users actually describe pain points in your domain. Discovers synonyms, long-tail variants, and Reddit-specific terminology. Groups results by category: `pain`, `tool`, `scenario`, `solution`.

Output: `keywords.jsonl` + `keywords.md`

### expand-subreddits (sub)

Finds Reddit communities where your target users are active. Uses existing keywords to discover new communities. Each subreddit gets a tier rating (1-4) and a strategy note.

Output: `subreddits.jsonl` + `subreddits.md`

### find-posts (fp)

Searches tier 1 and tier 2 subreddits for posts containing real pain points. Classifies each post by pain category and maps it to your product solution. Marks posts older than 30 days as archived.

Output: `posts.jsonl` + `posts.md`

### analyze-comments (ac)

Analyzes comment sections of active posts. Extracts three types of intelligence:
- **competitor** — mentions of competing or alternative tools, with sentiment
- **language** — verbatim user quotes useful as copy material
- **need** — unmet needs, with notes on whether your product addresses them

Output: `comments.jsonl` + `comments.md`

---

## Configuration Reference

`.reddit-intel.json` is created by `init` in your project root:

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
| `keywords.jsonl` | `keyword` | Pain-point and domain keywords with Reddit usage quotes |
| `subreddits.jsonl` | `name` | Target communities with tier, activity, and strategy |
| `posts.jsonl` | `url` | Posts with pain category, product solution, status |
| `comments.jsonl` | `post_url` + `content[:50]` | Comment insights: competitor / language / need |

---

## Example: Trellis

The `examples/trellis/` directory contains real data from using this skill for [Trellis](https://github.com/mindfold-ai/Trellis), an open-source AI development framework for Claude Code and Cursor.

The example includes:
- **45 keywords** across pain, tool, scenario, and solution categories
- **53 subreddits** across 4 tiers
- **44 posts** tracking active pain-point discussions
- **54 comment insights** with competitor mentions, user language, and unmet needs

The Trellis dataset shows what several weeks of running this skill produces: a growing competitive intelligence base that reveals how developers talk about AI coding tool frustrations, which tools they compare, and what features they're missing.

---

## JSONL Schema Reference

### keywords.jsonl

```json
{"keyword": "context loss", "category": "pain", "reddit_usage": "AI keeps forgetting my project context", "source": "r/ClaudeAI", "added": "2026-02-06"}
```

### subreddits.jsonl

```json
{"name": "r/ClaudeAI", "tier": 1, "members": "451K", "activity": "high", "promo_policy": "discussion OK", "relevance": "primary", "strategy": "Pain-point replies", "added": "2026-02-06"}
```

### posts.jsonl

```json
{"url": "https://www.reddit.com/...", "title": "...", "subreddit": "r/ClaudeAI", "upvotes": 85, "comments": 47, "post_date": "2025-06-01", "pain_category": "context_loss", "product_solution": "Hook auto-inject specs", "status": "active", "added": "2026-02-06"}
```

### comments.jsonl

```json
{"post_url": "https://www.reddit.com/...", "type": "competitor", "content": "I use Cursor when I exceed the token limit", "competitor": "Cursor", "sentiment": "positive", "insight": "Cursor used as fallback when hitting token limits", "added": "2026-02-06"}
```

---

## License

MIT License. Copyright 2026 Sam Cui.
