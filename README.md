# reddit-intel

把 Reddit 变成你的竞品情报机器 —— 在终端里直接跑。

reddit-intel 是一组 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill，自动发现真实用户怎么描述你的产品能解决的问题、他们在哪些社区活跃、评论区提到了哪些竞品、还有什么需求没被满足。

所有数据存在 git 友好的 JSONL 文件里。今天跑一次，下周再跑一次 —— 只增不删，持续积累。

---

## 工作流程

```
/reddit-kw                        /reddit-sub
  从 Reddit 用户语言中              找到目标用户活跃的
  发现痛点关键词                    相关社区（subreddit）
        │                                  │
        └──────────┬───────────────────────┘
                   ▼
             /reddit-fp
               在 tier 1/2 社区中搜索
               匹配关键词的痛点帖子
                   │
                   ▼
             /reddit-ac
               分析评论区，提取：
               • 竞品提及 + 用户情感
               • 用户原话（文案素材）
               • 未被满足的需求
                   │
                   ▼
         JSONL（数据源）+ Markdown（展示层）
         ──── git 追踪，只增不删 ────
```

4 个独立命令，每个都是独立的 Claude Code skill —— 随时调用，顺序随意。

---

## 你能拿到什么

**keywords.jsonl** — Reddit 用户描述痛点的真实用语：
```json
{"keyword": "context loss", "category": "pain", "reddit_usage": "Claude keeps forgetting my project context", "source": "r/ClaudeAI"}
```

**subreddits.jsonl** — 目标社区，按价值分层：
```json
{"name": "r/ClaudeAI", "tier": 1, "members": "451K", "promo_policy": "discussion OK", "strategy": "Pain-point replies"}
```

**posts.jsonl** — 正在讨论你能解决的问题的帖子：
```json
{"title": "200K context just ain't cutting it", "subreddit": "r/ClaudeAI", "upvotes": 85, "pain_category": "context_loss", "product_solution": "Layered context architecture"}
```

**comments.jsonl** — 从评论区提取的竞品情报：
```json
{"type": "competitor", "content": "I switched to Cursor when hitting token limits", "competitor": "Cursor", "sentiment": "positive", "insight": "Cursor used as fallback"}
{"type": "language", "content": "compacting process straight-up nukes crucial context", "insight": "Users frame compaction as lossy compression"}
{"type": "need", "content": "Need persistent memory across sessions", "insight": "Core unmet need — file-based injection solves this"}
```

每个 JSONL 文件同时渲染为 Markdown 报告，方便人类阅读。

---

## 前置条件

1. 安装 **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)**
2. 配置 **[Exa](https://exa.ai) MCP server** —— 因为 Reddit 屏蔽了 Anthropic 的默认爬虫，必须用 Exa 搜索

在 Claude Code 配置文件（`~/.claude.json` 或 `.claude/settings.json`）中添加：

```json
{
  "mcpServers": {
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": { "EXA_API_KEY": "去 exa.ai 申请" }
    }
  }
}
```

---

## 安装

```bash
# 克隆
git clone https://github.com/SamCuipogobongo/reddit-intel ~/.claude/skills/reddit-intel

# 把每个命令链接为独立 skill
for cmd in reddit-intel-init reddit-kw reddit-sub reddit-fp reddit-ac; do
  ln -s ~/.claude/skills/reddit-intel/commands/$cmd ~/.claude/skills/$cmd
done
```

搞定。5 个斜杠命令在所有 Claude Code 会话中可用。

---

## 快速上手

**第 1 步** — 在项目目录中初始化：
```
/reddit-intel-init
```
创建 `.reddit-intel.json` 配置文件 + `product-context.md` 模板。

**第 2 步** — 填写 `product-context.md`：你的产品解决什么痛点、目标用户是谁、核心价值是什么。参考 [`examples/trellis/product-context.md`](examples/trellis/product-context.md) 看真实示例。

**第 3 步** — 开跑：
```
/reddit-kw                 # 发现关键词
/reddit-sub                # 找社区
/reddit-fp                 # 搜帖子
/reddit-fp context loss    # ...或聚焦某个话题
/reddit-ac                 # 分析评论区
```

每个命令都是：读已有数据 → 搜索新条目 → 去重追加 → 重新渲染。想跑几次跑几次。

---

## 仓库结构

```
reddit-intel/
├── commands/                          # 5 个独立 Claude Code skill
│   ├── reddit-intel-init/SKILL.md     # /reddit-intel-init
│   ├── reddit-kw/SKILL.md            # /reddit-kw
│   ├── reddit-sub/SKILL.md           # /reddit-sub
│   ├── reddit-fp/SKILL.md            # /reddit-fp
│   └── reddit-ac/SKILL.md            # /reddit-ac
├── scripts/
│   └── jsonl_ops.py                   # 共享脚本：append, render, stats, init
├── references/
│   ├── step-details.md                # 每个 step 的详细搜索策略
│   ├── product-context.template.md    # 英文模板
│   └── product-context.template.zh.md # 中文模板
├── examples/
│   └── trellis/                       # 真实案例（见下方）
├── SKILL.md                           # 完整参考（所有 step 合一）
└── LICENSE                            # MIT
```

---

## 配置说明

`.reddit-intel.json` 由 `/reddit-intel-init` 创建：

```json
{
  "data_dir": "./reddit-intel/data",
  "product_name": "YourProduct",
  "product_context": "./reddit-intel/product-context.md",
  "language": "zh"
}
```

| 字段 | 说明 |
|------|------|
| `data_dir` | JSONL + Markdown 文件存放目录 |
| `product_name` | 渲染 Markdown 标题时使用 |
| `product_context` | 你填写好的产品上下文文件路径 |
| `language` | `en` 或 `zh`，所有输出标签自动切换 |

---

## 真实案例：Trellis

[`examples/trellis/`](examples/trellis/) 包含用 reddit-intel 为 [Trellis](https://github.com/mindfold-ai/Trellis)（开源 AI 开发框架）做竞品情报的真实数据。

几周增量运行后的积累：

| 数据 | 数量 | 发现了什么 |
|------|------|-----------|
| 关键词 | 45 | "context rot"、"AI amnesia"、"compacting nukes context" — 用户真实用语 |
| 社区 | 53 | r/ClaudeAI, r/ClaudeCode, r/ChatGPTCoding 为 tier 1；r/LocalLLaMA, r/cursor 为 tier 2 |
| 帖子 | 44 | context_loss 是 #1 痛点分类；1M context window 并没有解决问题 |
| 评论洞察 | 54 | Cursor、Obsidian vaults、devctx MCP、Ember MCP 为竞品；"250-500K token 后质量下降" |

这就是持续积累的情报基础 —— 每次运行都增加更多信号。

---

## License

MIT — Sam Cui, 2026
