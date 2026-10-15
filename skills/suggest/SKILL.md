---
name: suggest
description: Queue one line of feedback on a skill or root document without changing it — invoke when one stalled, misled or slowed this session and changing it now would take you off the work in hand
---

1. **Name the target**: the skill, or the document at the root of the
   knowledge base or of the core, whose text would change, and the step or
   sentence in it.
2. **Read `suggestions/<target>.md`**, the target being the skill's name, the
   name of a document at the knowledge base's root without `.md`, or `core-`
   and that name for one at the core's root. A line already saying the same
   takes no second, and a line this one contradicts is replaced, the later
   session having seen more.
3. **Append one line**, for a reader who never had this session:

       - <YYYY-MM-DD> · ${CLAUDE_SESSION_ID} · <step or sentence> — <what happened> → <what would have served>

   What happened is what the session saw, never a cause it did not test.
4. **Return to the work.** The target changes later, through whatever writes
   it, which reads this file first. The commit is the recording step's.
