# Step Detailed Execution Logic

This file defines the complete execution details for the 4 steps of the reddit-intel skill. Referenced by SKILL.md by step name.

> **Tool Rules (all steps)**: When searching Reddit content, **DO NOT** use the built-in WebSearch (reddit.com is blocked by Anthropic's crawler, causing empty retries and wasted tokens). **MUST** use `mcp__exa__web_search_exa` (type="deep"). Max 3 different queries per search intent; skip if no results.

---

## Step 1: Expand Keywords (expand-keywords)

### Files to Read
- `data/keywords.jsonl` -- existing keywords (unique key: `keyword`)
- `product-context.md` (configured in .reddit-intel.json) -- product positioning and pain points

### Keyword Categories
| category | Meaning | Examples |
|----------|---------|----------|
| pain | Pain Points | context loss, AI amnesia, keeps forgetting |
| tool | Tools | .cursorrules, CLAUDE.md, Cursor |
| scenario | Scenarios | vibe coding, AI pair programming, multi-file refactor |
| solution | Solutions | specs as code, auto-inject, layered context |

### Search Strategy
1. For each category, construct Exa search queries:
   - pain: `"site:reddit.com {keyword} frustration OR problem OR broken"`
   - tool: `"site:reddit.com {tool_name} alternative OR replacement OR better"`
   - scenario: `"site:reddit.com {scenario} workflow OR setup OR tools"`
   - solution: `"site:reddit.com {concept} implementation OR framework"`
2. Execute with `mcp__exa__web_search_exa` (type="deep")
3. Extract new keywords and Reddit user quotes (`reddit_usage` field)
4. Expand with synonyms and long-tail variants for newly discovered terms
5. Dedup by `keyword` field, append new entries to JSONL, re-render `keywords.md`

### Markdown Render Template (keywords.md)
```markdown
# {product_name} Reddit Intelligence Keywords
> Last updated: {date} | Total: {count}

## Pain Points (pain)
| Keyword | Reddit Usage | Source | Added |
|---------|-------------|--------|-------|
| {keyword} | {reddit_usage} | {source} | {added} |

## Tools (tool)
(same table format)

## Scenarios (scenario)
(same table format)

## Solutions (solution)
(same table format)
```

---

## Step 2: Expand Target Subreddits (expand-subreddits)

### Files to Read
- `data/subreddits.jsonl` -- existing subreddits (unique key: `name`)
- `data/keywords.jsonl` -- use keywords to search for new communities

### Tier Definitions
| tier | Label | Criteria |
|------|-------|----------|
| 1 | Core Battleground | Direct user community, high product relevance |
| 2 | High Relevance | Strong secondary audience, developer communities |
| 3 | General / Niche | Broad audience or tech-specific communities |
| 4 | Watching | Newly discovered, pending evaluation |

### Search Strategy
1. Search using new keywords: `"site:reddit.com/r/ {keyword}"`
2. Discover new communities from cross-posts and comments in existing posts
3. Evaluate each new community: members, activity, promo_policy, relevance
4. Newly discovered communities default to tier=4; upgrade manually later
5. Dedup by `name` field, append new entries to JSONL, re-render `subreddits.md`

### Markdown Render Template (subreddits.md)
```markdown
# {product_name} Target Subreddit Library
> Last updated: {date} | Total: {count}

## Tier 1: Core Battleground
| Subreddit | Size | Activity | Promo Policy | Relevance | Strategy | Added |
|-----------|------|----------|-------------|-----------|----------|-------|

## Tier 2: High Relevance
(same table format)

## Tier 3: General / Niche
(same table format)

## Tier 4: Watching
(same table format)
```

---

## Step 3: Find Post Pain Points (find-posts)

### Files to Read
- `data/posts.jsonl` -- existing posts (unique key: `url`)
- `data/keywords.jsonl` -- search keywords
- `data/subreddits.jsonl` -- target communities (**only search tier 1 and tier 2**)

### Pain Category Definitions

Use pain categories from your product-context.md. Each post is classified into the pain category it best matches, along with a `product_solution` describing how your product addresses it.

| pain_category | Meaning | Product Solution |
|---------------|---------|-----------------|
| (defined in product-context.md) | (defined in product-context.md) | (defined in product-context.md) |

### Search Strategy
1. For each tier 1/2 subreddit:
   - Select 3-5 most relevant keywords
   - Construct query: `"site:reddit.com/r/{subreddit} {keyword}"`
   - Execute with `mcp__exa__web_search_exa` (type="deep")
2. Selection criteria: prefer last 30 days, with engagement (comments > 0)
3. Analyze each post's `pain_category` and `product_solution`
4. Mark existing posts older than 30 days as `status="archived"`
5. Dedup by `url`, append new posts to JSONL, re-render `posts.md`

### Post Status Values
| status | Meaning | Condition |
|--------|---------|-----------|
| `active` | Recent post | post_date within last 30 days |
| `archived` | Reference only | post_date > 30 days ago |

### Markdown Render Template (posts.md)
```markdown
# Reddit Post Pain Point Tracker
> Last updated: {date} | Active: {active_count} | Archived: {archived_count}

## Active Posts
| Title | Subreddit | Upvotes | Comments | Post Date | Pain Category | Product Solution | Added |
|-------|-----------|---------|----------|-----------|--------------|-----------------|-------|
| [{title}]({url}) | {subreddit} | {upvotes} | {comments} | {post_date} | {pain_category} | {product_solution} | {added} |

## Archived Posts
(same table format)

## Pain Category Statistics
| Pain Category | Count |
|--------------|-------|
| {category} | {count} |
```

---

## Step 4: Analyze Comments (analyze-comments)

### Files to Read
- `data/posts.jsonl` -- active posts (status=active)
- `data/comments.jsonl` -- already-analyzed comments (unique key: `post_url` + first 50 chars of `content`)

### Comment Type Definitions
| type | Meaning | Key Fields |
|------|---------|-----------|
| competitor | Mentions competing/alternative tools | `competitor` field + `sentiment` (positive/neutral/negative) |
| language | Real user language / copy material | `content` verbatim quote + `insight` for marketing-usable phrasing |
| need | Unmet need | `insight` field records the core need and whether your product can address it |

### Search Strategy
1. Find unanalyzed posts: post `url` not present in comments.jsonl `post_url` set
2. Use `mcp__exa__web_search_exa` (type="deep") to search for post title and get comment summaries
3. Or use WebFetch to scrape the post URL for comments (non-Reddit URLs only)
4. For each valuable comment, classify as competitor / language / need
5. Append to JSONL, re-render `comments.md`

### Markdown Render Template (comments.md)
```markdown
# Reddit Comment Insights
> Last updated: {date} | Posts analyzed: {post_count} | Insights: {total_count}

## Competitor Mentions
| Competitor | Mentions | User Sentiment | Product Differentiation | Source Post |
|-----------|----------|---------------|------------------------|-------------|

## Real User Language (Copy Material)
| Verbatim Quote | Pain Category | Source |
|---------------|--------------|--------|

## Unmet Needs
| Need | Can Product Solve? | Source |
|------|-------------------|--------|

## Analyzed Posts
| Post | Analysis Date |
|------|--------------|
```
