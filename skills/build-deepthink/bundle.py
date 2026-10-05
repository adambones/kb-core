#!/usr/bin/env python3
"""Build a deep-think bundle: <file_map>, <file_contents> and <user_instructions> from a stem's include list.

Every file the list reaches but the bundle leaves out is named in a WARNING line, with why.
"""

import argparse
import fnmatch
import glob
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

MAX_FILE_BYTES = int(os.environ.get("BUNDLE_MAX_FILE_BYTES", "300000"))
# Tool and dependency caches, never anyone's content; a hidden directory is skipped as well
DEFAULT_EXCLUDES = ["node_modules", "dist", "build", "__pycache__"]
STEM = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

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
    # Relative wherever it can be, so the bundle names files as the knowledge base does and carries no home directory
    return os.path.relpath(path, root) if path.is_relative_to(root) else str(path)


def walk(directory: Path) -> List[Path]:
    """Every file under a directory, skipping hidden ones as a glob's ** does."""
    found = []
    for base, dirs, files in os.walk(directory):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        found += [Path(base) / name for name in sorted(files) if not name.startswith(".")]
    return found


def glob_files(root: Path, patterns: List[str]) -> Tuple[List[Tuple[Path, str]], List[str]]:
    """Every file each include pattern reaches, with the pattern that reached it, and the patterns that matched nothing."""
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


def select(root: Path, outbound: Path, stem: str) -> Dict[Path, str]:
    """The files the bundle carries, read once, warning on everything the list reached and left out."""
    # A - line excludes; a ! line includes past the tool-cache rule but never past a - line
    includes, excludes, unexcludes = [], [], []
    for line in read_lines(outbound / f".{stem}-include.txt"):
        if line.startswith("-"):
            excludes.append(line[1:])
        elif line.startswith("!"):
            includes.append(line[1:])
            unexcludes.append(line[1:])
        else:
            includes.append(line)

    found, unresolved = glob_files(root, includes)
    # A missing path globs to nothing without error, and the omission surfaces as the agent reasoning about code it was never shown
    for pattern in unresolved:
        print(f"WARNING: no match for include pattern: {pattern}")

    exact = {pattern for pattern in includes if not any(c in pattern for c in "*?[")}
    chosen, dropped = {}, Counter()
    for path, pattern in found:
        # A file the list names outright overrides every exclusion but the slot's own
        named = pattern in exact and path == Path(os.path.abspath(root / pattern))
        # The slot holds the inputs and earlier bundles, which a broad glob would otherwise sweep in
        if path.is_relative_to(outbound):
            dropped[(pattern, "in the outbound slot")] += 1
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
        # The star marks a file whose contents follow, the file map's own convention
        lines.append(prefix + ("└── " if last else "├── ") + name + ("" if is_dir else " *"))
        if is_dir:
            lines.extend(print_tree(tree[name], prefix + ("    " if last else "│   ")))
    return lines


def fence(text: str) -> str:
    # Longer than any backtick run inside, so a bundled markdown file cannot close the block around it
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def render(files: Dict[Path, str], root: Path, instructions: str) -> str:
    lines = ["<file_map>", root.name, *print_tree(build_tree(list(files), root)), "", "</file_map>", "", "<file_contents>"]
    for path, text in files.items():
        marks = fence(text)
        lines += [f"File: {shown(path, root)}", f"{marks}{path.suffix.lstrip('.') or 'txt'}", text, marks, ""]
    lines += ["</file_contents>", "", "<user_instructions>", instructions.strip(), "</user_instructions>", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stem", required=True, help="the round's stem, naming its include list, directive and bundle")
    parser.add_argument("--out", required=True, help="the outbound slot holding the inputs and receiving the bundle")
    args = parser.parse_args()

    if not STEM.match(args.stem):
        sys.exit(f"bundle: {args.stem!r} is not a stem; use letters, digits, dots, dashes and underscores")
    # Relative to the knowledge base rather than the working directory, as every include pattern is
    outbound = (KB / os.path.expanduser(args.out)).resolve()
    if outbound == KB:
        sys.exit("bundle: the outbound slot cannot be the knowledge base's root, which would leave every file out")
    # The inputs are dot-prefixed so a file browser on the slot shows only the bundle to upload
    include = outbound / f".{args.stem}-include.txt"
    if not include.is_file():
        sys.exit(f"bundle: no include list at {include}")
    instructions_path = outbound / f".{args.stem}-instructions.md"
    if not instructions_path.is_file():
        print(f"WARNING: no directive at {instructions_path}, so <user_instructions> is empty")
    instructions = instructions_path.read_text(encoding="utf-8", errors="ignore") if instructions_path.is_file() else ""

    files = select(KB, outbound, args.stem)
    bundle = outbound / f"{args.stem}-prompt.md"
    bundle.write_text(render(files, KB, instructions), encoding="utf-8")
    content = sum(len(text) for text in files.values())
    print(f"Wrote: {bundle} ({len(files)} files, {content:,} characters of content)")


if __name__ == "__main__":
    main()
