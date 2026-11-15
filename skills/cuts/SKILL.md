---
name: cuts
description: Price a change or a plan by the requirements that forced its weight, and return a lettered menu of cuts the user answers by letter — invoke on a commit, a range, a branch or a plan the user names
---

**Input.** The target and the user's words about it.

1. **Measure the target** once, into `scratch/cuts-<YYYY-MM-DD>-<target>.md`: the checkout that holds it and the refs it is read at as they stand locally, a branch from its merge base with the default branch, and for code `git diff --numstat` over those refs; for a plan, its path and the commit it is read at.
2. **Invoke `deliberate`** with this skill's `role.md` and that file on the input's first line, and the user's words as the ask.
3. **Carry out the answer.** Return the record's path and the menu's opening. Each letter the user takes enters the knowledge base's home for work in flight as the requirement it changes; the record stays as the run wrote it.
