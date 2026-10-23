---
name: transcribe
description: Turn a recording, or the machine transcript of one, into a polished mirror of what was said — written to the file a caller names, or into the reply, where a recording of the user alone stands as their message — invoke whenever the user hands over a recording, typed command or not
---

1. **Prime the vocabulary.** Read any home the caller or the user names with
   the recording before the recording itself, so its names and terms are in
   mind as you hear or correct what was said. A file name is no such naming: a
   recorder often names a recording after where it was made.

2. **Get the words.** Where you can hear audio, read the recording directly.
   Otherwise run `transcribe.sh` beside this file over it, in the background
   where a long recording would outlast the host's time limit for a command,
   and read the transcript it names; where it reports whisper.cpp, its model or
   ffmpeg missing, pass on what it says to install. A machine transcript handed
   over in place of a recording is read as it is.

3. **Mirror what was said.**
   - Fix transcription errors against the names and terms the knowledge base
     uses
   - Where more than one person takes part, open each turn with its speaker in
     bold, by the name a caller gives or the knowledge base uses, attributed by
     voice where you hear it and otherwise by what is said, and mark a turn
     nothing attributes `Unclear`. A voice in the background takes no part
   - Make small fixes to grammar and punctuation, and trim stutters, false
     starts and excess filler. Keep each speaker's words, order and colour:
     never summarise or paraphrase

4. **Deliver it.**
   - **To a file**, where a caller or the user names one: Markdown opening with
     a title for the conversation and its date where known, and no preamble
   - **Into the reply** otherwise, as a blockquote. A recording of the user
     alone, handed over with no other instruction, is their message: a rule
     beneath the mirror, then the answer to it
