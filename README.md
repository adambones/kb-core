# KB Core

The rules and skills every knowledge base shares. A knowledge base is a repository that a person and their agents keep as the system of record for their work — what is settled, what is in flight and what is under discussion — so that each session starts from documents rather than from memory.

## Install

From the root of the knowledge base, which is a git repository:

```sh
git clone https://github.com/adambones/kb-core.git core
core/sync
```

`core/sync` links each skill into every directory the agents discover skills from — `.claude/skills` for Claude Code, `.agents/skills` for Codex, Gemini CLI and Antigravity — creating both where neither exists. It removes any link at the knowledge base's root into the core, since the skills cite the core's rubrics in place, as `core/<name>.md`. It adds `/core` to `.gitignore`, creates each slot below, with a line of its own there for each the table marks ignored, and names each Always role below that the knowledge base has not bound and each file that would keep Claude Code from reading `AGENTS.md`. `checkin` runs it each time, so what the core gains reaches each knowledge base with no step of its own.

The checkout sits inside the knowledge base so every committed link is relative and resolves on any machine.

Turn agent memory off in each agent's settings (No Memories). In Claude Code that is `"autoMemoryEnabled": false` in `.claude/settings.json`.

Run each agent in its auto mode, which proceeds on routine work and asks only before an irreversible action, since the skills run unattended. In Claude Code that is `"defaultMode": "auto"` under `permissions` in `.claude/settings.json`. In Antigravity it is Agent Mode `auto` in `/config`, one setting for every workspace on the machine.

Start the knowledge base's documents from the core alone. Seeding it with another knowledge base's documents imports that one's traits into a new domain.

## Bind

`AGENTS.md`, the file every session reads, declares each role below under a Bindings heading. Claude Code reads it only where no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` sits in the directory a session starts in or any above it ([Claude Code's AGENTS.md support](https://code.claude.com/docs/en/memory#agents-md)), so none sits at or above the knowledge base's root.

| Role | Asked for by | Needed |
|------|--------------|--------|
| Source of truth | `core/RUBRIC.md`, `deliberate`, `teach-me` | Always |
| Homes | `core/RUBRIC.md` | Always |
| Lifecycles | `core/RUBRIC.md`, `deliberate`, `audit-comments`, `improve-docs` | Always |
| Slots | `core/RUBRIC.md` | Always |
| Audience — who messages reach | `core/MESSAGING.md`, `distill` | Always |
| Product truth — what the product is | `deliberate`, `distill` | Where the knowledge base has one |
| Shared repositories — where its writing lands in a repository another audience reads | `checkin`, `audit-comments`, `improve-docs` | Where the knowledge base has one |
| Verbatim source — where other parties' own words live | `deliberate`, `slack-log` | Where the knowledge base has one |
| Followed channels — each Slack channel it mirrors, with its ID and any backfill floor | `slack-log` | Where the knowledge base follows Slack |

## Slots

The core fixes these at the knowledge base's root, so no knowledge base declares them and no skill asks where they are. Carrying an ignored one between machines is the knowledge base's own concern, and a knowledge base may keep one of the same name inside a subdirectory of its own. A row names its slot as `` `name/` ``, which is how `core/sync` finds it, and a slot whose row has no Git cell is gitignored.

| Slot | Holds | Git |
|------|-------|-----|
| `code/` | Clones of the external repositories the knowledge base's agents work across | ignored |
| `deliberations/` | One record per `deliberate` run. The run writes it, the session that hears the user's ruling on it appends that ruling verbatim and dated, and nothing else edits it | tracked |
| `scratch/` | Working files, safe for anything to delete | ignored |
| `sessions/` | Agent sessions exported as transcripts | ignored |
| `suggestions/` | One file per skill or root document, a line per change a session saw it needed and did not make | tracked |

## Supply

The core leaves each knowledge base its orchestrators, the skills that sequence others through its own homes, tracking or tests. Each reads its rules at its own step, never from memory of an earlier read.

| Skill | Does | Needed |
|-------|------|--------|
| A writer of documents | Reads `core/RUBRIC.md` | Always |
| A writer of skills or root documents | Reads the suggestions file `suggest` names for each file it changes, deletes each line the change settles, puts each it leaves to the user, and invokes `cold-read` after the change | Always |
| A recording step | Invokes `checkin` | Always |
| A writer of code | Reads `core/IMPLEMENTATION.md` §§1–2 before the first edit, then invokes `audit-comments` | Where the knowledge base writes code |
| A reviewer of code | Reads `core/IMPLEMENTATION.md` §3 | Where the knowledge base reviews code |
| A schedule | Runs `slack-log`'s `sync` over the followed channels | Where the knowledge base follows Slack |
| A mode of `deliberate` | Holds a `role.md`, the deliverable its panel writes, and optionally a `check.md` its critics and check grade against; writes a `seal.txt` where the panel must not read beyond a list; invokes `deliberate` with those paths on its input's first line, and carries the record out once the run returns | Where the knowledge base asks for a deliverable other than a decision |

## Tasks

Every knowledge base runs its tasks through make, so `make help` is the map an agent reads on arrival, and the file every session reads names `make help` as that map. Its root `Makefile` sets the variables `core/kb.mk`'s header names, then `include`s it. `include` rather than `-include`, so a missing core fails loudly. A rule for `core/kb.mk` below the include, which clones the core and runs `core/sync`, lets the first `make` on a fresh checkout restore it; make reads the whole file first, so that rule's recipe must not depend on anything `kb.mk` defines.

## Change

Edit the core through `amend-core`. `core/` is a repository of its own, so its changes never show in the knowledge base's `git status`; `checkin` commits and pushes them there. Two knowledge bases on one machine keep separate checkouts.
