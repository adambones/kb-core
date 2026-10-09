# KB Core

The rules and skills every knowledge base shares. A knowledge base is a repository that a person and their agents keep as the system of record for their work — what is settled, what is in flight and what is under discussion — so that each session starts from documents rather than from memory.

## Install

From the root of the knowledge base, which is a git repository:

```sh
git clone https://github.com/adambones/kb-core.git core
core/sync
```

`core/sync` links each rubric file at the knowledge base's root, where the skills cite it, and each skill into every directory the agents discover skills from — `.claude/skills` for Claude Code, `.agents/skills` for Codex and Gemini CLI — creating both where neither exists. It adds `/core/` to `.gitignore`, and names each Always role below that the knowledge base has not bound. `checkin` runs it each time, so what the core gains reaches each knowledge base with no step of its own.

The checkout sits inside the knowledge base so every committed link is relative and resolves on any machine.

Turn agent memory off in each agent's settings (No Memories). In Claude Code that is `"autoMemoryEnabled": false` in `.claude/settings.json`.

Start the knowledge base's documents from the core alone. Seeding it with another knowledge base's documents imports that one's traits into a new domain.

## Bind

The file every session reads — `AGENTS.md`, with `CLAUDE.md` a link to it for Claude Code — declares each role below under a Bindings heading.

| Role | Asked for by | Needed |
|------|--------------|--------|
| Source of truth | `RUBRIC.md`, `teach-me` | Always |
| Homes | `RUBRIC.md` | Always |
| Lifecycles | `RUBRIC.md` | Always |
| Audience — who messages reach | `MESSAGING.md`, `distill` | Always |
| Product truth — what the product is | `distill` | Where the knowledge base has one |
| Shared repositories — where its writing lands in a repository another audience reads | `checkin`, `audit-comments` | Where the knowledge base has one |
| Verbatim source — where other parties' own words live | `slack-log` | Where the knowledge base follows Slack |
| Followed channels — each Slack channel it mirrors, with its ID and any backfill floor | `slack-log` | Where the knowledge base follows Slack |
| Session exports — where a session's own transcript is written | `export-session` | Where exports should land without the user naming a path |
| Outbound files — where a file bound for another party is written | `build-deepthink` | Where the knowledge base runs deep-think rounds |
| Session correspondence — where a session's exchange is kept, and the skill that keeps it | `build-deepthink` | Where the knowledge base keeps one outside the conversation |

## Supply

The core leaves each knowledge base its orchestrators, the skills that sequence others through its own homes, tracking or tests. Each reads its rules at its own step, never from memory of an earlier read.

| Skill | Does | Needed |
|-------|------|--------|
| A writer of documents | Reads `RUBRIC.md` | Always |
| A writer of skills or root documents | Invokes `cold-read` after every change | Always |
| A recording step | Invokes `checkin` | Always |
| A writer of code | Reads `IMPLEMENTATION.md` §§1–2 before the first edit, then invokes `audit-comments` | Where the knowledge base writes code |
| A reviewer of code | Reads `IMPLEMENTATION.md` §3 | Where the knowledge base reviews code |
| A schedule | Runs `slack-log`'s `sync` over the followed channels | Where the knowledge base follows Slack |
| A deep-think mode | Holds a `deepthink.md`, which `build-deepthink` bundles, and optionally a `gate.md` its answer is checked against | Where the knowledge base runs a kind of exchange the core's default does not |
| A checker of deep-think answers | Checks each answer against the source of truth under the mode's `gate.md`, and writes the check a further pass carries | Where the knowledge base runs deep-think exchanges and wants more than `build-deepthink`'s own last step |

## Tasks

A knowledge base that runs its tasks through make sets the variables `core/kb.mk`'s header names, then `include`s it from its root `Makefile`. `include` rather than `-include`, so a missing core fails loudly. A rule for `core/kb.mk` below the include, which clones the core and runs `core/sync`, lets the first `make` on a fresh checkout restore it; make reads the whole file first, so that rule's recipe must not depend on anything `kb.mk` defines.

## Change

Edit the core through `amend-core`. `core/` is a repository of its own, so its changes never show in the knowledge base's `git status`; `checkin` commits and pushes them there. Two knowledge bases on one machine keep separate checkouts.
