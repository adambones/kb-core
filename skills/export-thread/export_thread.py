#!/usr/bin/env python3
import argparse
import datetime
import glob
import json
import os
import re
import sys

ASSISTANT = "Claude"
SELF_COMMAND = "/export-thread"


def transcript_path(session_id):
    # A session files under the directory it started in, which the id does not name
    root = os.environ.get("CLAUDE_CONFIG_DIR", os.path.expanduser("~/.claude"))
    matches = glob.glob(os.path.join(root, "projects", "*", f"{session_id}.jsonl"))
    if not matches:
        sys.exit(f"export-thread: no transcript for session {session_id} under {root}/projects")
    return matches[0]


def records(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                # A live session can be mid-write on its last line
                continue


def origin_kind(holder):
    return (holder.get("origin") or {}).get("kind")


def human_text(content):
    if isinstance(content, str):
        command = re.search(r"<command-name>(.*?)</command-name>", content, re.S)
        if command is None:
            return content.strip()
        name = command.group(1).strip()
        if name == SELF_COMMAND:
            return None
        args = re.search(r"<command-args>(.*?)</command-args>", content, re.S)
        return f"{name} {args.group(1).strip() if args else ''}".strip()
    parts = []
    for block in content or []:
        if block.get("type") == "text":
            parts.append(block["text"].strip())
        elif block.get("type") == "image":
            parts.append("[image]")
    return "\n\n".join(part for part in parts if part)


def speaker_of(text, user, parties):
    # A pasted reply arrives under a line holding only its author's name
    first, _, rest = text.partition("\n")
    if first.strip() in parties and rest.strip():
        return first.strip(), rest.strip()
    return user, text


def read_session(path, user, parties):
    turns, reply, title, humans, exporting = [], [], None, 0, False

    def end_turn():
        nonlocal exporting
        # An export's own turn replies with nothing but the file it wrote
        if reply and not exporting:
            turns.append((ASSISTANT, "\n\n".join(reply)))
        reply.clear()
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
        if kind == "custom-title":
            title = record.get("customTitle") or title
        elif kind == "assistant":
            message = record.get("message") or {}
            # The harness's stand-ins for a reply the model never gave
            if record.get("isApiErrorMessage") or message.get("model") == "<synthetic>":
                continue
            for block in message.get("content") or []:
                if block.get("type") == "tool_use":
                    # Text before a tool call narrates the work, so the reply is only what the turn ends with
                    reply.clear()
                elif block.get("type") == "text" and block["text"].strip():
                    reply.append(block["text"].strip())
        elif kind == "user":
            content = (record.get("message") or {}).get("content")
            if isinstance(content, list) and all(block.get("type") == "tool_result" for block in content):
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
            # A message typed while Claude works is absorbed into the running turn instead of stored as a user record
            if attachment.get("type") == "queued_command" and origin_kind(attachment) == "human":
                said(human_text(attachment.get("prompt")))
    end_turn()
    if humans == 0:
        sys.exit(f"export-thread: no message in {path} carries a human origin; the transcript format may have changed")
    return turns, title


def quote(text):
    return "\n".join(f"> {line}" if line.strip() else ">" for line in text.splitlines())


def render(session_id, turns, user):
    merged = []
    for speaker, text in turns:
        if merged and merged[-1][0] == speaker:
            merged[-1][1].append(text)
        else:
            merged.append((speaker, [text]))
    lines, number, previous = [f"Session: {session_id}"], 0, None
    for speaker, texts in merged:
        # A round opens on the first block after a reply, so a pasted party's words share the number of the user's block above them
        if number == 0 or previous == ASSISTANT:
            number += 1
        body = "\n\n".join(texts)
        lines += ["", f"## Round {number} — {speaker}", "", quote(body) if speaker == user else body]
        previous = speaker
    return "\n".join(lines) + "\n"


def default_out(title, turns):
    stem = re.sub(r"[^a-z0-9]+", "-", (title or turns[0][1]).lower()).strip("-")[:50].rstrip("-")
    return os.path.join(os.getcwd(), f"{stem or 'conversation'}-{datetime.datetime.now():%Y-%m-%d-%H%M}.md")


def main():
    parser = argparse.ArgumentParser(description="Write a Claude Code session out as a thread of its dialogue")
    parser.add_argument("session_id")
    parser.add_argument("--user", default="User")
    parser.add_argument("--party", action="append", default=[])
    parser.add_argument("--out")
    args = parser.parse_args()
    names = [args.user, ASSISTANT, *args.party]
    if len(set(names)) < len(names):
        parser.error(f"--user, each --party and {ASSISTANT} need distinct names, since blocks under one name merge")

    path = transcript_path(args.session_id)
    turns, title = read_session(path, args.user, set(args.party))
    out = args.out or default_out(title, turns)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(args.session_id, turns, args.user))
    print(out)


if __name__ == "__main__":
    main()
