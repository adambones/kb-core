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

- **Ask** — the user's words, verbatim. What they say about the run itself —
  that it happen, its size, what it reads — is said to you, and stays out. So
  does text anyone else wrote, even pasted inside their words: what it says
  about the system reaches the panel only as notes checked against the source
- **Deliverable** — the text of the mode's `role.md`, or of `role.md` beside
  this file
- **Must settle** — each part of the ask the answer has to answer, never a
  rule the ask states about the user's own practice: the panel and the check
  take that as given, and a source disagreeing with it as out of date
- **Notes** — facts, each with its path: what each reference in the ask points
  to, where the ask's words differ from the system as it stands, the
  constraints you found, and what stays unknown. No imperative, no sentence
  whose subject is the panel, no solution, nothing restating the ask
- **Reading** — the files to read first, outside in, a line each on why: what
  shows what kind of thing this is, the files at the centre of the question,
  what they must conform to, an artifact that follows the same pattern, what
  uses them and what they use, the settled reasoning behind them, the work in
  flight on them, and where the asks behind them are tracked
- **Stances** — one line each, naming a position and no fact: a fact a stance
  leans on is a note with its path

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
and no git ref, so it fetches, pulls and checks out nothing, and names as a
gap what it cannot read as the tree stands. Hand each the knowledge base's
root, the checkout where there is one, and the brief: it reads the brief first, then
any source it needs, and neither a file in the run's directory you did not
name to it nor any record of a session's conversation. Save each return to
the run's directory as it arrives, named for its stage and stance, and hand a
later stage those paths rather than your copy. Ask each, beside its work, for
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
   its stance and critique. It chooses, takes what is strong from the answers
   it did not choose, and writes the deliverable.
4. **Check.** One agent, handed the brief, the verdict and the mode's
   `check.md`, and nothing else the panel wrote; its task too replaces the
   deliverable. It confirms each concrete claim the verdict rests on and
   corrects each wrong one in place, listing what the verdict said, what the
   source shows and where. A duration resting on the user's own pace is a
   wrong claim like any other. It changes no decision: a refuted claim that a
   decision rests on heads the list, and so does each part the brief says the
   answer must settle that the verdict missed.

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

    <YYYY-MM-DD> · session <session-id> · read at <the commit of each repository the run read>

    ## Ask
    ## Brief
    ## Verdict — <your name> panel, as checked
    ## Check
    ## Rulings

`<session-id>` is this session's ID: `${CLAUDE_SESSION_ID}` in Claude Code,
the conversation ID Antigravity gives the agent, or `unknown` where the harness
gives none. The Ask is the
brief's, the Brief the brief's other parts, the Verdict's own headings one
level below the record's, and the Check its list or a line saying it found
nothing to correct. Other parties' words from a source the knowledge base keeps
out of git are cited by path, never quoted. Rulings stays empty for the user.

## Return

File each distinct line the agents returned about a skill or root document
through `suggest`, and where the run created `<the run's directory>/kb`, remove
it with `git worktree remove <the run's directory>/kb`. Return the record's
path, the verdict's decision in its own words, any refuted premise, and the
corrections, and say that the user's ruling on the record is appended to its
Rulings, verbatim and dated, by whichever session hears it. A verdict that came
back wrong is answered by a reworked ask: a new run, whose input names this
record only where the ask does.
