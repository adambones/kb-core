#!/usr/bin/env python3
# Commits, pushes and new pull requests run only under the recording skills — refused outside them, not prompted
# A user's go-ahead given in words is beyond any hook, so the gate certifies only that the recording rules are loaded
# A push that rewrites or deletes what origin holds asks even inside the recording skills: an unmerged branch's overwritten commits exist nowhere else
# Only git and gh typed as the command are seen; a push from inside another program is the auto-mode classifier's to judge

import json
import os
import re
import shlex
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell_segments import segments  # noqa: E402

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
# Claude Code alone runs this hook, so its discovery directory decides which skills are the knowledge base's
SKILLS_DIR = os.path.join(ROOT, ".claude", "skills")
TYPED = re.compile(r"<command-name>/([A-Za-z0-9_-]+)</command-name>")
NOT_USER_INPUT = "[SYSTEM NOTIFICATION - NOT USER INPUT]"

# Each argument names one more recording skill, for a knowledge base whose recording step commits or opens pull requests itself
RECORDERS = ("checkin",) + tuple(sys.argv[1:])
# A skill that returns to the work it interrupted leaves the window open, as suggest does inside checkin
PASSING = ("suggest",)

# Git's global options that take their value as the next word
GIT_VALUE_OPTIONS = ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env")
REWRITES = ("--force", "--force-with-lease", "--force-if-includes", "--delete", "--mirror", "--prune")


def words_of(text):
    try:
        words = shlex.split(text)
    except ValueError:
        words = text.split()
    # An environment prefix is not the program, so GIT_TRACE=1 git push is still a push
    while words and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]):
        words = words[1:]
    # A subshell's parens stay glued to the words beside them
    if words:
        words[0] = words[0].lstrip("(")
        if "(" not in words[-1]:
            words[-1] = words[-1].rstrip(")")
    return [w for w in words if w]


def git_subcommand(words):
    """The subcommand and its arguments behind git's global options, or None."""
    i = 1
    while i < len(words) and words[i].startswith("-"):
        i += 2 if words[i] in GIT_VALUE_OPTIONS else 1
    return (words[i], words[i + 1 :]) if i < len(words) else None


def action_of(text):
    """One simple command's gated act, or None."""
    words = words_of(text)
    if not words:
        return None
    program = os.path.basename(words[0])
    if program == "gh":
        return "pr-create" if words[1:3] == ["pr", "create"] else None
    if program != "git":
        return None
    found = git_subcommand(words)
    if not found:
        return None
    sub, args = found
    if sub == "commit":
        return "commit"
    if sub != "push":
        return None
    for arg in args:
        # Short flags cluster, so -uf forces and -ud deletes
        if arg.startswith(REWRITES) or (arg.startswith("-") and not arg.startswith("--") and set(arg[1:]) & {"f", "d"}):
            return "force-push"
        # A + refspec forces one ref and a : refspec deletes one, each without any flag saying so
        if arg.startswith(("+", ":")):
            return "force-push"
    return "push"


def actions(command):
    return [a for a in (action_of(segment.text) for segment in segments(command)) if a]


def invoked(record):
    """The skill a record invokes, typed by the user or called by the agent, or None."""
    # The invocation marks the switch, not the loaded body: a second invocation is answered "already loaded" and carries none
    content = (record.get("message") or {}).get("content")
    parts = content if isinstance(content, list) else [{"type": "text", "text": content or ""}]
    for part in parts:
        if not isinstance(part, dict):
            continue
        if record.get("type") == "assistant" and part.get("type") == "tool_use" and part.get("name") == "Skill":
            return str((part.get("input") or {}).get("skill", "")).lstrip("/")
        # A notification quoting a command is not the user typing one
        if record.get("type") == "user" and part.get("type") == "text" and NOT_USER_INPUT not in part.get("text", ""):
            match = TYPED.search(part.get("text", ""))
            if match:
                return match.group(1)
    return None


def current_skill(lines):
    """The knowledge base's skill most recently invoked in the session."""
    # A plugin skill sharing a name, or one the knowledge base does not keep, carries someone else's rules
    # The latest invocation holds until another replaces it, so a recording step that called checkin may still commit after it returns
    current = None
    for line in lines:
        if '"Skill"' not in line and "<command-name>" not in line:
            continue
        try:
            name = invoked(json.loads(line))
        except ValueError:
            continue
        if name and name not in PASSING and os.path.isdir(os.path.join(SKILLS_DIR, name)):
            current = name
    return current


def ask(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        # An event the hook cannot read names no command, so it passes rather than blocking every shell call
        sys.exit(0)
    if event.get("tool_name") != "Bash":
        sys.exit(0)

    found = actions((event.get("tool_input") or {}).get("command", ""))
    if not found:
        sys.exit(0)

    try:
        with open(event.get("transcript_path", ""), encoding="utf-8") as handle:
            skill = current_skill(handle)
    except Exception:
        # An unreadable transcript hides the running skill, so the user decides rather than the gate passing or refusing
        ask("The session's transcript could not be read, so whether a recording skill is running is unknown.")

    if skill not in RECORDERS:
        # Exit 2 hands stderr to the model, so the refusal names the route rather than inviting a workaround
        sys.stderr.write(
            "Blocked: commits, pushes and new pull requests happen only under %s. Invoke the knowledge base's "
            "recording step once the session's writes are in place; where AGENTS.md has a push wait on the "
            "user's word, hold the change and say it is ready instead.\n" % " or ".join("/" + name for name in RECORDERS)
        )
        sys.exit(2)

    if "force-push" in found:
        ask("This push rewrites or deletes what origin holds, which no later commit can undo.")

    sys.exit(0)


if __name__ == "__main__":
    main()
