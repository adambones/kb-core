# A command line cut into the simple commands the shell will run, shared by the hooks that judge what a command touches
# Quote-aware because an operator inside a quoted pattern is text, and heredoc-aware because a body is one command's input rather than lines of its own

import os
import re
from collections import namedtuple

# Cut wide, since a shell reaches a directory by more spellings than any pattern lists
WORDS = re.compile(r"[\s'\"=:()<>`]+")
# The paren catches the (cd x half the segmenter leaves of a subshell, whose move is then taken to outlast it
CD = re.compile(r"""^\s*\(?\s*(?:cd|pushd)\s+["']?([^"'\s)]+)["']?\s*\)?\s*$""")
# Commands that only copy their input, so a heredoc they read is data unless a pipe hands it on to something that runs it
DATA_SINKS = ("cat", "tee")

# text is the line without its heredoc bodies, bare the same with every quoted span blanked, bodies those heredocs, piped whether its output feeds the next
Segment = namedtuple("Segment", "text bare bodies piped")


def verb_of(segment):
    words = segment.text.split()
    return os.path.basename(words[0].strip("()\"'")) if words else ""


def shell_text(segment):
    """What the shell and the programs it starts will read as commands and paths: the line itself, plus any heredoc that is not plain data."""
    if segment.bodies and (verb_of(segment) not in DATA_SINKS or segment.piped):
        return "\n".join([segment.text] + segment.bodies)
    return segment.text


def segments(command):
    """Each simple command in order, cut on every unquoted operator — a $(…) or (…) is not nested, so its operators cut the enclosing command too."""
    result = []
    state = {"text": [], "bare": [], "bodies": []}
    pending = []
    quote = None
    i, n = 0, len(command)

    def close(piped):
        text = "".join(state["text"])
        if text.strip():
            # The bodies list is shared rather than copied, because a heredoc declared here is only read after the line ends
            result.append(Segment(text, "".join(state["bare"]), state["bodies"], piped))
        state.update(text=[], bare=[], bodies=[])

    def emit(chars, bare=None):
        state["text"].append(chars)
        state["bare"].append(chars if bare is None else bare)

    while i < n:
        c = command[i]
        if quote:
            if c == "\\" and quote == '"' and i + 1 < n:
                emit(command[i : i + 2], "  ")
                i += 2
                continue
            if c == quote:
                quote = None
            emit(c, " ")
            i += 1
            continue
        # A backslash carries the next character through, a newline included, so a continued line stays one command
        if c == "\\" and i + 1 < n:
            emit(command[i : i + 2])
            i += 2
            continue
        if c in "'\"":
            quote = c
            emit(c, " ")
            i += 1
            continue
        if command.startswith("<<", i) and not command.startswith("<<<", i):
            j = i + 2
            strip_tabs = command.startswith("-", j)
            j += strip_tabs
            while j < n and command[j] in " \t":
                j += 1
            k = j
            while k < n and command[k] not in " \t\n;|&<>()":
                k += 1
            delimiter = re.sub(r"[\"'\\]", "", command[j:k])
            if delimiter:
                pending.append((delimiter, strip_tabs, state["bodies"]))
            emit(command[i:k])
            i = k
            continue
        if c == "\n":
            close(False)
            i += 1
            # Bodies follow the line that declared them
            for delimiter, strip_tabs, bodies in pending:
                lines = []
                while i < n:
                    end = command.find("\n", i)
                    line = command[i:] if end < 0 else command[i:end]
                    i = n if end < 0 else end + 1
                    if (line.lstrip("\t") if strip_tabs else line) == delimiter:
                        break
                    lines.append(line)
                bodies.append("\n".join(lines))
            pending = []
            continue
        if command.startswith(("&&", "||"), i):
            close(False)
            i += 2
            continue
        if c == "|":
            close(True)
            i += 1
            continue
        # An ampersand beside a redirection is part of it, as in 2>&1 and &>/dev/null
        if c == "&" and (command[i - 1 : i] in (">", "<") or command[i + 1 : i + 2] == ">"):
            emit(c)
            i += 1
            continue
        if c in ";&":
            close(False)
            i += 1
            continue
        emit(c)
        i += 1
    close(False)
    return result
