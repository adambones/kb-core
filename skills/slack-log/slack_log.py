#!/usr/bin/env python3
import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# A tool shell's PATH may miss claude, so the running Claude Code's own binary comes first while it still exists
OWN = os.environ.get("CLAUDE_CODE_EXECPATH")
CLAUDE = OWN if OWN and os.path.isfile(OWN) else "claude"
PREFIX = "mcp__claude_ai_Slack__"
READ_CHANNEL = PREFIX + "slack_read_channel"
READ_THREAD = PREFIX + "slack_read_thread"
# User settings can allow more than --allowedTools does and the model reads other people's words, so posting as the user and the shell and file tools are denied by name
DENIED = [PREFIX + t for t in (
    "slack_send_message", "slack_send_message_draft", "slack_schedule_message", "slack_add_reaction",
    "slack_create_canvas", "slack_update_canvas", "slack_create_conversation", "slack_create_list",
    "slack_update_list", "slack_add_list_record", "slack_update_list_record",
    "slack_get_file_upload_url", "slack_complete_file_upload")] + ["Bash", "Edit", "Write", "WebFetch"]
# Claude.ai connectors attach after the session starts, so a run that skips the search concludes the tools do not exist
LOAD = (f'Before anything else, call ToolSearch with query "select:{READ_CHANNEL},{READ_THREAD}" and max_results 2, '
        "repeating it once if they are not returned. ")
# Every result stays in a run's context until the run ends, which is what bounds a run's share of a channel
PAGE_SIZE = 40
PAGES_PER_RUN = 10
THREADS_PER_RUN = 20
# The notice Slack posts as an archived channel's last message; an unarchived channel stays skipped until its store is removed
ARCHIVED = "archived the channel"


# Each read comes back as (tool, input, payload) in the order the run placed it, which the cursor chain relies on
def fetch(prompt, attempt=1):
    # Default mode, so a permissive mode in user settings cannot widen the allowlist; the model only places calls, so the cheapest serves
    cmd = [CLAUDE, "-p", LOAD + prompt, "--output-format", "stream-json", "--verbose",
           "--permission-mode", "default", "--model", "haiku", "--max-turns", "60",
           "--allowedTools", " ".join([READ_CHANNEL, READ_THREAD, "ToolSearch"]),
           "--disallowedTools", " ".join(DENIED)]
    # Outside the knowledge base so its instructions and hooks never load; fixed so every run's transcript lands in one project
    cwd = Path(tempfile.gettempdir()) / "slack-log"
    cwd.mkdir(exist_ok=True)
    # A connector call can hang with no reply, so each read is bounded and a run that still stalls is cut short
    env = {**os.environ, "MCP_TOOL_TIMEOUT": "120000"}
    calls, results, failure = {}, [], None
    with tempfile.TemporaryFile("w+") as stderr:
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=stderr, text=True)
        watchdog = threading.Timer(900, proc.kill)
        watchdog.start()
        # Results are taken as they stream, so a run cut short still hands back every read it finished
        # Payloads come from the transcript's tool results, never from the model's reply, so no message is retyped
        for line in proc.stdout:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                # A run killed mid-write leaves its last line half-written
                continue
            for part in (event.get("message") or {}).get("content") or []:
                if not isinstance(part, dict):
                    continue
                if part.get("type") == "tool_use" and part["name"] in (READ_CHANNEL, READ_THREAD):
                    calls[part["id"]] = (part["name"], part["input"])
                elif part.get("type") == "tool_result" and part.get("tool_use_id") in calls:
                    if part.get("is_error"):
                        failure = f"slack read failed: {text_of(part['content'])[:300]}"
                    else:
                        results.append((*calls[part["tool_use_id"]], payload_of(part["content"])))
        proc.wait()
        watchdog.cancel()
        stderr.seek(0)
        if proc.returncode and not failure:
            failure = "the run stalled" if proc.returncode < 0 else f"claude exited {proc.returncode}: {stderr.read()[-400:]}"
    if results:
        return results
    # A quiet channel still returns an empty page, so no result at all means the run never placed the call
    reason = failure or "the run placed no read"
    if attempt >= 3:
        sys.exit(f"slack-log: {reason}")
    print(f"slack-log: retrying, {reason}", file=sys.stderr)
    return fetch(prompt, attempt + 1)


def text_of(content):
    if isinstance(content, str):
        return content
    return "".join(x.get("text", "") for x in content if isinstance(x, dict))


def payload_of(content):
    body = text_of(content)
    # Claude Code moves a large result to disk and hands the model a preview, so the payload is read back from that file
    saved = re.search(r"^<persisted-output>\n.*?saved to: (\S+)", body, re.S)
    if saved:
        body = text_of(json.loads(Path(saved.group(1)).read_text()))
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        sys.exit(f"slack-log: unparsed tool result: {body[:300]}")


# The connector returns Slack pre-rendered as text rather than its JSON, so these patterns are the contract and an unknown shape exits
CHANNEL_HEADER = re.compile(r"^=== Message from (.+?) at (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) \S+ === ?$", re.M)
THREAD_HEADER = re.compile(
    r"^(?:=== THREAD PARENT MESSAGE ===|=== THREAD REPLIES \(\d+ total\) ===|--- Reply \d+ of \d+ ---)$", re.M)
AUTHOR = re.compile(r"^(.*?)(?: <[^>]*>)?(?: \(([UBW][A-Z0-9]+)\))?$")
REACTION = re.compile(r"([^\s,()]+) \((\d+)\)")
CURSOR = re.compile(r"use cursor:? `([^`]+)`")


def message(author, when, ts, lines):
    meta = {}
    # The connector appends thread, reaction and file lines after the body, so only trailing ones count as metadata
    while lines and (not lines[-1].strip() or re.match(r"^(Thread|Reactions|Files): ", lines[-1])):
        line = lines.pop()
        if line.strip():
            key, value = line.split(": ", 1)
            meta[key] = value
    who = AUTHOR.match(author.strip())
    record = {"ts": ts, "name": who.group(1), "uid": who.group(2), "time": when, "text": "\n".join(lines).strip(),
              "reactions": {k: int(n) for k, n in REACTION.findall(meta.get("Reactions", ""))},
              "files": [f.strip() for f in re.findall(r"([^,(]+?) \(ID: ", meta.get("Files", ""))]}
    thread = re.match(r"(\d+) repl(?:y|ies) \(latest: (.+?) \S+\)", meta.get("Thread", ""))
    if thread:
        record["replies"], record["latest"] = int(thread.group(1)), thread.group(2)
    return record


def parse_channel(text):
    name = re.search(r"^Channel: #(\S+)", text, re.M)
    parts = CHANNEL_HEADER.split(text)[1:]
    records = []
    for author, when, block in zip(parts[0::3], parts[1::3], parts[2::3]):
        lines = block.strip("\n").split("\n")
        ts = lines.pop(0).removeprefix("Message TS: ").strip()
        records.append(message(author, when, ts, lines))
    if not records and "Message from" in text:
        sys.exit("slack-log: a channel read matched no message; the connector's format may have changed")
    return (name.group(1) if name else None), records


# The connector's reply total is returned beside each page's replies, so a short page can be caught
def parse_thread(text):
    total = re.search(r"^=== THREAD REPLIES \((\d+) total\) ===$", text, re.M)
    records = []
    for block in THREAD_HEADER.split(text):
        lines = block.strip("\n").split("\n")
        if len(lines) < 3 or not lines[0].startswith("From: "):
            continue
        when = lines[1].removeprefix("Time: ").rsplit(" ", 1)[0]
        records.append(message(lines[0][6:], when, lines[2].removeprefix("Message TS: ").strip(), lines[3:]))
    if not records:
        sys.exit("slack-log: a thread read matched no message; the connector's format may have changed")
    return records[0], records[1:], int(total.group(1)) if total else 0


# Every channel page since oldest, split across runs so a large channel never fills one context
def read_top(cid, oldest):
    pages, cursor = [], None
    while True:
        start = f", cursor {cursor}" if cursor else ""
        results = [r for r in fetch(
            f"Call {READ_CHANNEL} with channel_id {cid}, limit {PAGE_SIZE}, oldest {oldest}{start}. While its "
            f"pagination_info names a cursor and you have made fewer than {PAGES_PER_RUN} such calls, call it again "
            "with that cursor and the same channel_id, limit and oldest. Make no other calls and do not summarise. "
            "Then reply: done") if r[0] == READ_CHANNEL]
        if not results:
            sys.exit(f"slack-log: no channel read came back for {cid}")
        # The model retypes every argument, so each page is held to the channel and window asked for, and to the cursor the page before it returned
        asked = object()
        for _, args, payload in results:
            # A repeated call's page is dropped rather than read as a broken chain
            if (args.get("cursor") or None) == asked:
                continue
            asked = args.get("cursor") or None
            if args.get("channel_id") != cid or float(args.get("oldest", -1)) != float(oldest):
                sys.exit(f"slack-log: channel read for {cid} asked for another channel or window")
            if asked != cursor:
                sys.exit(f"slack-log: channel read for {cid} broke its cursor chain")
            pages.append(payload)
            found = CURSOR.search(payload.get("pagination_info", ""))
            cursor = found.group(1) if found else None
        if not cursor:
            return pages


def read_threads(cid, due):
    # The connector pages a long thread whatever limit is asked for
    # A thread's place outlives the run, so one longer than a run resumes where it stopped
    chains = {ts: {"next": None, "replies": []} for ts in due}
    threads = {}
    while len(threads) < len(chains):
        batch = [ts for ts in due if ts not in threads][:THREADS_PER_RUN]
        lines = [f"{ts} cursor {chains[ts]['next']}" if chains[ts]["next"] else ts for ts in batch]
        read = 0
        for _, args, payload in fetch(
                f"For each line below, call {READ_THREAD} with channel_id {cid}, the line's message_ts, limit 1000 "
                "and the line's cursor where it names one. While a thread's pagination_info names a cursor and you "
                f"have made fewer than {THREADS_PER_RUN} calls in all, call it again with that cursor and the same "
                "channel_id, message_ts and limit. Make no other calls and do not summarise. Then reply: done\n"
                + "\n".join(lines)):
            ts = args.get("message_ts")
            # The model retypes every argument and can hand one thread's cursor to another, so a page asked from anywhere but where its thread stands is dropped and the thread asked again
            if args.get("channel_id") != cid or ts not in chains or ts in threads or (
                    args.get("cursor") or None) != chains[ts]["next"]:
                continue
            chain = chains[ts]
            _, replies, total = parse_thread(payload["messages"])
            if total and len(replies) != total:
                sys.exit(f"slack-log: thread {ts} returned {len(replies)} of {total} replies on one page")
            found = CURSOR.search(payload.get("pagination_info", ""))
            chain["next"] = found.group(1) if found else None
            chain["replies"] += replies
            read += 1
            if not chain["next"]:
                threads[ts] = chain["replies"]
        # A dropped page is asked again only while each run lands one, so a run that lands none ends the sync
        if not read:
            sys.exit(f"slack-log: no page of a batch of {len(batch)} threads could be read for {cid}")
    return threads


def find_store(out, cid):
    for path in out.glob("*/store.json"):
        if json.loads(path.read_text()).get("channel_id") == cid:
            return path
    return None


def taken(held, cid):
    return held.exists() and json.loads(held.read_text()).get("channel_id") != cid


def save(path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    os.replace(tmp, path)


def sync(cid, out, lookback, since, label):
    path = find_store(out, cid)
    # A first sync under a label already taken would read a whole backfill only to refuse it
    if not path and label and taken(out / label / "store.json", cid):
        sys.exit(f"slack-log: {out / label} holds another conversation's log, so {cid} needs another --name")
    store = json.loads(path.read_text()) if path else {"channel_id": cid, "messages": {}}
    stored = store["messages"]
    if archived(tree(stored)[0]):
        print(f"#{store['name']}: archived, nothing to read")
        return
    # Replies surface only through their parent, so later syncs re-read a window of parents and a thread whose parent predates it stops updating
    # The connector hangs on oldest 0, so a backfill from the start asks from the first second instead
    floor = datetime.strptime(since, "%Y-%m-%d").timestamp() if since else 1
    oldest = f"{time.time() - lookback * 86400:.6f}" if stored else f"{floor:.6f}"
    name, top = None, []
    for page in read_top(cid, oldest):
        page_name, records = parse_channel(page["messages"])
        name, top = name or page_name, top + records

    due = [m["ts"] for m in top if m.get("replies") and (
        stored.get(m["ts"], {}).get("replies"), stored.get(m["ts"], {}).get("latest")) != (m["replies"], m["latest"])]
    threads = read_threads(cid, due) if due else {}
    # The store only adds: a deleted message stays, and an edit lands only while its parent is in the window
    for m in top:
        # On a reply this marks one also sent to the channel
        stored[m["ts"]] = {**stored.get(m["ts"], {}), **m, "in_channel": True}
    for parent, replies in threads.items():
        for r in replies:
            stored[r["ts"]] = {**stored.get(r["ts"], {}), **r, "parent": parent}

    # A DM or group DM has no name in Slack, so it takes the label it was followed under
    store["name"] = name or store.get("name") or label or cid
    store["title"] = f"#{name}" if name else store.get("title") or store["name"]
    store["synced"] = datetime.now().isoformat(timespec="seconds")
    directory = out / store["name"]
    held = directory / "store.json"
    # Before any rename, since a second conversation under one name would overwrite the record that keeps what Slack deleted
    if held != path and taken(held, cid):
        sys.exit(f"slack-log: {directory} holds another conversation's log; rename that directory, which its store's channel ID still finds")
    # A renamed channel takes its directory along, so keep.txt still finds its store
    if path and path.parent != directory:
        path.parent.rename(directory)
    directory.mkdir(parents=True, exist_ok=True)
    save(directory / "store.json", store)
    render(directory)
    print(f"#{store['name']}: {len(top)} top-level read, {len(due)} threads read, {len(stored)} held")


# Slack's wire markup to markdown, leaving every author's word as written
def markup(text):
    text = re.sub(r"<@[A-Z0-9]+\|([^>]+)>", r"@\1", text)
    text = re.sub(r"<!(channel|here|everyone)>", r"@\1", text)
    text = re.sub(r"<#[A-Z0-9]+\|([^>]+)>", r"#\1", text)
    text = re.sub(r"<mailto:[^|>]+\|([^>]+)>", r"\1", text)
    text = re.sub(r"<(https?://[^|>]+)\|([^>]+)>",
                  lambda m: m.group(1) if m.group(1) == m.group(2) else f"[{m.group(2)}]({m.group(1)})", text)
    text = re.sub(r"<(https?://[^>]+)>", r"\1", text)
    text = re.sub(r"::skin-tone-\d:", ":", text)
    # The connector's note on a forward tells its own caller how to fetch the original, which a reader cannot use
    text = re.sub(r"Forwarded message from ([^(\n]+) \((https?://[^)]+)\)[^\n]*", r"[forwarded from \1](\2)", text)
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return [line.rstrip() for line in text.split("\n") if line.strip()]


# A day of None heads a day section, "" always prints the date, and a date prints it only for a reply on another day
def entry(m, depth, day=None):
    stamp = m["time"][11:16] if day in (None, m["time"][:10]) else m["time"][5:16]
    body = markup(m["text"]) or [""]
    echo = " (+channel)" if m.get("parent") and m.get("in_channel") else ""
    counts = defaultdict(int)
    for name, n in m.get("reactions", {}).items():
        counts[name.split("::")[0]] += n
    tail = "".join(f" [file: {f}]" for f in m.get("files", []))
    tail += " · " + " ".join(f"{k}×{n}" for k, n in counts.items()) if counts else ""
    pad = "  " * depth
    out = [f"{pad}- {stamp} {m['name']}{echo}: {body[0]}"] + [f"{pad}  {b}" for b in body[1:]]
    out[-1] += tail
    return out


def tree(stored):
    replies = defaultdict(list)
    for m in stored.values():
        if m.get("parent"):
            replies[m["parent"]].append(m)
    noise = re.compile(r"<@[A-Z0-9]+\|[^>]+> has (joined|left) the channel")
    tops = [m for m in stored.values() if not m.get("parent") and not noise.fullmatch(m["text"])]
    order = lambda m: float(m["ts"])
    return sorted(tops, key=order), {k: sorted(v, key=order) for k, v in replies.items()}


def title(store):
    return store.get("title") or f"#{store['name']}"


def render(directory):
    store = json.loads((directory / "store.json").read_text())
    tops, replies = tree(store["messages"])
    months = defaultdict(list)
    for m in tops:
        months[m["time"][:7]].append(m)
    for month, members in months.items():
        out, day = [f"# {title(store)} · {month}"], None
        for m in members:
            if m["time"][:10] != day:
                day = m["time"][:10]
                out += ["", f"## {datetime.strptime(day, '%Y-%m-%d'):%a %d %b}", ""]
            out += entry(m, 0) + [x for r in replies.get(m["ts"], []) for x in entry(r, 1, day)]
        (directory / f"{month}.md").write_text("\n".join(out) + "\n")
    # Written by whoever curates, one `<parent ts> [# heading]` per line
    keep = directory / "keep.txt"
    if keep.exists():
        out = [f"# {title(store)} · curated"]
        for row in keep.read_text().splitlines():
            ts, _, note = row.partition("#")
            m = store["messages"].get(ts.strip())
            if m:
                out += ["", f"## {note.strip() or m['time'][:10]}", ""]
                out += entry(m, 0, "") + [x for r in replies.get(m["ts"], []) for x in entry(r, 1, m["time"][:10])]
        (directory / "curated.md").write_text("\n".join(out) + "\n")


def archived(tops):
    return bool(tops) and tops[-1]["text"] == ARCHIVED


def recent(directory, days):
    store = json.loads((directory / "store.json").read_text())
    since = time.time() - days * 86400
    tops, replies = tree(store["messages"])
    moved = []
    for m in tops:
        thread = replies.get(m["ts"], [])
        first = min([float(x["ts"]) for x in [m] + thread if float(x["ts"]) >= since], default=None)
        if first:
            fresh = [r for r in thread if float(r["ts"]) >= since]
            moved.append((first, m, fresh, len(thread) - len(fresh)))
    synced = store.get("synced", "")
    # Two days, so a daily schedule may miss one run before a reader is warned
    stale = not archived(tops) and synced < (datetime.now() - timedelta(days=2)).isoformat()
    if not moved and not stale:
        return
    print(f"# {title(store)} · since {datetime.fromtimestamp(since):%Y-%m-%d %H:%M}" + (f" · STALE, last synced {synced[:16]}" if stale else "") + "\n")
    for _, m, fresh, earlier in sorted(moved, key=lambda t: t[0]):
        print("\n".join(entry(m, 0, "")))
        if earlier:
            print(f"  - … {earlier} earlier repl{'y' if earlier == 1 else 'ies'}")
        for r in fresh:
            print("\n".join(entry(r, 1, m["time"][:10])))
    print()


def channels(out, names):
    found = sorted(p.parent for p in out.glob("*/store.json"))
    return [d for d in found if not names or d.name in names]


def main():
    parser = argparse.ArgumentParser(description="Mirror Slack channels into thread-nested markdown that keeps every word")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("sync", "recent", "render"):
        sub = commands.add_parser(command)
        sub.add_argument("--out", type=Path, required=True)
        sub.add_argument("channels", nargs="*", help="channel IDs to sync, or channel directory names to read")
        if command == "sync":
            sub.add_argument("--lookback", type=int, default=60, help="days of parents re-read for moved threads")
            sub.add_argument("--since", help="YYYY-MM-DD floor for a channel's first sync; ignored once its store exists")
            sub.add_argument("--name", help="directory name for one conversation Slack leaves unnamed, such as a DM")
        if command == "recent":
            sub.add_argument("--days", type=int, default=7)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.command == "sync":
        # Two syncs over one store would race its rewrite
        with open(args.out / ".lock", "w") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                sys.exit("slack-log: another sync holds the lock")
            if args.name and len(args.channels) != 1:
                parser.error("--name labels exactly one conversation")
            for cid in args.channels:
                sync(cid, args.out, args.lookback, args.since, args.name)
    elif args.command == "recent":
        for directory in channels(args.out, args.channels):
            recent(directory, args.days)
    else:
        for directory in channels(args.out, args.channels):
            render(directory)


if __name__ == "__main__":
    main()
