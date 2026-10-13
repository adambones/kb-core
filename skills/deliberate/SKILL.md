---
name: deliberate
description: Answer a deep-think exchange with a panel of fresh agents in place of an outside deep-think agent — proposers working apart from opposed stances, a critic for each, and a judge — invoke when the user gives instructions for the panel
---

**Bindings.** Session correspondence, where the brief and the panel's answer are
published; where it is undeclared, both are your reply.

A panel spends more on one question than a single reader would, to buy what a
single reader lacks: answers that did not start from each other, each broken
against the source before one is chosen. Its agents write no file.

## Build the exchange

Invoke `build-deepthink`, or the mode the ask fits, and follow it through its
checks under a stem ending `-panel`, so that a session building the same
exchange for an outside agent, which may answer under the plain stem, never
writes over this one. The bundle is the same file an outside agent would read,
and every agent in the panel reads it first. Its partition holds for the stances
as well: none carries your solution, since a panel handed it argues inside it.

## The brief is the go

Publish the brief as `build-deepthink` §Publish the brief says, adding the
stances, one line each, and the size, then stop until the user answers it.
Nothing runs before they have read it. A reply that corrects the brief is
applied, the bundle rebuilt where a note changed, and the brief published again.
One that asks or objects is answered first. The panel runs on a reply that leaves
the brief standing.

## Stances and size

Choose the stances from the ask and the notes, so that no two converge by
default:

- **The generator**, always: the boldest answer it can defend from the source. It
  states what its answer costs, and neither cost, migration nor the present
  design rules an option out. The critics carry the rigour, so the licence costs
  nothing when it is wrong
- **The present design**, where one exists: the best answer that keeps it
- **Against**, for each plan the ask or the notes name: the strongest answer that
  rejects it
- The rest from the axes the problem turns on

A mode whose role returns a plan or tests rather than a choice takes its stances
from the angles that role leaves open.

Four proposers, or one per stance where the plans named need more, unless the
user sets the size. Proposers and the judge run at the highest reasoning effort
the host offers and critics one step below, unless the user sets it.

## Run the panel

Every agent is fresh, never a fork of this conversation. Hand each the absolute
paths of the knowledge base's root and of the bundle, and tell it to read the
bundle first, then any source it needs, and never the session correspondence or
a file under `scratch/<stem>/` that you did not name to it. Write what each
returns to `scratch/<stem>/pass-<n>/`, named for its stance, as it arrives, and
name those paths to the stage that reads them, so nothing a later stage needs
lives only in your context.

1. **Propose.** Launch every proposer at once, each handed its own stance and
   none another's. Ask for the answer in the form the bundle's role asks for,
   with the path behind every claim about the source.
2. **Attack.** Launch one critic as each proposal arrives, handed that proposal
   and its stance and no other. Its task replaces the role the bundle hands its
   reader: confirm or refute each claim with the path and lines that decide it,
   name the strongest objection to the whole, and for each refuted claim the
   answer rests on, say what would have to be true for it to hold.
3. **Judge.** One agent, handed every proposal with its stance and critique, and
   nothing of yours beyond the bundle. It chooses, takes what is strong from the
   answers it did not choose, and writes the answer the bundle's role asks for.

## The answer

The judge's answer is the exchange's answer, under the party name
`<your name> panel`, and is checked and published as `build-deepthink` §When the
answer comes back says. The proposals and critiques stay in scratch.

Another pass rebuilds as `build-deepthink` §Another pass says, adding no file
that only a panel agent read, and runs the panel again once the user has read
that pass's brief. Its stances and size stand unless the user changes them.
