---
name: suggest
description: Queue one line of feedback on a skill or root document without changing it — invoke when one stalled, misled or slowed this session and changing it now would take you off the work in hand
---

1. **Name the target**: the skill, or the document at the root of the
   knowledge base or of the core, whose text would change, and the step or
   sentence in it.
2. **Read its suggestions file where it exists**: `core/suggestions/<target>.md`
   where the target resolves into `core/`, a skill linked from it included,
   and `suggestions/<target>.md` otherwise, the target being the skill's
   name or the document's name without `.md`. A line already saying the same
   takes no second, and a line this one contradicts is replaced, the later
   session having seen more.
3. **Append one line**, for a reader who never had this session:

       - <YYYY-MM-DD> · <session-id> · <step or sentence> — <what happened> → <what would have served>

   `<session-id>` is this session's ID: `${CLAUDE_SESSION_ID}` in Claude Code,
   `${CODEX_THREAD_ID}` in Codex, the conversation ID Antigravity gives the
   agent, or `unknown` where the harness gives none. A line in the core's file
   is read from other knowledge bases, so it adds the name of this one's root
   directory as a field before the ID, the one place the session resumes, and
   names no other noun of this knowledge base's own. What happened is what the
   session saw, never a cause it did not test.
4. **Return to the work.** The target changes later, through whatever writes
   it, which reads this file first. The commit is the recording step's.
