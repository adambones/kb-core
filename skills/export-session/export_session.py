#!/usr/bin/env python3
import argparse
import glob
import json
import mimetypes
import os
import re
import sys

SELF_COMMANDS = ("/export-session", "$export-session")
# Keyed by harness, each named for the assistant its transcripts default to
RESUME = {"Claude": "claude --resume", "Gemini": "agy --conversation", "Codex": "codex resume"}
# The harness fences a paste in tags of its own, which are not the user's words
PASTE_FENCE = re.compile(r"</?pasted_content[^>]*>")
# A message that is only a path as drag and drop leaves it, bare or after /transcribe
HANDOFF = re.compile(r"(/transcribe\s+)?('[^']+'|\"[^\"]+\"|(?:\\.|\S)+)")
# A rule parts transcribe's mirror from any answer that follows
RULE = re.compile(r" {0,3}([-*_])(?: *\1){2,} *")
# transcribe's speaker label
SPEAKER = re.compile(r"\*\*([^*\n:]+):\*\*[ \t]*")


def records(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                # A live session can be mid-write on its last line
                continue


def find_transcript(session):
    if os.path.isfile(session):
        first = next(records(session), {})
        if first.get("type") == "session_meta":
            harness = "Codex"
        else:
            # Antigravity records carry step_index at the top level, where Claude Code's carry none
            harness = "Gemini" if "step_index" in first else "Claude"
        return session, harness, session_of(session, harness)
    # A Claude Code session files under the directory it started in, which the id does not name
    claude_root = os.environ.get("CLAUDE_CONFIG_DIR", os.path.expanduser("~/.claude"))
    # Escaped, so an id holding a wildcard cannot export another session's transcript
    matches = glob.glob(os.path.join(claude_root, "projects", "*", f"{glob.escape(session)}.jsonl"))
    if matches:
        return matches[0], "Claude", session
    # Antigravity files under Gemini's home, in a directory per client
    gemini_root = os.path.expanduser("~/.gemini")
    # The full log holds every line the other truncates
    for name in ("transcript_full.jsonl", "transcript.jsonl"):
        matches = glob.glob(os.path.join(gemini_root, "*", "brain", glob.escape(session), ".system_generated", "logs", name))
        if matches:
            return matches[0], "Gemini", session
    codex_root = os.environ.get("CODEX_HOME", os.path.expanduser("~/.codex"))
    for folder in ("sessions", "archived_sessions"):
        matches = glob.glob(os.path.join(glob.escape(codex_root), folder, "**", f"rollout-*-{glob.escape(session)}.jsonl"), recursive=True)
        if len(matches) > 1:
            sys.exit(f"export-session: multiple Codex transcripts for session {session}; pass a transcript path")
        if matches:
            return matches[0], "Codex", session
    sys.exit(f"export-session: no transcript for session {session} under {claude_root}/projects, {gemini_root}/*/brain or {codex_root}")


# A moved transcript keeps no id, since a wrong one would reopen another session
def session_of(path, harness):
    if harness == "Codex":
        return next((r.get("payload", {}).get("id") for r in records(path) if r.get("type") == "session_meta"), None)
    if harness == "Claude":
        return next((r["sessionId"] for r in records(path) if "sessionId" in r), None)
    # Antigravity records carry none, so only the conversation folder above .system_generated names it
    parts = os.path.abspath(path).split(os.sep)
    return parts[-4] if parts[-3:-1] == [".system_generated", "logs"] else None


def origin_kind(holder):
    return (holder.get("origin") or {}).get("kind")


def filter_command(raw):
    command = re.search(r"<command-name>(.*?)</command-name>", raw, re.S)
    if command is None:
        text = PASTE_FENCE.sub("", raw).strip()
        return None if any(text == name or text.startswith(name + " ") or text.startswith(name + "\n") for name in SELF_COMMANDS) else text
    name = command.group(1).strip()
    if name in SELF_COMMANDS:
        return None
    args = re.search(r"<command-args>(.*?)</command-args>", raw, re.S)
    return f"{name} {args.group(1).strip() if args else ''}".strip()


def human_text(content):
    if isinstance(content, str):
        return filter_command(content)
    parts = []
    for block in content or []:
        if block.get("type") == "text":
            filtered = filter_command(block["text"])
            # A self-command in any block makes the whole message the export's own
            if filtered is None:
                return None
            if filtered:
                parts.append(filtered)
    images = [block for block in content or [] if block.get("type") == "image"]
    # A pasted image leaves a numbered marker in the prompt, so only a message carrying none gets ours
    if images and not any("[Image #" in part for part in parts):
        parts += ["[image]"] * len(images)
    return "\n\n".join(parts)


def antigravity_text(record):
    raw = record.get("content") or ""
    # Antigravity appends IDE metadata after the prompt, none of it the user's words
    request = re.search(r"<USER_REQUEST>\n?(.*?)\n?</USER_REQUEST>", raw, re.S)
    return human_text(request.group(1) if request else raw)


def speaker_of(text, user, parties):
    # A pasted reply arrives under a line holding only its author's name
    first, _, rest = text.partition("\n")
    if first.strip() in parties and rest.strip():
        return first.strip(), rest.strip()
    return user, text


def codex_text(content):
    parts = []
    for block in content or []:
        kind = block.get("type", "").lower()
        if kind == "text":
            parts.append(block.get("text", ""))
        elif kind in ("image", "localimage"):
            parts.append("[image]")
    return "\n\n".join(parts).strip()


def read_codex_session(path, user, assistant, parties):
    turns, reply, humans, exporting = [], [], 0, False

    def flush():
        if reply and not exporting:
            turns.append((assistant, "\n\n".join(reply)))
        reply.clear()

    # UI events distinguish dialogue from injected context and its duplicate model inputs
    for record in records(path):
        if record.get("type") != "event_msg":
            continue
        payload = record.get("payload") or {}
        kind = payload.get("type")
        item = payload.get("item") or {}
        if kind == "item_completed":
            role = {"UserMessage": "user", "AgentMessage": "assistant"}.get(item.get("type"))
            text = codex_text(item.get("content")) if role else ""
        elif kind in ("user_message", "agent_message"):
            role = "user" if kind == "user_message" else "assistant"
            text = (payload.get("message") or "").strip()
            if role == "user" and (payload.get("images") or payload.get("local_images")):
                text = (text + "\n\n[image]").strip()
        elif kind in ("task_complete", "task_aborted", "turn_aborted"):
            flush()
            exporting = False
            continue
        else:
            continue
        if role == "user":
            text = human_text(text)
            flush()
            exporting = text is None
            if text:
                humans += 1
                turns.append(speaker_of(text, user, parties))
        elif role == "assistant" and text:
            reply.append(text)
    if humans == 0:
        sys.exit(f"export-session: no message in {path} came from the user; the transcript format may have changed")
    # An open turn can contain the export command's own progress messages
    return turns


def read_session(path, user, assistant, parties):
    turns, reply, humans, exporting, waiting = [], [], 0, False, False

    def flush():
        # An export's own turn replies with nothing but the file it wrote
        if reply and not exporting:
            turns.append((assistant, "\n\n".join(reply)))
        reply.clear()

    def end_turn():
        nonlocal exporting
        flush()
        exporting = False

    def said(text):
        nonlocal humans
        if text:
            humans += 1
            turns.append(speaker_of(text, user, parties))

    for record in records(path):
        # Subagent traffic
        if record.get("isSidechain"):
            continue
        kind = record.get("type")
        source = record.get("source")
        if kind == "assistant":
            message = record.get("message") or {}
            # The harness's stand-ins for a reply the model never gave
            if record.get("isApiErrorMessage") or message.get("model") == "<synthetic>":
                continue
            # A turn often answers before it works and ends on a status line, so all of its text is the reply
            for block in message.get("content") or []:
                if block.get("type") == "text" and block["text"].strip():
                    reply.append(block["text"].strip())
                elif block.get("type") == "tool_use":
                    waiting = True
        elif kind == "user":
            content = (record.get("message") or {}).get("content")
            if isinstance(content, list) and all(block.get("type") == "tool_result" for block in content):
                waiting = False
                continue
            # Injected context continues a turn, where any other input opens one
            if not record.get("isMeta"):
                end_turn()
            if origin_kind(record) == "human":
                text = human_text(content)
                if text is None:
                    exporting = True
                else:
                    said(text)
        elif kind == "attachment":
            attachment = record.get("attachment") or {}
            # A message typed while Claude Code works is absorbed into the running turn instead of stored as a user record
            if attachment.get("type") == "queued_command" and origin_kind(attachment) == "human":
                # What the turn said before the message arrived answered what came before it
                flush()
                said(human_text(attachment.get("prompt")))
        # Antigravity's planner replies and calls tools in one record
        elif kind == "PLANNER_RESPONSE" and source == "MODEL":
            text = (record.get("content") or "").strip()
            if text:
                reply.append(text)
            if record.get("tool_calls"):
                waiting = True
        # Antigravity logs a tool's result under the model's name, so it ends the wait without a reply
        elif kind == "GENERIC" and source == "MODEL":
            waiting = False
        elif kind == "USER_INPUT" and source == "USER_EXPLICIT":
            end_turn()
            text = antigravity_text(record)
            if text is None:
                exporting = True
            else:
                said(text)
    # A turn still waiting on a tool when the transcript ends is the one running this export
    if not waiting:
        end_turn()
    if humans == 0:
        sys.exit(f"export-session: no message in {path} came from the user; the transcript format may have changed")
    return turns


def handoff(text):
    match = HANDOFF.fullmatch(text.strip())
    if match is None:
        return False
    if match.group(1):
        return True
    # A bare path hands over a recording only, since any other file comes with a question of its own
    path = re.sub(r"\\(.)", r"\1", match.group(2).strip("'\""))
    return (mimetypes.guess_type(path)[0] or "").startswith(("audio/", "video/"))


def mirror_of(reply):
    lines = reply.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith(">")), None)
    if start is None:
        return None
    end = start
    while end < len(lines) and (lines[end].startswith(">") or not lines[end].strip()):
        end += 1
    if end < len(lines) and not RULE.fullmatch(lines[end]):
        return None
    # Whatever precedes the mirror only fetched the words, so it drops out with the command it answered
    mirror = "\n".join(re.sub(r"^> ?", "", line) for line in lines[start:end]).strip()
    # With no answer to rule it off, only a speaker's label tells a mirror from any other quote
    if end == len(lines) and not SPEAKER.match(mirror):
        return None
    return mirror, "\n".join(lines[end + 1:]).strip()


def voices(mirror, user):
    turns = []
    for line in mirror.splitlines():
        match = SPEAKER.match(line)
        if match:
            turns.append((match.group(1).strip(), [line[match.end():]]))
        elif turns:
            turns[-1][1].append(line)
        # transcribe labels no one in a recording of the user alone, so unlabelled words are theirs
        else:
            turns.append((user, [line]))
    return [(speaker, "\n".join(lines).strip()) for speaker, lines in turns if "".join(lines).strip()]


# A recording handed over is its speakers' own words, so its mirror takes the command's place
def lift_mirrors(turns, user, assistant):
    lifted = []
    for speaker, text in turns:
        handed = speaker == assistant and lifted and lifted[-1][0] == user and handoff(lifted[-1][1])
        split = mirror_of(text) if handed else None
        if split is None:
            lifted.append((speaker, text))
            continue
        mirror, answer = split
        command = lifted[-1]
        # The same command sent again before any reply leaves copies that nothing answered
        while lifted and lifted[-1] == command:
            lifted.pop()
        lifted += voices(mirror, user)
        if answer:
            lifted.append((speaker, answer))
    return lifted


# The line a re-export finds its session's file by
def id_line(session):
    return f"Session: {session} · "


def render(title, session, harness, turns):
    merged = []
    for speaker, text in turns:
        if merged and merged[-1][0] == speaker:
            merged[-1][1].append(text)
        else:
            merged.append((speaker, [text]))
    # The id leads the file, so a search for it finds the export and the command beside it reopens the session
    lines = [f"{id_line(session)}`{RESUME[harness]} {session}`", ""] if session else []
    lines.append(f"# {title}")
    # A speaker's headings and rules render as the page's own
    for speaker, texts in merged:
        lines += ["", f"**{speaker}:**", "", "\n\n".join(texts)]
    return "\n".join(lines) + "\n"


def first_line(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.readline()
    except (OSError, UnicodeDecodeError):
        return ""


# A session keeps the file its first export wrote in that folder, whatever name a re-export would give it
def target(out, session):
    if not session:
        return out
    folder = os.path.dirname(os.path.abspath(out))
    found = [path for path in glob.glob(os.path.join(glob.escape(folder), "*.md")) if first_line(path).startswith(id_line(session))]
    if len(found) > 1:
        sys.exit(f"export-session: {' and '.join(found)} each export session {session}; delete all but one")
    if found:
        return found[0]
    if os.path.exists(out):
        sys.exit(f"export-session: {out} already exists and does not export session {session}; choose another --out")
    return out


def main():
    parser = argparse.ArgumentParser(description="Write an agent session out as a labeled transcript of its dialogue")
    parser.add_argument("session", help="the session's id, or its transcript's path")
    parser.add_argument("--title", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--user", default="User")
    parser.add_argument("--assistant")
    parser.add_argument("--party", action="append", default=[])
    args = parser.parse_args()
    path, harness, session = find_transcript(args.session)
    assistant = args.assistant or harness
    names = [args.user, assistant, *args.party]
    if len(set(names)) < len(names):
        parser.error(f"--user, each --party and {assistant} need distinct names, since blocks under one name merge")

    reader = read_codex_session if harness == "Codex" else read_session
    turns = lift_mirrors(reader(path, args.user, assistant, set(args.party)), args.user, assistant)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    out = target(args.out, session)
    if os.path.realpath(out) == os.path.realpath(path):
        sys.exit("export-session: the output path is the source transcript; choose another --out")
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(args.title, session, harness, turns))
    print(out)


if __name__ == "__main__":
    main()
