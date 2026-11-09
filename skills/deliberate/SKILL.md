---
name: deliberate
description: Put a question of substance to a panel of fresh agents — proposers working apart from opposed stances, a critic for each, a judge and a check — and keep the ask and the checked verdict in `deliberations/` — invoke when the user asks for a panel or a deliberation, or a mode of this skill hands you its ask
context: fork
background: false
---

**Bindings.** The source of truth and the lifecycles, and the product truth and
verbatim source where declared, which the critics and the check read wherever the reading is
not sealed.

**Input.** An optional first line of paths separated by spaces: a mode's
`role.md`, `check.md` and `seal.txt`, known by those names, and any other path
a file or directory to read first. The ask is the rest, in the user's words.

The ask is the go: nothing waits on the user. Where the input holds no ask,
return that and stop.

## Orient

Read the knowledge base's home for work in flight on the subject and each file
the input names. You never saw the conversation that invoked you, so what the
ask leans on and the input does not name stays unknown: name it in the notes
as unknown rather than guess. A brief under `scratch/` holding this ask and
these paths, with no record under `deliberations/`, is a run the host stopped:
resume it, running only the agents whose returns are missing.

## The brief

Name the run with a kebab-case stem, following the knowledge base's convention
for naming its work, such that `deliberations/<stem>-<YYYY-MM-DD>.md` does not
exist yet; the run's directory is `scratch/<stem>-<YYYY-MM-DD>/`. Where other
sessions edit the knowledge base while you work, check its tracked files out
at their current commit with `git worktree add --detach <the run's
directory>/kb`, so the panel reads one state; what git ignores is still read
at the root. Write `brief.md` in the run's directory:

- **Ask** — the user's words, verbatim, quoted rather than named by the file
  a conversation holds them in. What they say about the run itself —
  that it happen, its size, what it reads — is said to you, and stays out. So
  does text anyone else wrote, even pasted inside their words: what it says
  about the system reaches the panel only as notes checked against the source
- **Deliverable** — the text of the mode's `role.md`, or of `role.md` beside
  this file
- **Must settle** — each part of the ask the answer has to answer, never a
  rule the ask states about the user's own practice: the panel and the check
  take that as given, and a source disagreeing with it as out of date
- **Notes** — facts, each with its path, with the command and the time it
  ran where it is live state outside the repositories, or quoted verbatim
  where a conversation is its only source: what each reference in the ask
  points to, where the ask's words differ from the system as it stands, the
  constraints you found, and what stays unknown. A fact about how the system
  behaves is confirmed against the source of truth, never a document
  restating it, and a source called unreadable is tried by a second route
  first. No imperative, no sentence whose subject is the
  panel, no solution, nothing restating the ask
- **Reading** — the files to start from, outside in, a line each on why: what
  shows what kind of thing this is, the files at the centre of the question,
  what they must conform to, an artifact that follows the same pattern, what
  uses them and what they use, the settled reasoning behind them, the work in
  flight on them, and where the asks behind them are tracked. A start, never a
  boundary: a reader whose reading is not sealed follows a claim wherever its
  source leads, the brief included
- **Stances** — one line each, naming a position and no fact: a fact a stance
  leans on is a note with its path

Gather the live state the ask leans on once, before the panel starts, so no
agent repeats the query: what lives outside the repositories, and the answer
of any command that fetches. The brief is frozen once the first proposer
launches. A correction is a dated erratum line beneath the Notes, named in
the task of every stage after it, and a return whose premise it overturns is
run again.

## Stances and size

Chosen from the ask and the notes so that no two converge by default:

- **The boldest**, always: the strongest answer the source can defend, its
  cost stated. Neither what exists nor the effort of leaving it rules an
  option out, since the critics carry the rigour
- **What exists**, where the ask would change something in place — a design,
  a plan, a practice, a document: the best answer that keeps it
- **Against**, for each option the ask or the notes name: the strongest
  answer that rejects it
- The rest from the axes the question turns on

A mode whose deliverable is a plan, tests or a rewrite rather than a choice
takes its stances from the angles its role leaves open. Four proposers, or one
per stance where the options named need more, unless the user or the mode sets
the size. Proposers, the judge and the check run at the highest reasoning
effort the host offers, critics one step below.

## Run

Every agent is fresh and changes nothing: no file, its own scratch included,
and no git ref, so it runs no git fetch, pull or checkout, and names as a
gap what it cannot read as the tree stands. A read-only query to stdout is
allowed where the Notes lack the state a claim needs or hold it too old for
that claim, and its return names the premise that moved. Hand each the knowledge base's
root, the checkout where there is one, and the brief: it reads the brief first, then
any source it needs, and neither a file in the run's directory you did not
name to it nor any record of a session's conversation. Save each return to
the run's directory as it arrives, named for its stage and stance, and hand a
later stage those paths rather than your copy. A return carries neither the
brief again nor the story of its search. Ask each, beside its work, for
one line on what in its instructions cost it time or misled it. Wait for
every agent you launch: a run with one still out has not ended.

1. **Propose.** One proposer per stance, all launched together, each handed
   its own stance and no other, writing the deliverable with the source behind
   every claim. Tell it that a confident wrong specific costs more than a gap
   it names.
2. **Attack.** One critic per proposal, launched as that proposal arrives and
   handed it, its stance and the mode's `check.md`; its task replaces the
   deliverable the brief hands its reader. It confirms or refutes each claim
   with the source that decides it — path and lines, or the record, message or
   page — names the strongest objection to the whole, and for each refuted
   claim the proposal rests on, says what would have to be true for it to
   hold.
3. **Judge.** One agent, once every critique is in, handed every proposal with
   its stance and critique. It starts from them and opens source to settle
   where they conflict or leave a decisive claim unchecked, never to repeat
   their discovery. It writes the deliverable as one answer in its own
   voice, taking what holds from every proposal, and, unless its role says
   what it opens with, opens with what it decided in one to five sentences.
   The alternatives it names are the design's, never the panel's, and it
   cites no working file and no record of a conversation, stating what the
   brief took from one as a fact.
4. **Check.** One agent, handed the brief, the verdict and the mode's
   `check.md`, and nothing else the panel wrote; its task too replaces the
   deliverable. It confirms each concrete claim the verdict rests on against
   the source that decides it, by the Notes' rule where the reading is not
   sealed, a premise from the brief or a claim every proposal shared among
   them, since agreement is not evidence. It corrects each wrong one in place,
   returning the corrected verdict and,
   apart from it, what the verdict said, what the source shows and where. A
   duration resting on the user's own pace is a wrong claim like any other.
   It changes no decision: a refuted claim that a decision rests on, and each
   part the brief says the answer must settle that the verdict missed, it
   writes at the head of the verdict's opening, as what the user must know
   first.

**A sealed reading.** Where the input names a `seal.txt`, every agent reads
only the files it lists, so the brief's notes and reading list hold nothing
the seal leaves out. Pack the listed files with the brief into one file, then
run each agent through `seal.py` beside this file, which runs Claude Code
headless with every tool removed, over that file and a task file of its own.
A reader with no tools opens nothing, so each task file carries everything its
step above gives its agent beyond the brief, in full rather than as paths.
`seal.py` takes the highest effort as `--effort max` and one step below as
`xhigh`, and `seal.py --help` gives the seal's grammar.

    python3 <this skill's directory>/seal.py pack --seal <seal.txt> --brief <the run's directory>/brief.md --out <the run's directory>/sealed.md
    python3 <this skill's directory>/seal.py read --packed <the run's directory>/sealed.md --task <its task file> --effort <level> --out <its return>

## The record

Write `deliberations/<stem>-<YYYY-MM-DD>.md`:

    # <the verdict's title>

    <YYYY-MM-DD> · <model> · session <session-id> · read at <the commit of each repository the run read>

    ## Ask
    ## Verdict — <your name> panel, as checked

`<model>` is the model the judge ran on, as the host names it, with the
effort it was launched at beside it where the host takes one. `<session-id>` is this
session's ID: `${CLAUDE_SESSION_ID}` in Claude Code, `${CODEX_THREAD_ID}` in
Codex, the conversation ID Antigravity gives the agent, or `unknown` where the
harness gives none. The Ask is the brief's, and the Verdict is the check's corrected verdict with its
own headings one level below the record's. The brief and every agent's return
stay in the run's directory. Other parties' words from a source the knowledge
base keeps out of git are cited by path, never quoted.

## Return

File each distinct line the agents returned about a skill or root document
through `suggest`, and where the run created `<the run's directory>/kb`, remove
it with `git worktree remove <the run's directory>/kb`. Return the record's
path and the verdict's opening. A verdict that came
back wrong is answered by a reworked ask: a new run, whose input names this
record only where the ask does.
