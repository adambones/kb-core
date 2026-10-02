---
name: export-thread
description: Write this Claude Code session out as a Markdown conversation — the user's messages and the reply each turn ends with, none of the work behind them — for the user to hand another party
---

Run one command, and read neither the transcript nor the file it writes.

    python3 "${CLAUDE_SKILL_DIR}/export_thread.py" ${CLAUDE_SESSION_ID} [--user <name>] [--party <name>]... [--out <path>]

- **`--user`** is the user's name, where the session's instructions give one
- **`--party`** names each other party whose reply the user pasted as a message
  of its own, opening with a line holding only that name, so the reply comes out
  under that name
- **`--out`** is the path the user gave, and is omitted otherwise

Report the path it prints, or its error verbatim.
