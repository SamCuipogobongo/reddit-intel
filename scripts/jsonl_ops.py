#!/usr/bin/env python3
"""JSONL operations for the reddit-intel skill.

Subcommands:
  init                    - Initialize config and data directory.
  config                  - Print current configuration.
  append <type> '<json>'  - Append entry (dedup by unique key). Prints ADDED or DUP.
  render <type>           - Render JSONL to Markdown.
  stats                   - Print entry counts for all JSONL files.
"""

import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CONFIG_FILE = ".reddit-intel.json"

# ---------------------------------------------------------------------------
# Bilingual labels
# ---------------------------------------------------------------------------

LABELS = {
    "en": {
        "keywords_title": "Reddit Intelligence Keywords",
        "keywords_cats": {
            "pain": "Pain Points",
            "tool": "Tools",
            "scenario": "Scenarios",
            "solution": "Solutions",
        },
        "kw_header": "| Keyword | Reddit Usage | Source | Added |",
        "kw_sep":    "|---------|--------------|--------|-------|",
        "sub_title": "Target Subreddits",
        "sub_tiers": {
            1: "Core Battleground",
            2: "High Relevance",
            3: "General / Niche",
            4: "Watching",
        },
        "sub_header": "| Subreddit | Members | Activity | Promo Policy | Relevance | Strategy | Added |",
        "sub_sep":    "|-----------|---------|----------|-------------|-----------|----------|-------|",
        "posts_title": "Reddit Post Pain-Point Tracker",
        "posts_active": "Active Posts",
        "posts_archived": "Archived Posts",
        "posts_stats": "Pain Category Statistics",
        "posts_header": "| Title | Subreddit | Upvotes | Comments | Post Date | Pain | Product Solution | Added |",
        "posts_sep":    "|-------|-----------|---------|----------|-----------|------|-----------------|-------|",
        "pain_col": "Pain",
        "count_col": "Count",
        "comments_title": "Reddit Comment Insights",
        "comp_section": "Competitor Mentions",
        "comp_header": "| Competitor | Mentions | Sentiment | Differentiation | Source Posts |",
        "comp_sep":    "|------------|----------|-----------|-----------------|-------------|",
        "lang_section": "User Real Language (Copy Material)",
        "lang_header": "| Quote | Pain Point | Source |",
        "lang_sep":    "|-------|------------|--------|",
        "need_section": "Unmet Needs",
        "need_header": "| Need | Can Product Solve? | Source |",
        "need_sep":    "|------|--------------------|--------|",
        "analyzed_section": "Analyzed Posts",
        "analyzed_header": "| Post | Analysis Date |",
        "analyzed_sep":    "|------|---------------|",
        "none_yet": "*None yet*",
        "stats_title": "Reddit Intel Data Stats",
        "stats_unit": "entries",
        "posts_per": "posts",
    },
    "zh": {
        "keywords_title": "Reddit \u60c5\u62a5\u5173\u952e\u8bcd\u5e93",
        "keywords_cats": {
            "pain": "\u75db\u70b9\u8bcd",
            "tool": "\u5de5\u5177\u8bcd",
            "scenario": "\u573a\u666f\u8bcd",
            "solution": "\u65b9\u6848\u8bcd",
        },
        "kw_header": "| \u5173\u952e\u8bcd | Reddit \u771f\u5b9e\u7528\u8bed | \u6765\u6e90 | \u6dfb\u52a0\u65e5\u671f |",
        "kw_sep":    "|--------|----------------|------|---------|",
        "sub_title": "\u76ee\u6807 Subreddit \u5e93",
        "sub_tiers": {
            1: "\u4e3b\u6218\u573a",
            2: "\u9ad8\u76f8\u5173\u793e\u533a",
            3: "\u901a\u7528 / \u5782\u76f4",
            4: "\u89c2\u5bdf\u4e2d",
        },
        "sub_header": "| Subreddit | \u89c4\u6a21 | \u6d3b\u8dc3\u5ea6 | \u63a8\u5e7f\u653f\u7b56 | \u76f8\u5173\u5ea6 | \u7b56\u7565 | \u6dfb\u52a0\u65e5\u671f |",
        "sub_sep":    "|-----------|------|--------|---------|--------|------|---------|",
        "posts_title": "Reddit \u5e16\u6587\u75db\u70b9\u8ffd\u8e2a",
        "posts_active": "\u6d3b\u8dc3\u5e16\u6587",
        "posts_archived": "\u5df2\u5f52\u6863\u5e16\u6587",
        "posts_stats": "\u75db\u70b9\u5206\u7c7b\u7edf\u8ba1",
        "posts_header": "| \u6807\u9898 | Subreddit | Upvotes | \u8bc4\u8bba | \u53d1\u5e16\u65e5\u671f | \u75db\u70b9 | \u4ea7\u54c1\u89e3\u6cd5 | \u6dfb\u52a0\u65e5\u671f |",
        "posts_sep":    "|------|-----------|---------|------|---------|------|---------|---------|",
        "pain_col": "\u75db\u70b9",
        "count_col": "\u51fa\u73b0\u6b21\u6570",
        "comments_title": "Reddit \u8bc4\u8bba\u533a\u60c5\u62a5",
        "comp_section": "\u7ade\u54c1\u63d0\u53ca",
        "comp_header": "| \u7ade\u54c1 | \u63d0\u53ca\u6b21\u6570 | \u7528\u6237\u8bc4\u4ef7 | \u4ea7\u54c1\u5dee\u5f02\u5316 | \u6765\u6e90\u5e16\u6587 |",
        "comp_sep":    "|------|---------|---------|-----------|---------|",
        "lang_section": "\u7528\u6237\u771f\u5b9e\u8bed\u8a00\uff08\u6587\u6848\u7d20\u6750\uff09",
        "lang_header": "| \u539f\u8bdd\u6458\u5f55 | \u75db\u70b9 | \u6765\u6e90 |",
        "lang_sep":    "|---------|------|------|",
        "need_section": "\u672a\u88ab\u6ee1\u8db3\u7684\u9700\u6c42",
        "need_header": "| \u9700\u6c42 | \u4ea7\u54c1\u80fd\u5426\u6ee1\u8db3 | \u6765\u6e90 |",
        "need_sep":    "|------|------------|------|",
        "analyzed_section": "\u5df2\u5206\u6790\u5e16\u6587\u5217\u8868",
        "analyzed_header": "| \u5e16\u6587 | \u5206\u6790\u65e5\u671f |",
        "analyzed_sep":    "|------|---------|",
        "none_yet": "*\u6682\u65e0*",
        "stats_title": "Reddit \u60c5\u62a5\u6570\u636e\u7edf\u8ba1",
        "stats_unit": "\u6761",
        "posts_per": "\u7bc7",
    },
}

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

TYPES = {
    "keywords":   {"unique_key": ["keyword"],                    "file": "keywords"},
    "subreddits": {"unique_key": ["name"],                       "file": "subreddits"},
    "posts":      {"unique_key": ["url"],                        "file": "posts"},
    "comments":   {"unique_key": ["post_url", "content_prefix"], "file": "comments"},
}

# ---------------------------------------------------------------------------
# Config management
# ---------------------------------------------------------------------------

_CONFIG = None
BASE = None


def find_config_root():
    """Walk up from CWD looking for .reddit-intel.json. Return the dir containing it."""
    d = os.getcwd()
    while True:
        if os.path.isfile(os.path.join(d, CONFIG_FILE)):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    # fallback: try git root
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip()
    except Exception:
        return os.getcwd()


def load_config():
    """Load .reddit-intel.json, return dict with keys:
    data_dir, product_name, product_context, language.
    """
    root = find_config_root()
    path = os.path.join(root, CONFIG_FILE)
    if not os.path.isfile(path):
        print(
            f"ERROR: {CONFIG_FILE} not found. Run 'jsonl_ops.py init' first.",
            file=sys.stderr,
        )
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    # Resolve relative data_dir to absolute
    cfg["_root"] = root
    if not os.path.isabs(cfg.get("data_dir", "")):
        cfg["data_dir"] = os.path.join(root, cfg["data_dir"])
    else:
        cfg["data_dir"] = cfg["data_dir"]
    if "product_context" in cfg and not os.path.isabs(cfg["product_context"]):
        cfg["product_context"] = os.path.join(root, cfg["product_context"])
    cfg.setdefault("language", "en")
    cfg.setdefault("product_name", "MyProduct")
    return cfg


def get_config():
    """Return the cached config, loading it on first call."""
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = load_config()
    return _CONFIG


def base_dir():
    """Return the absolute path to the data directory."""
    global BASE
    if BASE is None:
        BASE = get_config()["data_dir"]
    return BASE

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def jsonl_path(typ):
    """Return the JSONL file path for a given type."""
    return os.path.join(base_dir(), TYPES[typ]["file"] + ".jsonl")


def md_path(typ):
    """Return the Markdown file path for a given type."""
    return os.path.join(base_dir(), TYPES[typ]["file"] + ".md")


def today():
    """Return today's date in ISO format."""
    return date.today().isoformat()

# ---------------------------------------------------------------------------
# JSONL I/O
# ---------------------------------------------------------------------------


def read_jsonl(path):
    """Read a JSONL file, skip malformed lines with a warning."""
    entries = []
    if not os.path.exists(path):
        return entries
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                print(
                    f"WARNING: skipping malformed line {lineno} in {path}",
                    file=sys.stderr,
                )
    return entries


def build_dedup_key(entry, typ):
    """Build a dedup key string for the given entry and type."""
    tcfg = TYPES[typ]
    parts = []
    for k in tcfg["unique_key"]:
        if k == "content_prefix":
            parts.append(entry.get("content", "")[:50])
        else:
            parts.append(str(entry.get(k, "")))
    return "\x00".join(parts)


def _trunc(text, n=60):
    """Truncate text to n characters, adding ellipsis if needed."""
    if not text:
        return ""
    if len(text) <= n:
        return text
    return text[: n - 3] + "..."

# ---------------------------------------------------------------------------
# cmd_init
# ---------------------------------------------------------------------------


def cmd_init(args):
    """Initialize reddit-intel config and data directory."""
    import argparse
    import shutil

    parser = argparse.ArgumentParser(prog="jsonl_ops.py init")
    parser.add_argument("--data-dir", default="./reddit-intel/data")
    parser.add_argument("--product-name", default="MyProduct")
    parser.add_argument(
        "--template-src",
        default=None,
        help="Path to product-context.template.md",
    )
    parser.add_argument("--lang", default="en", choices=["en", "zh"])
    parsed = parser.parse_args(args)

    # Determine project root (git root or CWD)
    try:
        root = (
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
    except Exception:
        root = os.getcwd()

    # Compute context path (sibling of data dir)
    data_parent = os.path.dirname(parsed.data_dir.rstrip("/"))
    if not data_parent:
        data_parent = os.path.dirname(parsed.data_dir)
    if not data_parent:
        data_parent = "."
    context_path = os.path.join(data_parent, "product-context.md")

    config = {
        "data_dir": parsed.data_dir,
        "product_name": parsed.product_name,
        "product_context": context_path,
        "language": parsed.lang,
    }

    config_path = os.path.join(root, CONFIG_FILE)
    with open(config_path, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    # Create data directory
    abs_data = os.path.join(root, parsed.data_dir)
    os.makedirs(abs_data, exist_ok=True)

    # Resolve template: explicit --template-src > auto-detect by --lang
    template = parsed.template_src
    if not template:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        refs_dir = os.path.join(os.path.dirname(script_dir), "references")
        if parsed.lang == "zh":
            candidate = os.path.join(refs_dir, "product-context.template.zh.md")
        else:
            candidate = os.path.join(refs_dir, "product-context.template.md")
        if os.path.isfile(candidate):
            template = candidate

    # Copy template
    abs_context = os.path.join(root, context_path)
    if template and os.path.isfile(template):
        if not os.path.isfile(abs_context):
            os.makedirs(os.path.dirname(abs_context), exist_ok=True)
            shutil.copy2(template, abs_context)
            print(f"Created {context_path} from template")
        else:
            print(f"Skipped: {context_path} already exists")

    print(f"Created {CONFIG_FILE} at {config_path}")
    print(f"Data directory: {abs_data}")
    print(f"\nNext steps:")
    print(f"  1. Edit {context_path} with your product info")
    print(f"  2. Run /reddit-intel expand-keywords")

# ---------------------------------------------------------------------------
# cmd_config
# ---------------------------------------------------------------------------


def cmd_config():
    """Print the current configuration as JSON."""
    cfg = load_config()
    print(
        json.dumps(
            {k: v for k, v in cfg.items() if not k.startswith("_")},
            indent=2,
            ensure_ascii=False,
        )
    )

# ---------------------------------------------------------------------------
# cmd_append
# ---------------------------------------------------------------------------


def cmd_append(typ, json_str):
    """Append a JSON entry to the JSONL file, deduplicating by unique key."""
    entry = json.loads(json_str)
    path = jsonl_path(typ)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    existing = read_jsonl(path)
    keys = {build_dedup_key(e, typ) for e in existing}
    new_key = build_dedup_key(entry, typ)
    if new_key in keys:
        print("DUP")
        return
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("ADDED")

# ---------------------------------------------------------------------------
# Render: keywords
# ---------------------------------------------------------------------------


def render_keywords(entries):
    """Render keywords JSONL entries to Markdown."""
    cfg = get_config()
    L = LABELS[cfg["language"]]
    cats = L["keywords_cats"]
    grouped = defaultdict(list)
    for e in entries:
        grouped[e.get("category", "pain")].append(e)

    lines = [
        f"# {cfg['product_name']} {L['keywords_title']}",
        f"> Updated: {today()} | Total: {len(entries)}",
        "",
    ]
    for cat, label in cats.items():
        rows = grouped.get(cat, [])
        lines.append(f"## {label} ({cat})")
        lines.append(L["kw_header"])
        lines.append(L["kw_sep"])
        for e in rows:
            lines.append(
                f"| {e.get('keyword', '')} "
                f"| {e.get('reddit_usage', '')} "
                f"| {e.get('source', '')} "
                f"| {e.get('added', '')} |"
            )
        lines.append("")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Render: subreddits
# ---------------------------------------------------------------------------


def render_subreddits(entries):
    """Render subreddits JSONL entries to Markdown."""
    cfg = get_config()
    L = LABELS[cfg["language"]]
    tier_labels = L["sub_tiers"]
    grouped = defaultdict(list)
    for e in entries:
        grouped[e.get("tier", 4)].append(e)

    lines = [
        f"# {cfg['product_name']} {L['sub_title']}",
        f"> Updated: {today()} | Total: {len(entries)}",
        "",
    ]
    for tier in (1, 2, 3, 4):
        label = tier_labels[tier]
        rows = grouped.get(tier, [])
        lines.append(f"## Tier {tier}: {label}")
        lines.append(L["sub_header"])
        lines.append(L["sub_sep"])
        for e in rows:
            lines.append(
                f"| {e.get('name', '')} | {e.get('members', '')} | {e.get('activity', '')} "
                f"| {e.get('promo_policy', '')} | {e.get('relevance', '')} "
                f"| {e.get('strategy', '')} | {e.get('added', '')} |"
            )
        lines.append("")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Render: posts
# ---------------------------------------------------------------------------


def render_posts(entries):
    """Render posts JSONL entries to Markdown."""
    cfg = get_config()
    L = LABELS[cfg["language"]]

    active = sorted(
        [e for e in entries if e.get("status") == "active"],
        key=lambda e: e.get("upvotes", 0),
        reverse=True,
    )
    archived = sorted(
        [e for e in entries if e.get("status") == "archived"],
        key=lambda e: e.get("upvotes", 0),
        reverse=True,
    )

    lines = [
        f"# {L['posts_title']}",
        f"> Updated: {today()} | Active: {len(active)} | Archived: {len(archived)}",
        "",
    ]

    # Active posts
    lines.append(f"## {L['posts_active']}")
    lines.append(L["posts_header"])
    lines.append(L["posts_sep"])
    for e in active:
        title_link = f"[{e.get('title', '')}]({e.get('url', '')})"
        solution = e.get("product_solution", "")
        lines.append(
            f"| {title_link} | {e.get('subreddit', '')} | {e.get('upvotes', '')} "
            f"| {e.get('comments', '')} | {e.get('post_date', '')} "
            f"| {e.get('pain_category', '')} | {solution} | {e.get('added', '')} |"
        )
    lines.append("")

    # Archived posts
    lines.append(f"## {L['posts_archived']}")
    if archived:
        lines.append(L["posts_header"])
        lines.append(L["posts_sep"])
        for e in archived:
            title_link = f"[{e.get('title', '')}]({e.get('url', '')})"
            solution = e.get("product_solution", "")
            lines.append(
                f"| {title_link} | {e.get('subreddit', '')} | {e.get('upvotes', '')} "
                f"| {e.get('comments', '')} | {e.get('post_date', '')} "
                f"| {e.get('pain_category', '')} | {solution} | {e.get('added', '')} |"
            )
    else:
        lines.append(L["none_yet"])
    lines.append("")

    # Pain category statistics
    pain_counts = Counter(e.get("pain_category", "") for e in entries)
    lines.append(f"## {L['posts_stats']}")
    lines.append(f"| {L['pain_col']} | {L['count_col']} |")
    lines.append("|------|---------|")
    for pain, cnt in pain_counts.most_common():
        lines.append(f"| {pain} | {cnt} |")
    lines.append("")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Render: comments
# ---------------------------------------------------------------------------


def render_comments(entries):
    """Render comments JSONL entries to Markdown."""
    cfg = get_config()
    L = LABELS[cfg["language"]]

    competitors = [e for e in entries if e.get("type") == "competitor"]
    language = [e for e in entries if e.get("type") == "language"]
    needs = [e for e in entries if e.get("type") == "need"]
    post_urls = sorted(set(e.get("post_url", "") for e in entries))

    lines = [
        f"# {L['comments_title']}",
        (
            f"> Updated: {today()} | Analyzed: {len(post_urls)} "
            f"{L['posts_per']} | Insights: {len(entries)}"
        ),
        "",
    ]

    # Competitor mentions -- aggregate by competitor name
    lines.append(f"## {L['comp_section']}")
    lines.append(L["comp_header"])
    lines.append(L["comp_sep"])
    comp_grouped = defaultdict(list)
    for e in competitors:
        comp_grouped[e.get("competitor", "")].append(e)
    for comp, items in sorted(comp_grouped.items()):
        sentiments = ", ".join(
            sorted(set(e.get("sentiment", "") for e in items if e.get("sentiment")))
        )
        insights = "; ".join(
            _trunc(e.get("insight", ""), 50) for e in items
        )
        lines.append(
            f"| {comp} | {len(items)} | {sentiments} "
            f"| {insights} | {len(items)} {L['posts_per']} |"
        )
    lines.append("")

    # User real language
    lines.append(f"## {L['lang_section']}")
    lines.append(L["lang_header"])
    lines.append(L["lang_sep"])
    for e in language:
        content = _trunc(e.get("content", ""), 80)
        insight = _trunc(e.get("insight", ""), 60)
        lines.append(
            f"| {content} | {insight} | {_trunc(e.get('post_url', ''), 40)} |"
        )
    lines.append("")

    # Unmet needs
    lines.append(f"## {L['need_section']}")
    lines.append(L["need_header"])
    lines.append(L["need_sep"])
    for e in needs:
        content = _trunc(e.get("content", ""), 80)
        insight = _trunc(e.get("insight", ""), 60)
        lines.append(
            f"| {content} | {insight} | {_trunc(e.get('post_url', ''), 40)} |"
        )
    lines.append("")

    # Analyzed posts list
    lines.append(f"## {L['analyzed_section']}")
    lines.append(L["analyzed_header"])
    lines.append(L["analyzed_sep"])
    # Get unique post_urls with their earliest added date
    post_dates = {}
    for e in entries:
        url = e.get("post_url", "")
        d = e.get("added", "")
        if url not in post_dates or d < post_dates[url]:
            post_dates[url] = d
    for url in sorted(post_dates):
        lines.append(f"| {_trunc(url, 80)} | {post_dates[url]} |")
    lines.append("")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Render dispatch
# ---------------------------------------------------------------------------

RENDERERS = {
    "keywords":   render_keywords,
    "subreddits": render_subreddits,
    "posts":      render_posts,
    "comments":   render_comments,
}


def cmd_render(typ):
    """Read JSONL, render to Markdown, write .md file."""
    entries = read_jsonl(jsonl_path(typ))
    md = RENDERERS[typ](entries)
    out = md_path(typ)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"Rendered {len(entries)} entries -> {out}")

# ---------------------------------------------------------------------------
# cmd_stats
# ---------------------------------------------------------------------------


def cmd_stats():
    """Print entry counts for all JSONL files."""
    cfg = get_config()
    L = LABELS[cfg["language"]]
    print(L["stats_title"])
    print("\u2501" * 30)
    for typ, tcfg in TYPES.items():
        path = jsonl_path(typ)
        count = 0
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        count += 1
        fname = tcfg["file"] + ".jsonl"
        print(f"{fname:<20}: {count} {L['stats_unit']}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        cmd_init(sys.argv[2:])

    elif cmd == "config":
        cmd_config()

    elif cmd == "append":
        if len(sys.argv) < 4:
            print(
                "Usage: jsonl_ops.py append <type> '<json>'",
                file=sys.stderr,
            )
            sys.exit(1)
        typ = sys.argv[2]
        if typ not in TYPES:
            print(
                f"ERROR: unknown type '{typ}'. Valid: {', '.join(TYPES)}",
                file=sys.stderr,
            )
            sys.exit(1)
        cmd_append(typ, sys.argv[3])

    elif cmd == "render":
        if len(sys.argv) < 3:
            print(
                "Usage: jsonl_ops.py render <type>",
                file=sys.stderr,
            )
            sys.exit(1)
        typ = sys.argv[2]
        if typ not in TYPES:
            print(
                f"ERROR: unknown type '{typ}'. Valid: {', '.join(TYPES)}",
                file=sys.stderr,
            )
            sys.exit(1)
        cmd_render(typ)

    elif cmd == "stats":
        cmd_stats()

    else:
        print(f"ERROR: unknown command '{cmd}'", file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
