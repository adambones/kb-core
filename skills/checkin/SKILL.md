---
name: checkin
description: Commit and push what the session changed in every repository it touched — invoked by the knowledge base's recording step, or when the user asks for a commit
---

A commit is a pointer to its diff, never a record of the session. Write from the
diff, not from session memory.

1. **Read `MESSAGING.md`.** It holds the writing rules the title and body apply.
   Do not write from memory of them.

2. **Stage.** Only what this session changed — other dirty files belong to
   parallel sessions.
   - **Commit by pathspec — `git commit <paths>`, never a bare `git commit`.** The
     index is shared with every session on the machine, so careful staging is not
     enough: a sibling that has staged its own work lands it in your commit the
     moment you commit the index instead of a list
   - **`core/` is a repository of its own.** An edit made through a link into it
     never shows in the knowledge base's `git status`, so check
     `git -C core status` and commit there like any other repository the session
     touched

3. **Write the commit.**
   - **One line, 72 characters, One Claim.** Squash merges concatenate branch
     titles into the merge body, so each title is a row in an index someone else
     reads. A title that wraps breaks that index
   - **Body empty** unless it carries a fact no artifact can: `Closes #N`, a
     cross-repo pointer, a revert reason, an ordering or cherry-pick constraint.
     A cross-repo pointer keeps the full `org/repo#n` form, which GitHub
     autolinks
   - **No trailers** — no Co-Authored-By, no Generated-with
   - **A repository the shared-repository binding names**, where the knowledge
     base declares one: run its formatter first, then write as if a human
     engineer made the change — never reference sessions, agents, reviews, or AI
     processes. Match the host repo's log dialect

4. **Push.** For each repo committed above: `git pull --no-rebase`, then
   `git push`. Merge, not rebase — pass `--no-rebase` explicitly, because a
   machine's `pull.rebase` default is often `true` and rebasing over another
   machine's pushed commits jams per-commit where a merge resolves in one pass.
   Never `--force`. A merge conflict stops for attended resolution. A rejected
   push stops for the user — never reset or re-parent.

5. **Report** what was committed, where, and whether each push landed. A
   `core/` commit gets its own line, since every knowledge base inherits it.
