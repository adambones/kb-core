---
name: cold-read
description: Grade a changed skill or root document through a fresh agent that never had the session — run after every change to one
---

A writer cannot grade what it wrote (**Cold Reader**, `core/RUBRIC.md` §1).

1. **Spawn a fresh agent**, never a fork of this conversation. It reports and
   edits nothing.

2. **Hand it what each changed file's reader has in view**, each file named with
   the reader it is written for, and tell it to read nothing else:
   - every changed file, marked, with what changed in it
   - every file or skill a changed file tells its reader to read or invoke, one
     hop
   - every skill in this knowledge base and the core that invokes a changed skill
     or reads a changed file, found by searching both for its name, since an edit
     to a shared contract breaks there
   - `core/RUBRIC.md`, and every other document in the core where a changed
     file is in the core
   - the file every session reads

3. **Ask for these, keyed by sentence in each changed file**, a finding on text
   the change did not touch marked as standing:
   - the question from that file's reader each sentence answers, or none
   - every sentence that restates another, in any file handed over
   - every pair of sentences that cannot both be followed, in any file handed
     over
   - every breach of **No Examples** (`core/RUBRIC.md`)

   For a changed skill:
   - every point where, walking its steps cold, it would stall, guess or need
     something from outside the files handed over
   - every mode that acts on an artifact the rest of the skill does not, which is
     a skill of its own

   For a changed file in the core:
   - every noun of one knowledge base's own, which the core cannot name

   For a changed script:
   - what it does that its documentation would not lead a reader to expect
   - any way it could damage what it runs in

4. **Dispose.** Apply what you accept. A fix made here is part of the change this
   read graded, not a change of its own to read again. A
   finding you decline stands only until the person reading your report rules on
   it, so each is a line there with its reason.
