#!/usr/bin/env python3
import argparse
import glob
import json
import os
import re
import sys

SELF_COMMAND = "/export-session"
# The harness fences a paste in tags of its own, which are not the user's words
PASTE_FENCE = re.compile(r"</?pasted_content[^>]*>")


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
        # Antigravity records carry step_index at the top level, where Claude Code's carry none
        return session, "Gemini" if "step_index" in next(records(session), {}) else "Claude"
    # A Claude Code session files under the directory it started in, which the id does not name
    claude_root = os.environ.get("CLAUDE_CONFIG_DIR", os.path.expanduser("~/.claude"))
    # Escaped, so an id holding a wildcard cannot export another session's transcript
    matches = glob.glob(os.path.join(claude_root, "projects", "*", f"{glob.escape(session)}.jsonl"))
    if matches:
        return matches[0], "Claude"
    # Antigravity files under Gemini's home, in a directory per client
    gemini_root = os.path.expanduser("~/.gemini")
    # The full log holds every line the other truncates
    for name in ("transcript_full.jsonl", "transcript.jsonl"):
        matches = glob.glob(os.path.join(gemini_root, "*", "brain", glob.escape(session), ".system_generated", "logs", name))
        if matches:
            return matches[0], "Gemini"
    sys.exit(f"export-session: no transcript for session {session} under {claude_root}/projects or {gemini_root}/*/brain")


def origin_kind(holder):
    return (holder.get("origin") or {}).get("kind")


def filter_command(raw):
    command = re.search(r"<command-name>(.*?)</command-name>", raw, re.S)
    if command is None:
        text = PASTE_FENCE.sub("", raw).strip()
        # Antigravity sends a slash command as bare text, untagged
        return None if text == SELF_COMMAND or text.startswith(SELF_COMMAND + " ") else text
    name = command.group(1).strip()
    if name == SELF_COMMAND:
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


def quote(text):
    return "\n".join(f"> {line}" if line.strip() else ">" for line in text.splitlines())


def render(title, turns):
    merged = []
    for speaker, text in turns:
        if merged and merged[-1][0] == speaker:
            merged[-1][1].append(text)
        else:
            merged.append((speaker, [text]))
    lines = [f"# {title}"]
    # Quoted whole, so a heading or rule a speaker wrote cannot open a section of the page the export is pasted into
    for speaker, texts in merged:
        lines += ["", f"**{speaker}:**", "", quote("\n\n".join(texts))]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Write an agent session out as a labeled transcript of its dialogue")
    parser.add_argument("session", help="the session's id, or its transcript's path")
    parser.add_argument("--title", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--user", default="User")
    parser.add_argument("--assistant")
    parser.add_argument("--party", action="append", default=[])
    args = parser.parse_args()
    path, default_assistant = find_transcript(args.session)
    assistant = args.assistant or default_assistant
    names = [args.user, assistant, *args.party]
    if len(set(names)) < len(names):
        parser.error(f"--user, each --party and {assistant} need distinct names, since blocks under one name merge")

    turns = read_session(path, args.user, assistant, set(args.party))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(render(args.title, turns))
    print(args.out)


if __name__ == "__main__":
    main()
