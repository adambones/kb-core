---
name: improve-code
description: Review finished code in one fan-out, apply the fixes that change no contract, and bring back the rest, every proposed cut among them — invoke on a change before or after it merges, or on a path of code as it stands
---

**Input:** `<checkout> [<scope>] [-- <path>…]`

## Target

State the checkout's absolute path in every command and in every agent's prompt,
since an agent inherits the session's directory rather than the target's. Paths
after `--` are the reading paths: other checkouts that use the code under review, which
the reviewers read and nothing in which changes, so a fix that falls in one is
asked.

## Scope

| `<scope>` | What is reviewed |
|---|---|
| omitted | The uncommitted changes, untracked files included; on a clean tree, the branch's commits not on its default branch |
| `<a>..<b>`, a branch or a pull request | That range, a branch or a pull request being read from where it leaves its base |
| a date | Everything since the last commit before it |
| a path | The files under it as they stand, every line counting as changed and none as deleted |

Where a scope finds nothing, stop and say so. Fixes need the checkout at the scope's
last commit, or holding the uncommitted changes under review. Where
it is neither, every fix is asked and the audit is skipped.

## Review

Six fresh agents, one per reviewer below, run in parallel. Hand each the
checkout, the reading paths, the command that produces the scope or the files a
path names, its own angles, and the sections of `core/IMPLEMENTATION.md` they cite,
with §3's preservation inventory as what a contract is. Ask each for every
candidate it can name a scenario or a cost for, the half-believed included, keyed
by `file:line`, with whether the fix would change a contract.

- **Correctness**
  - every changed line and its enclosing function, for the input, state or timing that makes it wrong
  - every deleted or replaced line, for the invariant it held and where the new code holds it
  - every changed function's callers and callees, inside the scope or not, for a precondition, result, error or ordering one of them no longer meets
- **Reuse**
  - new code re-implementing what the codebase already has, found by searching the shared modules and the files beside the change, naming the helper to call instead
- **Simplification**
  - redundant or derivable state, copy-paste with slight variation, deep nesting and dead code, naming the simpler form
  - the red pen in `core/IMPLEMENTATION.md` §3, and every breach of its §1 and of the conventions the repository's code and docs set, quoting the rule and the line
- **Efficiency**
  - repeated work or I/O, independent operations run in sequence, work added to startup or a hot path, and long-lived closures holding scope they do not need, naming the cheaper form
- **Altitude**
  - a symptom patched where a general change to the mechanism beneath it is cheaper, naming that change
  - the structural register in `core/IMPLEMENTATION.md` §3
- **Deletion**
  - every mechanism the change adds, and what would break without it, counting only its users beyond its own tests, in the checkout and the reading paths
  - every hedge: code serving a need that nothing in the checkout or the reading paths has yet
  - except on a path scope, each behaviour the change adds over the code at the scope's start that nothing outside the change asks for, with the lines that carry it

## Sort

Verify each candidate against the code before it counts. Merge duplicates, ask
wherever two fixes contradict, and sort:

- **Applied** — a fix that changes no contract. Unlike a `core/IMPLEMENTATION.md` §3
  review, a defect whose fix restores what the code's comments, tests and
  documents already promise is applied too
- **Asked** — a fix that changes a contract, and every cut the deletion reviewer
  proposes, since what the change is for is not the pass's to decide. Each comes
  back as a decision with what it costs, or for a cut, what it removes
- **Parked** — a remedy §3 would park on its price; one it would leave is dropped

A candidate that fits two takes the more cautious, parked before asked before
applied.

## Apply

Read `core/IMPLEMENTATION.md` §§1–2 before the first fix. Run the repository's tests
before it as well, so a test already red is charged to no fix. Then make the
applied fixes, testing after each or bisecting a batch that turns a test red. A fix
that turns a test red changes a contract after all, so revert it and ask. Where
the tests cannot run here, every fix that touches behaviour is asked.

## Audit once

Invoke `audit-comments` over the scope and the pass's own changes, or over the
pass's changes alone on a path scope. A code fix the audit makes is tested like an
applied fix, and one that changes a contract is asked instead.

## Report

The reply carries the asked and parked fixes, one line for each applied fix that
corrects behaviour and each test already red, and the audit's report. An asked fix
approved later lands through the knowledge base's writer of code. Leave the commit
to the knowledge base's recording step.
