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

A knowledge base that cannot push to the core binds a read-only core. There `core/sync` links every skill but `amend-core`, denies Claude Code's edits under `core/` in `.claude/settings.json`, and resets the checkout to the core's remote at each pull, deleting what the core does not track and printing each edit, file and commit it drops.

Turn agent memory off in each agent's settings (No Memories). In Claude Code that is `"autoMemoryEnabled": false` in `.claude/settings.json`.

`core/sync` also installs `core/hooks/commit-gate.py` in `.claude/settings.json`, where Claude Code refuses a commit, a push or a new pull request unless `checkin` is the session's latest skill. A knowledge base whose recording step commits or opens pull requests itself passes that skill's name as an argument after the hook's path there.

Run each agent in its auto mode, which proceeds on routine work and asks only before an irreversible action, since the skills run unattended. In Claude Code that is `"defaultMode": "auto"` under `permissions` in `~/.claude/settings.json`, for every project on the machine since a project's own settings cannot start it, or Auto in the desktop app's mode selector, which keeps it per folder. In Antigravity it is Agent Mode `auto` in `/config`, one setting for every workspace on the machine.

Start the knowledge base's documents from the core alone. Seeding it with another knowledge base's documents imports that one's traits into a new domain.

## Bind

`AGENTS.md`, the file every session reads, declares each role below under a Bindings heading, and says that only `checkin` commits and pushes, since a client the commit gate does not reach learns it nowhere else; `core/sync` flags an `AGENTS.md` that never names `checkin`. Claude Code reads it only where no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` sits in the directory a session starts in or any above it ([Claude Code's AGENTS.md support](https://code.claude.com/docs/en/memory#agents-md)), so none sits at or above the knowledge base's root.

| Role | Asked for by | Needed |
|------|--------------|--------|
| Source of truth | `core/RUBRIC.md`, `deliberate`, `counsel`, `teach-me` | Always |
| Homes | `core/RUBRIC.md` | Always |
| Lifecycles | `core/RUBRIC.md`, `deliberate`, `counsel`, `audit-comments`, `improve-docs` | Always |
| Slots | `core/RUBRIC.md` | Always |
| Audience — who messages reach | `core/MESSAGING.md`, `distill` | Always |
| Product truth — what the product is | `deliberate`, `counsel`, `distill` | Where the knowledge base has one |
| Shared repositories — where its writing lands in a repository another audience reads | `checkin`, `audit-comments`, `improve-docs` | Where the knowledge base has one |
| Verbatim source — where other parties' own words live | `deliberate`, `counsel`, `slack-log` | Where the knowledge base has one |
| Followed channels — each Slack channel it mirrors, with its ID and any backfill floor | `slack-log` | Where the knowledge base follows Slack |
| Read-only core — the core's remote, which it pulls and cannot push to | `core/sync`, `suggest` | Where the knowledge base cannot push to the core |

## Slots

The core fixes these at the knowledge base's root, so no knowledge base declares them and no skill asks where they are. Carrying an ignored one between machines is the knowledge base's own concern, and a knowledge base may keep one of the same name inside a subdirectory of its own. A row names its slot as `` `name/` ``, which is how `core/sync` finds it, and a slot whose row has no Git cell is gitignored.

| Slot | Holds | Git |
|------|-------|-----|
| `code/` | Clones of the external repositories the knowledge base's agents work across | ignored |
| `deliberations/` | One record per `deliberate` or `counsel` run. The run writes it, the session that hears the user's ruling on it appends that ruling verbatim and dated, and nothing else edits it | tracked |
| `scratch/` | Working files, safe for anything to delete, each top-level entry named for what it serves. `core/sync` deletes an entry once nothing in it has changed for 14 days | ignored |
| `sessions/` | Agent sessions exported as transcripts | ignored |
| `suggestions/` | One file per skill or root document of the knowledge base's own, a line per change a session saw it needed and did not make. The core's skills and documents keep theirs in `core/suggestions/`, or in `suggestions/core/` where the knowledge base binds a read-only core | tracked |

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
| A mode of `deliberate` or `counsel` | Holds a `role.md`, the deliverable its panel writes, and optionally a `check.md` its skill grades the panel's work against; writes a `seal.txt` where the panel must not read beyond a list; invokes its skill with those paths on its input's first line, and carries the record out once the run returns | Where the knowledge base asks for a deliverable other than the skill's own |

## Tasks

Every knowledge base runs its tasks through make, so `make help` is the map an agent reads on arrival, and the file every session reads names `make help` as that map. Its root `Makefile` sets the variables `core/kb.mk`'s header names, then `include`s it. `include` rather than `-include`, so a missing core fails loudly. A rule for `core/kb.mk` below the include, which clones the core and runs `core/sync`, lets the first `make` on a fresh checkout restore it; make reads the whole file first, so that rule's recipe must not depend on anything `kb.mk` defines.

## Change

Edit the core through `amend-core`, except `core/suggestions/`, which `suggest` appends to from any knowledge base that can push to the core. `core/` is a repository of its own, so its changes never show in the knowledge base's `git status`; `checkin` commits and pushes them there. Two knowledge bases on one machine keep separate checkouts.
