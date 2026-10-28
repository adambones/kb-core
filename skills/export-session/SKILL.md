---
name: export-session
description: Write this session out as a labeled Markdown transcript of its dialogue, none of its tool calls, for the user to hand another party, headed by the command that reopens the session
---

Run one command, and read neither the transcript nor the file it writes. In
Antigravity run it with `BypassSandbox`, since inside the terminal sandbox it
can neither find the transcript nor write the file.

    python3 <this skill's directory>/export_session.py <session> --title <title> --out <path> [--user <name>] [--assistant <name>] [--party <name>]...

- **`<session>`** is this session's ID: `${CLAUDE_SESSION_ID}` in Claude Code,
  `${CODEX_THREAD_ID}` in Codex, the conversation ID Antigravity gives the agent,
  or a transcript path the user gave. The script reads Claude Code, Codex and
  Antigravity transcripts, so under
  any other harness say so and stop
- **`--title`** says in a few words what the session was about
- **`--out`** is an absolute path: the one the user gave, or else the
  knowledge base's `sessions/` folder with a trailing slash, in which the script
  names the file for today, the title and the model that wrote most replies.
  Where the folder already holds an export of this session, the script
  overwrites that instead
- **`--user`** is the user's name, where the session's instructions give one
- **`--assistant`** is the assistant's name, where it differs from the
  transcript's default: `Claude` for Claude Code, `Codex` for Codex, `Gemini` for Antigravity
- **`--party`** names each other party whose reply the user pasted as a message
  of its own, opening with a line holding only that name, so the reply comes out
  under that name

Report the path it prints, or its error verbatim.
