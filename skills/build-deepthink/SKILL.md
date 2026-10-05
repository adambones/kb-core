---
name: build-deepthink
description: Bundle a brief and its context for a deep-think agent that reads one text input and has no filesystem, whose answer you then check against the source
---

**Bindings.** Outbound files, where the bundle is written; where it is undeclared,
ask for a path. Session correspondence, where the brief is published; where it is
undeclared, the brief is your reply.

The deep-think agent generates: it reads the bundle once, reasons at length and
answers. You are the agent on the ground. You choose what it reads, and its answer
comes back to be checked against the source of truth, so the bundle has to make it
as effective as a reader sitting in the repository. Where you were not oriented on
the subject this session, read its home for work in flight first.

## Modes

A mode is a skill holding a `deepthink.md`, the role the deep-think agent takes in
that kind of exchange, and optionally a `spar.md`, the checklist its answer is
checked against. A mode's skill scopes the exchange and says what to pack, hide
and ask for beyond the steps below, and where it replaces a step its rules win,
its own checks included. Invoked directly, this skill builds an exchange that ends
in a decision, under its own `deepthink.md`.

## The stem

Name the exchange with a short kebab-case stem, following whatever convention the
knowledge base sets for naming its work, and state it without asking. Ask only
where the answer would change the include list and the conversation does not
settle it. Three files in the outbound slot share the stem:

    .<stem>-include.txt       what the bundle holds
    .<stem>-instructions.md   the directive
    <stem>-prompt.md          the bundle the user uploads

The dot keeps the two inputs out of a file browser that hides dotfiles, so it
shows only what gets uploaded.

## Partition what you know

By now you have likely investigated and have a solution in mind. The constraints
you found go into the bundle. The solution stays out of it, where it would anchor
the answer on yours; keep it for when the answer comes back, in the session's
correspondence where the knowledge base keeps one.

## The include list

The budget is 200K characters of file contents, about 50K tokens, because
attention degrades well before the context fills. Over it, trim generated output
first, then keep one or two representative neighbours rather than every one,
excerpt a long file into a working copy outside the outbound slot that holds only
the sections that matter, and cut the least essential category. Under it, do not
pad.

Build the list outside-in from these categories, considering every one and
skipping one only where nothing qualifies or the budget forces the cut. Never
adapt a neighbouring exchange's list, which inherits that exchange's boundaries.

1. **Orientation** — whatever shows the agent what kind of thing it is looking
   at, from that thing's own structure rather than prose about it
2. **Seeds** — the files at the centre of the task
3. **Contracts** — every definition the seeds depend on or must conform to
4. **An exemplar** — at least one existing artifact that follows the pattern the
   seeds follow, so the agent can judge whether it was followed
5. **Neighbours** — what uses the seeds, and what they use, one step out
6. **Rationale** — the settled docs and premises that explain why it is shaped
   this way
7. **Work in flight** — every document in the knowledge base's home for work in
   flight on the subject. It is the primary grounding, so the directive points at
   it rather than restating it
8. **Conditions** — what the seeds depend on that their references do not show
9. **The asks** — the requests behind the work, wherever the knowledge base tracks
   them

A rubric goes in only where the exchange generates or grades the artifact it
governs, and then whole, since whoever checks the answer reads the same file and
a restated copy is where the two drift apart.

Every bundle includes `core/skills/build-deepthink/roles.md` and exactly one
`deepthink.md`: the mode's, or this skill's.

Only text reaches the bundle. A binary seed goes to the agent as an upload of its
own, where its chat accepts one.

Write `.<stem>-include.txt` with one path or glob per line, relative to the
knowledge base's root. A `#` line is a comment for whoever maintains the list and
never reaches the agent. A line starting `-` excludes a pattern, and one starting
`!` includes a pattern past the default exclusions, which are hidden files and
tool caches.

## The directive

Write `.<stem>-instructions.md`, which the bundle carries as
`<user_instructions>`. The bundle carries a file map, and the role files say who
the agent is and who checks it, so the directive carries only the exchange:

- **Problem** — what is wrong or wanted, and how it shows
- **Constraints** — what you found that the bundle does not already say. Where a
  bundled document covers it, point there
- **Desired outcome** — what done looks like
- **Exit condition** — what the exchange is for and where it should stand when it
  ends: a decision taken, a design settled, a plan ready to run
- **Notes on files**, only where the map alone misleads: which files are the work
  product and which are reference, and why an exemplar is there
- **Specific concerns**, where there are any

## Build

From the knowledge base's root, without asking:

    python3 core/skills/build-deepthink/bundle.py --stem <stem> --out <outbound slot>

A change to the directive later is a rerun, not a decision.

## Before publishing

Read back the two inputs and the bundle's file map, and check:

- the orientation files establish what kind of thing this is from the bundle
  alone
- every seed is there, and every exemplar the mode asks for
- `roles.md` and one `deepthink.md` are in the map
- the rationale for every system touched, and the work-in-flight documents, are
  bundled rather than restated
- the directive states problem, constraints, outcome and exit condition without
  prescribing a solution
- the content size the build prints is within budget
- the build printed no warning, since each one names files the bundle left out

## Publish the brief

Publish the brief where the knowledge base keeps session correspondence, under the
rules of the skill that keeps it, naming the stem, which is what ties the answer
back to this exchange. Where the brief is your reply, name the bundle's path too,
since nothing else tells the user which file to upload.

The brief is what you decided and the user has not otherwise read: the directive's
problem, constraints, outcome, exit condition and concerns, or what the mode's
skill says its brief carries. A sentence whose subject is the bundle rather than
the problem stays out, and so does any other report of the build, since its size
changes no decision. A gap that does — no exemplar exists, a doc the exchange needs
is missing — goes in the brief, marked as a gap.

## When the answer comes back

Check each concrete claim against the source of truth before anything acts on it,
and reply as a peer with what you found, at most three times. Where the knowledge
base supplies a skill for this, it runs instead, and a mode's `spar.md` is the
checklist it reads.
