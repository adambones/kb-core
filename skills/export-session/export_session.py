#!/usr/bin/env python3
import argparse
import glob
import json
import os
import re
import sys

ASSISTANT = "Claude"
SELF_COMMAND = "/export-session"
# The harness fences a paste in tags of its own, which are not the user's words
PASTE_FENCE = re.compile(r"</?pasted_content[^>]*>")


def transcript_path(session_id):
    # A session files under the directory it started in, which the id does not name
    root = os.environ.get("CLAUDE_CONFIG_DIR", os.path.expanduser("~/.claude"))
    matches = glob.glob(os.path.join(root, "projects", "*", f"{session_id}.jsonl"))
    if not matches:
        sys.exit(f"export-session: no transcript for session {session_id} under {root}/projects")
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
            return PASTE_FENCE.sub("", content).strip()
        name = command.group(1).strip()
        if name == SELF_COMMAND:
            return None
        args = re.search(r"<command-args>(.*?)</command-args>", content, re.S)
        return f"{name} {args.group(1).strip() if args else ''}".strip()
    parts = [PASTE_FENCE.sub("", block["text"]).strip() for block in content or [] if block.get("type") == "text"]
    images = [block for block in content or [] if block.get("type") == "image"]
    # A pasted image leaves a numbered marker in the prompt, so only a message carrying none gets ours
    if images and not any("[Image #" in part for part in parts):
        parts += ["[image]"] * len(images)
    return "\n\n".join(part for part in parts if part)


def speaker_of(text, user, parties):
    # A pasted reply arrives under a line holding only its author's name
    first, _, rest = text.partition("\n")
    if first.strip() in parties and rest.strip():
        return first.strip(), rest.strip()
    return user, text


def read_session(path, user, parties):
    turns, reply, humans, exporting, waiting = [], [], 0, False, False

    def flush():
        # An export's own turn replies with nothing but the file it wrote
        if reply and not exporting:
            turns.append((ASSISTANT, "\n\n".join(reply)))
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
            # A message typed while Claude works is absorbed into the running turn instead of stored as a user record
            if attachment.get("type") == "queued_command" and origin_kind(attachment) == "human":
                # What the turn said before the message arrived answered what came before it
                flush()
                said(human_text(attachment.get("prompt")))
    # A turn still waiting on a tool when the transcript ends is the one running this export
    if not waiting:
        end_turn()
    if humans == 0:
        sys.exit(f"export-session: no message in {path} carries a human origin; the transcript format may have changed")
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
    parser = argparse.ArgumentParser(description="Write a Claude Code session out as a labeled transcript of its dialogue")
    parser.add_argument("session_id")
    parser.add_argument("--title", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--user", default="User")
    parser.add_argument("--party", action="append", default=[])
    args = parser.parse_args()
    names = [args.user, ASSISTANT, *args.party]
    if len(set(names)) < len(names):
        parser.error(f"--user, each --party and {ASSISTANT} need distinct names, since blocks under one name merge")

    turns = read_session(transcript_path(args.session_id), args.user, set(args.party))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(render(args.title, turns))
    print(args.out)


if __name__ == "__main__":
    main()
