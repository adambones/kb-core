---
name: audit-comments
description: Cold-read the diff's comments after implementation — prune what does not orient a reader, lift what the author wrote to reassure itself, and report the hot points
---

The diff is finished and unread. This pass is the user's introduction to it: the
comments are where the change is load-bearing, so an index of them is an index of
what they have to understand. Run it once the code is written, before anything is
written to the knowledge base's home for work in flight.

Two things come out. Comment edits land in the code, and a report lands in the
session's reply. No new file — nothing here earns a home.

## Authority

The cold reader reports and changes nothing. It cannot tell a real defect from a
constraint it was never shown, so a real defect comes back as a proposal like
everything else.

Fixing what it surfaces is yours. A constraint you cannot state simply is usually
a seam that is actually wrong, which is why a comment pass finds bugs at all, and
a known defect left in the diff to honour a scope boundary serves nobody. The
condition is that the fix is announced — its own entry in the report, named as a
code change rather than a comment one. An unreported behaviour change riding
inside a pass called audit is the one thing the user's diff review cannot see
coming.

## The cold half goes to a fresh agent

An author cannot cold-read its own comments (**Cold Reader**, `core/RUBRIC.md` §1).
Spawn a fresh agent —
never a conversation fork, which inherits this context and is the same warm reader
wearing a hat. Hand it the diff and the comment rules from
`core/IMPLEMENTATION.md` §2, and nothing else. Not the conversation, not the
design, not what the change is for. Its blindness is the instrument.

One thing joins the handout when the diff is in a repository the knowledge base's
**shared-repository binding** names, where it declares one: the rules that binding
sets for writing there. A comment naming the knowledge base, anything in it, or the
user's own reading reads as ordinary context to an agent never told there is a
boundary, so the cold read passes it through and the leak ships.

Ask it for three things, keyed by `file:line`:

- **The question.** The Cold Reader question turned on a comment that already exists:
  name the question the finished file asks that this one answers. A comment it
  cannot name a question for is proposed for deletion. Never ask it to justify a
  comment — justification is available for anything, and the pass comes back
  unanimously clean.
- **Voice.** Each survivor against the format, voice and tense rules it was handed,
  and against the shared-repository binding's rules where they apply.
- **The missing bookmark.** Lines the diff makes load-bearing that carry no
  comment. This is the half of the audit an inventory of what got written cannot
  reach, and it is the more expensive miss: a hot point with no comment on it is a
  hot point the user walks past.

One agent over the whole diff. A diff too large for that is a change that should
have been smaller, and fanning out buys coverage at the price of the cross-file
read.

## It proposes, you dispose

A cold reader judges whether a comment is *needed* and how it *reads*. It cannot
judge whether the comment is *true* — it does not know the constraint is real. Left
to delete on its own authority it strips the very insight a comment exists to
capture, so every deletion is a proposal. Where you keep a comment it wanted gone,
the disagreement is a line in the report.

## The warm half is yours alone

Sort what survives into two species. The first orients a reader and stays in the
code.

The second is the **Reassurance Comment**: the line written to settle the author
rather than orient the reader. It fails the voice and tense rules both, so a strict
audit deletes it silently. Do not. It marks the seam you were least sure of, which
is the highest-signal thing in the diff, and it is only visible from inside the
session that wrote it — no cold reader can recover it.

So it comes out of the code and goes into the report as what it actually was: the
place you were guessing. From there it graduates like anything else, into the
knowledge base's home for work in flight, or into its home for test risks where it
keeps one and the seam is a risk rather than a smell.

## The report

The diff is the reading surface. Two things go into the reply, because the diff
cannot show them:

- **The smell index.** Each reassurance comment, lifted out of the code and stated
  as what it was — the place you were guessing. One line each.
- **Declined findings.** A proposal you overrode, or a hole you left open, with the
  reason. One line each.

A code fix made off the back of a finding is its own entry — `file:line`, what was
wrong, what changed — and this is the only announcement it gets.

Nothing else goes in. Not the comments you rewrote, deleted or added, and not the
bookmarks you filled: those are in the diff, and the user reads the diff. Where the
smell index is empty and nothing was declined, the report is no section at all.
