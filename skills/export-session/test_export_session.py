import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import export_session as exporter


SESSION = "00000000-0000-0000-0000-000000000001"


def event(kind, **fields):
    return {"type": "event_msg", "payload": {"type": kind, **fields}}


def message(role, text):
    return event("item_completed", item={
        "type": "UserMessage" if role == "user" else "AgentMessage",
        "content": [{"type": "text" if role == "user" else "Text", "text": text}],
    })


class ExportSessionTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)

    def transcript(self, rows, path=None):
        path = path or self.root / "session.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
        return str(path)

    def test_modern_dialogue_excludes_internal_records_and_unfinished_reply(self):
        path = self.transcript([
            {"type": "session_meta", "payload": {"id": SESSION}},
            {"type": "response_item", "payload": {"role": "user", "content": "injected instructions"}},
            message("user", "Question"),
            {"type": "response_item", "payload": {"role": "user", "content": "Question"}},
            message("assistant", "Checking"),
            event("item_completed", item={"type": "Reasoning", "raw_content": "private reasoning"}),
            event("item_completed", item={"type": "CommandExecution", "aggregated_output": "tool output"}),
            {"type": "response_item", "payload": {"role": "assistant", "content": "duplicate answer"}},
            message("assistant", "Answer"),
            event("task_complete", last_agent_message="Answer"),
            message("user", "Next question"),
            message("assistant", "Still working"),
        ])
        with open(path, "a") as stream:
            stream.write('{"unfinished":')
        self.assertEqual(exporter.read_codex_session(path, "User", "Codex", set()), [
            ("User", "Question"), ("Codex", "Checking\n\nAnswer"), ("User", "Next question"),
        ])

    def test_legacy_events_preserve_party_and_image(self):
        path = self.transcript([
            event("user_message", message="Guest\nA reply", images=["image"]),
            event("agent_reasoning", text="private"),
            event("agent_message", message="$export-session is available"),
            event("task_complete"),
        ])
        self.assertEqual(exporter.read_codex_session(path, "User", "Codex", {"Guest"}), [
            ("Guest", "A reply\n\n[image]"), ("Codex", "$export-session is available"),
        ])

    def test_export_commands_and_their_replies_are_omitted(self):
        for command in ("$export-session", "/export-session --title Export", "$export-session\nplease"):
            with self.subTest(command=command):
                path = self.transcript([
                    message("user", "Keep this"), message("assistant", "Answer"), event("task_complete"),
                    message("user", command), message("assistant", "Saved"), event("task_complete"),
                    message("user", "Continue"), message("assistant", "Continued"), event("task_complete"),
                ])
                self.assertEqual(exporter.read_codex_session(path, "User", "Codex", set()), [
                    ("User", "Keep this"), ("Codex", "Answer"), ("User", "Continue"), ("Codex", "Continued"),
                ])

    def test_modern_image_and_aborted_turn(self):
        path = self.transcript([
            event("item_completed", item={"type": "UserMessage", "content": [{"type": "localImage", "path": "photo.png"}]}),
            message("assistant", "Partial reply"), event("turn_aborted"),
        ])
        self.assertEqual(exporter.read_codex_session(path, "User", "Codex", set()), [
            ("User", "[image]"), ("Codex", "Partial reply"),
        ])

    def test_custom_home_lookup_path_detection_and_archive(self):
        for number, folder in enumerate(("sessions/2026/10/27", "archived_sessions")):
            with self.subTest(folder=folder):
                home = self.root / str(number)
                path = self.transcript([{"type": "session_meta", "payload": {"id": SESSION}}],
                                       home / folder / f"rollout-date-{SESSION}.jsonl")
                with patch.dict(os.environ, {"CODEX_HOME": str(home), "CLAUDE_CONFIG_DIR": str(home / "claude")}):
                    self.assertEqual(exporter.find_transcript(SESSION), (path, "Codex", SESSION))
                self.assertEqual(exporter.find_transcript(path), (path, "Codex", SESSION))

    def test_cli_reexport_keeps_original_path_and_resume_header(self):
        path = self.transcript([
            {"type": "session_meta", "payload": {"id": SESSION}},
            message("user", "Hello"), message("assistant", "World"), event("task_complete"),
        ])
        first, second = self.root / "first.md", self.root / "second.md"
        for out in (first, second):
            result = subprocess.run([
                sys.executable, str(Path(exporter.__file__)), path,
                "--title", "Export", "--out", str(out), "--user", "Reader",
            ], check=True, capture_output=True, text=True)
            self.assertEqual(result.stdout.strip(), str(first))
        self.assertFalse(second.exists())
        self.assertEqual(first.read_text(),
                         f"Session: {SESSION} · `codex resume {SESSION}`\n\n# Export\n\n**Reader:**\n\nHello\n\n**Codex:**\n\nWorld\n")

    def test_existing_harnesses_still_export(self):
        fixtures = [
            [{"type": "user", "origin": {"kind": "human"}, "message": {"content": "Question"}},
             {"type": "assistant", "message": {"content": [{"type": "text", "text": "Answer"}]}}],
            [{"step_index": 1, "type": "USER_INPUT", "source": "USER_EXPLICIT", "content": "Question"},
             {"step_index": 2, "type": "PLANNER_RESPONSE", "source": "MODEL", "content": "Answer"}],
        ]
        for rows in fixtures:
            with self.subTest(rows=rows):
                path = self.transcript(rows)
                self.assertEqual(exporter.read_session(path, "User", "Assistant", set()), [
                    ("User", "Question"), ("Assistant", "Answer"),
                ])

    def test_filename_collision_preserves_other_session(self):
        out = self.root / "existing.md"
        original = "Session: another-session · resume\n\nKeep me\n"
        out.write_text(original)
        with self.assertRaisesRegex(SystemExit, "already exists"):
            exporter.target(str(out), SESSION)
        self.assertEqual(out.read_text(), original)

    def test_source_transcript_cannot_be_overwritten_without_session_id(self):
        path = self.transcript([
            {"type": "user", "origin": {"kind": "human"}, "message": {"content": "Question"}},
        ])
        original = Path(path).read_text()
        result = subprocess.run([
            sys.executable, str(Path(exporter.__file__)), path,
            "--title", "Export", "--out", path,
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source transcript", result.stderr)
        self.assertEqual(Path(path).read_text(), original)


if __name__ == "__main__":
    unittest.main()
