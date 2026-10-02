# KB Core

The rules and skills every knowledge base shares. A knowledge base is a repository that a person and their agents keep as the system of record for their work — what is settled, what is in flight and what is under discussion — so that each session starts from documents rather than from memory.

## Install

From the knowledge base's root:

```sh
git clone https://github.com/adambones/kb-core.git core
echo '/core/' >> .gitignore
ln -s core/RUBRIC.md RUBRIC.md
ln -s core/MESSAGING.md MESSAGING.md
ln -s core/IMPLEMENTATION.md IMPLEMENTATION.md
```

The skills cite the rubric files by those root names. The checkout sits inside the knowledge base so every committed link is relative and resolves on any machine. It is not a submodule, which would pin a commit and make every edit a commit here plus a pointer bump in each knowledge base.

Link each skill into every directory the knowledge base's agents discover skills from — `.claude/skills` for Claude Code, `.agents/skills` for Codex:

```sh
mkdir -p .claude/skills .agents/skills
for s in core/skills/*; do
  ln -s "../../$s" ".claude/skills/${s##*/}"
  ln -s "../../$s" ".agents/skills/${s##*/}"
done
```

Where those directories are themselves links to one skill directory the knowledge base keeps, link the core's skills into that directory once instead. A skill the core gains later needs its links in each knowledge base.

`export-thread` serves every session on the machine, not only a knowledge base's, so link it once per machine into Claude Code's user-level skill directory as well — Claude Code being the one agent whose transcripts it reads:

```sh
mkdir -p ~/.claude/skills
ln -s "$PWD/core/skills/export-thread" ~/.claude/skills/export-thread
```

Turn agent memory off in each agent's settings (No Memories). In Claude Code that is `"autoMemoryEnabled": false` in `.claude/settings.json`.

Start the knowledge base's documents from the core alone, and give its first few a cold read before the corpus grows. Seeding it with another knowledge base's documents imports that one's traits into a new domain.

## Bind

The file every session reads — `AGENTS.md`, with `CLAUDE.md` a link to it for Claude Code — declares each role below under a Bindings heading, as `RUBRIC.md` defines them.

| Role | Asked for by | Needed |
|------|--------------|--------|
| Source of truth | `RUBRIC.md` | Always |
| Homes | `RUBRIC.md` | Always |
| Lifecycles | `RUBRIC.md` | Always |
| Audience — who messages reach | `MESSAGING.md`, `distill` | Always |
| Product truth — what the product is | `distill` | Where the knowledge base has one |
| Shared repositories — where its writing lands in a repository another audience reads | `checkin`, `audit-comments` | Where the knowledge base has one |
| Verbatim source — where other parties' own words live | `slack-log` | Where the knowledge base follows Slack |
| Followed channels — each Slack channel it mirrors, with its ID and any backfill floor | `slack-log` | Where the knowledge base follows Slack |

## Supply

The core leaves each knowledge base its orchestrators, the skills that sequence others through its own homes, tracking or tests. Each reads its rules at its own step, never from memory of an earlier read.

| Skill | Reads | Needed |
|-------|-------|--------|
| A writer of documents | `RUBRIC.md` | Always |
| A recording step | Invokes `checkin` | Always |
| A writer of code | `IMPLEMENTATION.md` §§1–2 before the first edit, then invokes `audit-comments` | Where the knowledge base writes code |
| A reviewer of code | `IMPLEMENTATION.md` §3 | Where the knowledge base reviews code |
| A schedule | Runs `slack-log`'s `sync` over the followed channels | Where the knowledge base follows Slack |

## Change

Edit the core through `amend-core`. `core/` is a repository of its own, so its changes never show in the knowledge base's `git status`; `checkin` commits and pushes them there. Two knowledge bases on one machine keep separate checkouts, which stay in step by pull.
