---
name: slack-log
description: Mirror Slack channels, live or archived, into thread-nested markdown that keeps every word, and read what moved in them — invoke to follow or curate a channel, or before relying on recent Slack
---

**Bindings.** The verbatim source and the followed channels. Where either is undeclared, stop.

`python3 <this skill's directory>/slack_log.py` fetches, stores and draws the log on Python 3.9 or later. With a Slack user token in its environment as `SLACK_USER_TOKEN`, it reads Slack's Web API as that user at no model cost. The token's app needs the user scopes `channels:history`, `groups:history`, `im:history` and `mpim:history`, the four matching `:read` scopes, and `users:read`. A token Slack refuses fails the run rather than falling back.

Without a token, its fetch runs `claude -p` against the claude.ai Slack connector, denied the connector's writes and every shell and file-editing tool, and reads as the Slack user that connector is authorised for. That path needs `claude`, found as the Claude Code session running the sync or on its PATH, logged in to an account where the connector is authorised.

## The log

Each channel lives in `<verbatim source>/slack/<name>/`, `<name>` being its Slack name, else the `--name` its first sync was given, else its ID. Its `store.json` is the record: each message's author, time, text, reactions and file names, keyed by timestamp (`ts`). A message deleted in Slack stays. The markdown is redrawn from the store on every sync and never edited: a `<YYYY-MM>.md` file per month by post date, each thread under its parent, a reply also sent to the channel marked `(+channel)`, and `curated.md` wherever a `keep.txt` exists. It keeps every word and drops join and leave notices.

## Follow

Find the channel's ID with the connector's channel search, archived channels included, and add it to the followed channels. Its first `sync` backfills from its floor, or from the channel's start, which takes minutes on a large channel. `--since` applies to every ID in one call, so channels with different floors are backfilled in separate calls.

## Refresh

`slack_log.py sync --out <verbatim source>/slack [--since <floor>] [--name <name>] <ID>...` re-reads the top level over a sixty-day window and only the threads whose reply count or latest reply moved, so a reply under a parent older than the window is missed. `--name` names the directory for a single conversation that Slack leaves unnamed. A sync whose directory another conversation's log already holds stops before it writes, leaving every log as it was: give an unnamed conversation another `--name`, or rename the other directory, which its store's channel ID still finds. Once a channel's log ends in its archive notice, sync skips it. A failed read exits non-zero and leaves that channel's log as it was. The knowledge base runs it on a schedule, and by hand before relying on a log that `recent` flags as stale.

## Read

`slack_log.py recent --out <verbatim source>/slack --days <n> [<name>...]` prints every thread that moved in the window: the parent in full, earlier replies as a count, new replies in full. Its heading flags a log whose last sync is over two days old.

## Curate

`keep.txt` holds one parent's `ts` per line with an optional `# heading`. The next sync or `slack_log.py render --out <verbatim source>/slack [<name>...]` redraws `curated.md` from it, so a kept thread keeps its new replies.
