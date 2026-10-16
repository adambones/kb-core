---
name: export-session
description: Write this session out as a labeled Markdown transcript — the user's messages and everything the assistant said, none of its tool calls — for the user to hand another party
---

Run one command, and read neither the transcript nor the file it writes.

    python3 <this skill's directory>/export_session.py <session> --title <title> --out <path> [--user <name>] [--assistant <name>] [--party <name>]...

- **`<session>`** is this session's ID: `${CLAUDE_SESSION_ID}` in Claude Code,
  the conversation ID Antigravity gives the agent, or a transcript path the user
  gave. The script reads Claude Code and Antigravity transcripts only, so under
  any other harness say so and stop
- **`--title`** says in a few words what the session was about
- **`--out`** is an absolute path: the one the user gave, or else
  `sessions/<YYYY-MM-DD>-<topic>.md` under the knowledge base's root, dated today,
  its topic the title lowercased with each run of anything but letters and digits
  made a hyphen and none left at either end
- **`--user`** is the user's name, where the session's instructions give one
- **`--assistant`** is the assistant's name, where it differs from the
  transcript's default: `Claude` for Claude Code, `Gemini` for Antigravity
- **`--party`** names each other party whose reply the user pasted as a message
  of its own, opening with a line holding only that name, so the reply comes out
  under that name

Report the path it prints, or its error verbatim.
