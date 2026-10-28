#!/usr/bin/env python3
# Which commands the gate catches, which skill it trusts, and what a run of the hook decides
# The hook runs from a knowledge base the test builds, so the result never depends on which skills the host keeps

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "commit-gate.py")
KB_SKILLS = ("checkin", "record", "build", "reply", "write", "suggest")

KB = tempfile.mkdtemp()
os.makedirs(os.path.join(KB, "core", "hooks"))
for name in ("commit-gate.py", "shell_segments.py"):
    shutil.copy2(os.path.join(HERE, name), os.path.join(KB, "core", "hooks", name))
for name in KB_SKILLS:
    os.makedirs(os.path.join(KB, ".claude", "skills", name))
GATE = os.path.join(KB, "core", "hooks", "commit-gate.py")

spec = importlib.util.spec_from_file_location("commit_gate", GATE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


# Record shapes copied from a live transcript, including the "already loaded" answer a second invocation gets instead of a body
def called(skill):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "toolu_1", "name": "Skill", "input": {"skill": skill}, "caller": {"type": "direct"}}]}}


def typed(skill):
    return {"type": "user", "message": {"content": "<command-message>%s</command-message>\n<command-name>/%s</command-name>" % (skill, skill)}}


def reloaded(skill):
    return {"type": "user", "isMeta": True, "message": {"content": [{"type": "text", "text": "Skill /%s is already loaded above; instructions unchanged." % skill}]}}


def reminder(skill):
    return {"type": "user", "message": {"content": [{"type": "text", "text": gate.NOT_USER_INPUT + " <command-name>/%s</command-name>" % skill}]}}


COMMANDS = [
    ("a commit", "git commit -m 'Add the gate'", ["commit"]),
    ("a commit by path into another tree", "git -C /home/user/kb/core commit README.md -m x", ["commit"]),
    ("a push after a merge pull", "git pull --no-rebase && git push", ["push"]),
    ("a push behind an environment prefix", "GIT_TRACE=1 git push -u origin feature", ["push"]),
    ("a force push", "git push --force-with-lease origin feature", ["force-push"]),
    ("a short force flag inside a cluster", "git push -uf origin feature", ["force-push"]),
    ("a plus refspec forces without a flag", "git push origin +feature", ["force-push"]),
    ("a remote branch deletion", "git push origin --delete feature", ["force-push"]),
    ("a colon refspec deletes without a flag", "git push origin :feature", ["force-push"]),
    ("a pull request", "gh pr create --draft --head feature", ["pr-create"]),
    ("a read of the log is not gated", "git log --oneline -5", []),
    ("commit-tree is not a commit", "git commit-tree HEAD^{tree}", []),
    ("a pull request listing is not gated", "gh pr list --head feature", []),
    ("a quoted mention is text, not a command", "grep -n 'git push' docs/workflow.md", []),
    ("an issue is left to its own permission prompt", "gh issue create --title x", []),
    ("a push inside a subshell is still a push", "(cd code/app && git push)", ["push"]),
]

SKILLS = [
    ("no invocation leaves no recording skill", [], None),
    ("an agent's call marks the skill", [called("record"), called("checkin")], "checkin"),
    ("a typed command marks the skill", [typed("record")], "record"),
    ("a later skill takes over", [called("checkin"), called("reply")], "reply"),
    ("a second invocation answered from memory still switches", [called("checkin"), called("write"), called("checkin"), reloaded("checkin")], "checkin"),
    ("a plugin skill sharing a name is not the knowledge base's", [called("checkin"), called("plugin:write")], "checkin"),
    ("a skill the knowledge base does not keep is not its", [called("checkin"), called("unknown")], "checkin"),
    ("a notification quoting a command is not one", [called("reply"), reminder("record")], "reply"),
    ("a suggestion queued inside checkin leaves it current", [called("checkin"), called("suggest")], "checkin"),
]

failures = 0

for label, command, expected in COMMANDS:
    got = gate.actions(command)
    failures += got != expected
    print(("ok  " if got == expected else "FAIL"), label)

for label, records, expected in SKILLS:
    got = gate.current_skill(json.dumps(record) for record in records)
    failures += got != expected
    print(("ok  " if got == expected else "FAIL"), label)


def run(command, records, recorders=(), transcript=None):
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")
    event = {"tool_name": "Bash", "tool_input": {"command": command}, "transcript_path": transcript or handle.name}
    done = subprocess.run([GATE, *recorders], input=json.dumps(event), capture_output=True, text=True)
    os.remove(handle.name)
    decision = json.loads(done.stdout)["hookSpecificOutput"]["permissionDecision"] if done.stdout.strip() else ""
    return done.returncode, decision, done.stderr


RUNS = [
    ("checkin commits with no prompt", "git commit README.md -m x", [called("checkin")], (), None, (0, "", "")),
    ("a recorder the hook's command names commits too", "gh pr create --draft --head kb", [called("record")], ("record",), None, (0, "", "")),
    ("a skill the hook's command does not name is refused", "gh pr create --draft --head kb", [called("record")], (), None, (2, "", "/checkin")),
    ("a commit outside the recording skills is refused, naming each recorder", "git commit -am x", [called("build")], ("record",), None, (2, "", "/checkin or /record")),
    ("a push in a session that recorded nothing is refused", "git push", [], (), None, (2, "", "/checkin")),
    ("a force push asks even inside checkin", "git push --force origin kb", [called("checkin")], (), None, (0, "ask", "")),
    ("a force push outside is refused before it is asked", "git push -f", [called("reply")], (), None, (2, "", "/checkin")),
    ("an unreadable transcript hands the act back to the user", "git push", [], (), "/nonexistent/transcript.jsonl", (0, "ask", "")),
    ("an ungated command passes untouched", "git status", [], (), None, (0, "", "")),
]

# settings.json runs the hook by path with no interpreter in front, so a lost mode bit ungates every push silently
failures += not os.access(HOOK, os.X_OK)
print(("ok  " if os.access(HOOK, os.X_OK) else "FAIL"), "the hook is executable")

for label, command, records, recorders, transcript, (code, decision, named) in RUNS:
    status, got_decision, message = run(command, records, recorders, transcript)
    got = status == code and got_decision == decision and named in message
    failures += not got
    print(("ok  " if got else "FAIL"), label)

shutil.rmtree(KB)
print(("%d failed" % failures) if failures else "all passed")
sys.exit(1 if failures else 0)
