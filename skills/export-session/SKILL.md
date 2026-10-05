---
name: export-session
description: Write this Claude Code session out as a labeled Markdown transcript — the user's messages and everything Claude said, none of its tool calls — for the user to hand another party
---

Run one command, and read neither the transcript nor the file it writes.

    python3 "${CLAUDE_SKILL_DIR}/export_session.py" ${CLAUDE_SESSION_ID} --title <title> --out <path> [--user <name>] [--party <name>]...

- **`--title`** says in a few words what the session was about
- **`--out`** is an absolute path: the one the user gave, or else
  `sessions/<YYYY-MM-DD>-<topic>.md` under the knowledge base's verbatim source,
  dated today, its topic the title lowercased with each run of anything but letters
  and digits made a hyphen. Where there is neither, ask the user for a path
- **`--user`** is the user's name, where the session's instructions give one
- **`--party`** names each other party whose reply the user pasted as a message
  of its own, opening with a line holding only that name, so the reply comes out
  under that name

Report the path it prints, or its error verbatim.
