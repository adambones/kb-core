#!/usr/bin/env python3
"""Seal a panel's reading: pack the files a seal list names with the brief into one file, and run a reader over it with no tools.

A seal list holds one path or glob a line, relative to the knowledge base's root. A `#` line is a comment, a line
starting `-` excludes a pattern, and one starting `!` includes a pattern past the default exclusions, which are hidden
files and the directories node_modules, dist, build and __pycache__. A path named outright, with no glob, overrides
every exclusion. A file over SEAL_MAX_FILE_BYTES (default 300000) is left out.

`pack` prints a WARNING for each pattern that reached files it left out, with why, and for a pack past 300,000
characters of file contents. `read` runs Claude Code headless with every tool, MCP server and skill removed, from an
empty directory, so the reader sees its task, the packed file and the user's own instruction file, and opens nothing.
Every path argument is relative to the knowledge base's root.
"""

import argparse
import fnmatch
import glob
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

MAX_FILE_BYTES = int(os.environ.get("SEAL_MAX_FILE_BYTES", "300000"))
# Every agent reads the whole pack, and attention thins well before a context window fills
BUDGET_CHARS = 300_000
# Dependency and build output, which a broad glob would sweep in ahead of anyone's content
DEFAULT_EXCLUDES = ["node_modules", "dist", "build", "__pycache__"]
# A reader can wait on a usage limit, but not past an hour
READ_SECONDS = 3600

# The knowledge base is the parent of its core/ checkout, which holds this skill; resolved, since the skills/ link would otherwise put it one level too high
KB = Path(__file__).resolve().parents[3]


def read_lines(path: Path) -> List[str]:
    lines = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            lines.append(line)
    return lines


def shown(path: Path, root: Path) -> str:
    # Relative wherever it can be, so the packed file names files as the knowledge base does and carries no home directory
    return os.path.relpath(path, root) if path.is_relative_to(root) else str(path)


def walk(directory: Path) -> List[Path]:
    """Every file under a directory, skipping hidden ones as a glob's ** does."""
    found, visited = [], set()
    # Followed, since a knowledge base links shared skills into its own tree, and each real directory walked once so a link loop ends
    for base, dirs, files in os.walk(directory, followlinks=True):
        real = os.path.realpath(base)
        if real in visited:
            dirs[:] = []
            continue
        visited.add(real)
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        found += [Path(base) / name for name in sorted(files) if not name.startswith(".")]
    return found


def glob_files(root: Path, patterns: List[str]) -> Tuple[List[Tuple[Path, str]], List[str]]:
    """Every file each pattern reaches, with the pattern that reached it, and the patterns that matched nothing."""
    out, seen, unresolved = [], set(), []
    for pattern in patterns:
        hits = glob.glob(pattern if os.path.isabs(pattern) else str(root / pattern), recursive=True)
        if not hits:
            unresolved.append(pattern)
        for hit in sorted(hits):
            # Absolute but unresolved, so a file reached through a link keeps the path the knowledge base cites it by
            path = Path(os.path.abspath(hit))
            for candidate in walk(path) if path.is_dir() else [path]:
                real = os.path.realpath(candidate)
                if real not in seen and candidate.is_file():
                    out.append((candidate, pattern))
                    seen.add(real)
    return out, unresolved


def matches_any(path: Path, root: Path, patterns: List[str]) -> bool:
    """Whether the path, or a directory above it inside the root, matches a pattern written relative to the root or absolute."""
    if not path.is_relative_to(root):
        return any(fnmatch.fnmatch(str(path), pattern) for pattern in patterns)
    parts = path.relative_to(root).parts
    prefixes = ["/".join(parts[: i + 1]) for i in range(len(parts))]
    candidates = prefixes + [str(root / prefix) for prefix in prefixes]
    return any(fnmatch.fnmatch(candidate, pattern.rstrip("/")) for candidate in candidates for pattern in patterns)


def cached(path: Path, root: Path) -> bool:
    if not path.is_relative_to(root):
        return False
    return any(part in DEFAULT_EXCLUDES for part in path.relative_to(root).parts[:-1])


def is_text_file(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return b"\x00" not in handle.read(8000)
    except OSError:
        return False


def read_file(path: Path) -> Optional[str]:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return None
        # latin-1 decodes any byte sequence, so it is the fallback that cannot fail
        for encoding in ("utf-8", "latin-1"):
            try:
                return path.read_text(encoding=encoding)
            except UnicodeError:
                continue
    except OSError:
        pass
    return None


def select(root: Path, seal: Path, skip: List[Path]) -> Dict[Path, str]:
    """The files the seal admits, read once, warning on everything the list reached and left out."""
    # A - line excludes; a ! line includes past the default exclusions, and past a - line only where it names a path outright
    includes, excludes, unexcludes = [], [], []
    for line in read_lines(seal):
        if line.startswith("-"):
            excludes.append(line[1:])
        elif line.startswith("!"):
            includes.append(line[1:])
            unexcludes.append(line[1:])
        else:
            includes.append(line)

    found, unresolved = glob_files(root, includes)
    # A missing path globs to nothing without error, and the omission surfaces as a reader reasoning about a file it was never shown
    for pattern in unresolved:
        print(f"WARNING: no match for seal pattern: {pattern}")

    exact = {pattern for pattern in includes if not any(c in pattern for c in "*?[")}
    chosen, dropped = {}, Counter()
    for path, pattern in found:
        # A file the list names outright overrides every exclusion but the run's own files
        named = pattern in exact and path == Path(os.path.abspath(root / pattern))
        if path in skip:
            dropped[(pattern, "the brief or the packed file itself")] += 1
        elif matches_any(path, root, excludes) and not named:
            dropped[(pattern, "excluded by the list")] += 1
        elif cached(path, root) and not named and not matches_any(path, root, unexcludes):
            dropped[(pattern, "under a tool cache")] += 1
        elif not is_text_file(path):
            dropped[(pattern, "binary")] += 1
        else:
            text = read_file(path)
            if text is None:
                dropped[(pattern, f"unreadable or over {MAX_FILE_BYTES} bytes")] += 1
            else:
                chosen[path] = text
    for (pattern, why), count in sorted(dropped.items()):
        print(f"WARNING: {pattern}: {count} file(s) left out, {why}")
    return dict(sorted(chosen.items(), key=lambda item: str(item[0])))


def build_tree(paths: List[Path], root: Path) -> dict:
    tree: dict = {}
    for path in paths:
        parts = Path(shown(path, root)).parts
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node.setdefault("__files__", []).append(parts[-1])
    return tree


def print_tree(tree: dict, prefix: str = "") -> List[str]:
    lines = []
    dirs = sorted(k for k in tree if k != "__files__")
    entries = [(d, True) for d in dirs] + [(f, False) for f in sorted(tree.get("__files__", []))]
    for index, (name, is_dir) in enumerate(entries):
        last = index == len(entries) - 1
        lines.append(prefix + ("└── " if last else "├── ") + name)
        if is_dir:
            lines.extend(print_tree(tree[name], prefix + ("    " if last else "│   ")))
    return lines


def fence(text: str) -> str:
    # Longer than any backtick run inside, so a packed markdown file cannot close the block around it
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def render(files: Dict[Path, str], root: Path, brief: str) -> str:
    lines = ["<file_map>", root.name, *print_tree(build_tree(list(files), root)), "</file_map>", "", "<file_contents>"]
    for path, text in files.items():
        marks = fence(text)
        lines += [f"File: {shown(path, root)}", f"{marks}{path.suffix.lstrip('.') or 'txt'}", text, marks, ""]
    lines += ["</file_contents>", "", "<brief>", brief.strip(), "</brief>", ""]
    return "\n".join(lines)


def inside(path: Path, root: Path) -> Path:
    """A path under the root, or the reason the run stops: an out path elsewhere could overwrite anything."""
    if not path.is_relative_to(root):
        sys.exit(f"seal: {path} is outside {root}")
    return path


def pack(args):
    seal, brief = (Path(os.path.abspath(KB / p)) for p in (args.seal, args.brief))
    out = inside(Path(os.path.abspath(KB / args.out)), KB / "scratch")
    for needed in (seal, brief):
        if not needed.is_file():
            sys.exit(f"seal: no file at {needed}")
    files = select(KB, seal, [brief, out])
    out.write_text(render(files, KB, brief.read_text(encoding="utf-8", errors="ignore")), encoding="utf-8")
    content = sum(len(text) for text in files.values())
    if content > BUDGET_CHARS:
        print(f"WARNING: {content:,} characters of content is past the {BUDGET_CHARS:,} every reader can hold well; cut the seal")
    print(f"Wrote: {out} ({len(files)} files, {content:,} characters of content)")


def read(args):
    packed, task = (Path(os.path.abspath(KB / p)) for p in (args.packed, args.task))
    out = inside(Path(os.path.abspath(KB / args.out)), KB / "scratch")
    for needed in (packed, task):
        if not needed.is_file():
            sys.exit(f"seal: no file at {needed}")
    # The running Claude Code names its own executable, which a tool shell's PATH may not reach
    binary = os.environ.get("CLAUDE_CODE_EXECPATH") or "claude"
    # An empty tool list removes only the built-in tools, so two flags remove the MCP servers' tools and the skills as well
    # A sealed reader's transcript would only crowd the session list
    command = [binary, "-p", "--tools", "", "--strict-mcp-config", "--disable-slash-commands", "--effort", args.effort, "--no-session-persistence",
               "Your instructions come first in the input, then the files you may read and the brief, packed into one document."]
    # On stdin rather than as an argument: a judge's task carries every proposal and critique, past the size one argument may have
    reading = task.read_text(encoding="utf-8") + "\n\n" + packed.read_text(encoding="utf-8")
    # A fresh empty directory, so no project's instruction file or settings reach the reader, and nobody else's directory can plant one
    with tempfile.TemporaryDirectory() as empty:
        try:
            result = subprocess.run(command, input=reading, capture_output=True, text=True, cwd=empty, timeout=READ_SECONDS)
        except subprocess.TimeoutExpired:
            sys.exit(f"seal: the reader gave no answer in {READ_SECONDS} seconds")
    if result.returncode != 0:
        sys.exit(f"seal: the reader exited {result.returncode}: {result.stderr.strip() or result.stdout.strip()}")
    out.write_text(result.stdout, encoding="utf-8")
    print(f"Wrote: {out} ({len(result.stdout):,} characters)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    pack_parser = commands.add_parser("pack", help="pack the seal list's files and the brief into one file")
    pack_parser.add_argument("--seal", required=True, help="the list of paths and globs the reading admits")
    pack_parser.add_argument("--brief", required=True)
    pack_parser.add_argument("--out", required=True, help="the packed file, under scratch/")
    pack_parser.set_defaults(run=pack)
    read_parser = commands.add_parser("read", help="run one reader with no tools over a packed file")
    read_parser.add_argument("--packed", required=True)
    read_parser.add_argument("--task", required=True, help="a file holding this reader's own instructions and whatever it reads beyond the pack")
    read_parser.add_argument("--effort", required=True, choices=["low", "medium", "high", "xhigh", "max"])
    read_parser.add_argument("--out", required=True, help="where its answer goes, under scratch/")
    read_parser.set_defaults(run=read)
    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
