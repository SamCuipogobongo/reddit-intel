# Trellis Product Context (for Reddit Intelligence)

## One-liner

Trellis is an open-source AI development framework for Claude Code & Cursor that auto-injects project specs so your AI assistant truly understands your codebase.

## Core Value Propositions

1. **Teach Once, Apply Forever** -- Write coding standards in Markdown specs, auto-injected into every AI session via Hooks. No more repeating yourself.
2. **The More You Use It, The Smarter It Gets** -- Best practices live in auto-updated spec files. Lessons from every task become a growing knowledge base.
3. **Ship in Parallel, Multiply Output** -- Git Worktree-powered multi-agent parallel development. Multiple features at once, zero conflicts.
4. **Team Knowledge Sharing** -- One person's best practice benefits the entire team. Spec files are version-controlled alongside code.
5. **Cross-Session Memory** -- Work traces persist in your repo. AI reads previous session records, achieving genuine cross-session project memory.

## Target Users

| User Type | Core Benefit |
|-----------|-------------|
| Solo Developers | AI understands project context, less repetitive communication |
| Engineering Teams | Unified AI coding standards, shared best practices |
| Tech Leads | Define standards via specs, automated quality assurance |
| Power AI Coders | Parallel development, cross-session memory, custom workflows |
| OSS Maintainers | Define contribution standards, auto-inject for every contributor |

## Differentiation vs Alternatives

| vs What | Trellis Advantage |
|---------|------------------|
| `.cursorrules` | Layered architecture with context compression vs monolithic single file |
| Claude Skills | Hook-enforced injection (can't be skipped) vs optional Skills |
| No framework | Structured specs + auto-inject vs re-explaining every session |
| CLAUDE.md alone | Task management + parallel sessions + workspace + quality loops |

## Key Technical Features (for Reddit discussions)

- **Auto-Injection via Hooks** -- Specs loaded at session start, not optional
- **Layered Context Architecture** -- Only injects relevant specs per task
- **Task Management System** -- PRD + implement/check/debug agent context
- **Parallel Sessions** -- Git Worktrees for isolated multi-agent work
- **Personal Workspace** -- Session journaling with cross-session continuity
- **Custom Skills & Commands** -- Define slash commands for workflow automation
- **Quality Assurance Loop** -- Programmatic verification (lint, type-check) in a loop

## Quick Facts

- Open source: AGPL-3.0
- GitHub Stars: 1.7K+
- Tech stack: TypeScript, Node.js 18+
- Supports: Claude Code + Cursor
- Install: `npm install -g @mindfoldhq/trellis@latest`
- Website: https://trytrellis.app/
- GitHub: https://github.com/mindfold-ai/Trellis
- Discord: https://discord.com/invite/tWcCZ3aRHc

## Pain Categories (for post classification)

| pain_category | Meaning | Product Solution |
|---------------|---------|-----------------|
| context_loss | AI loses project context after session start or auto-compact | Hook auto-inject specs on every session start |
| inconsistent_output | AI ignores coding conventions, produces inconsistent code | Layered context architecture enforces standards |
| no_memory | No cross-session memory, AI starts blank every time | Cross-session workspace journals |
| vibe_coding_quality | Vibe coding produces unmaintainable or unsafe code | Quality assurance loop with lint/typecheck |
| no_parallel | Can't run multiple AI agents simultaneously | Git worktree parallel sessions |
| team_chaos | Team members get inconsistent AI behavior, no shared standards | Team spec sharing via version-controlled files |
| cursorrules_limits | .cursorrules file growing too large, monolithic and hard to manage | Layered context architecture replaces single file |
