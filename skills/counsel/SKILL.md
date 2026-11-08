---
name: counsel
description: Put a situation to a council of fresh advisors, each reading it from its own angle, and return one bold, direct counsel on how to tackle it, kept in `deliberations/` — invoke when the user asks for counsel or a council on a situation, or a mode of this skill hands you its ask
---

`deliberate` answers with what survives cross-examination. This skill answers how to tackle a situation, by judgement: a bold call costs only the glance it takes to reject, a hedge costs the advice, and a wrong fact the advice rests on costs both.

**Bindings.** The source of truth and the lifecycles, and the product truth and verbatim source where declared, which every agent reads wherever the reading is not sealed.

**Input.** As `deliberate`'s: an optional first line of paths, then the ask in the user's words. Nothing waits on the user but the agreement below, and where the input holds no ask, ask the user for one.

Where this skill adopts `deliberate`'s rules, its advisors stand for the proposers, their angles for the stances, the Situation for the Notes, the counsellor for the judge and the counsel for the verdict.

## Orient

The session that invokes this skill hosts the run. Read the knowledge base's homes on the situation, beyond the one the ask names, since counsel often comes from what surrounds the question, and each file the input names. The host's own view of the answer stays out of everything an agent reads, since the advisors' range is the point. A brief under `scratch/` for this ask with no record under `deliberations/` is a run the host stopped: resume it without agreeing the ask again, running only the agents whose returns are missing.

## Agree the ask

An ask's own words can steer the council in ways its writer cannot see. Before the brief, open the agreement with one message holding:

- the ask reworded to state the outcome the user wants and the horizon it runs to, narrowing the council no further than they mean
- each change from their wording and why, where it requested a form, took a premise as given, or left out what surrounds the question
- the questions the counsel would turn on that no source answers, each with what the sources suggest

Ask nothing a source answers, and leave what kind of problem it is to the council. Answer each reply the same way until the user confirms a wording, which becomes the brief's Ask; a fact the user states on the way goes in the Situation. An ask a mode hands over, or one the user says to run as written, is already agreed.

## The brief

Name the run, check the knowledge base out and gather live state as `deliberate` §The brief does, and write `brief.md` in the run's directory:

- **Ask** — the agreed ask, verbatim. By `deliberate`'s rule, talk about the run and text others wrote stay out of it
- **Deliverable** — the text of the mode's `role.md`, or of `role.md` beside this file
- **Situation** — facts, by `deliberate`'s rule for Notes: what the user is after beyond the ask, what binds them, what they have tried or ruled out, what the other people involved have said and done, and what stays unknown
- **Reading** — by `deliberate`'s rule
- **Angles** — one line each

The brief lists no parts an answer must settle.

## Angles and size

Five advisors, unless the user or the mode sets the size, each asking one question of the situation. The first two below always run. The rest come from the list or from the axes the situation turns on, chosen so that no two converge, and a mode's role may name its own in their place.

- **The real question** — what the ask stands in for, and what kind of problem that makes it, which may not be the kind the ask names
- **The boldest move** — the strongest course the situation allows, whatever exists or the effort of leaving it
- **What can't be undone** — what must come first, which outside dates bind, what closes options once done, and what can wait
- **The other side** — what each other person or institution involved wants, cannot see and cannot ignore
- **The cheap test** — what small step would settle the question before anything is committed
- **Their own record** — what has worked and failed for the user before, and what they have said they want
- **The long view** — what will matter once this is far behind them

Every agent runs at the highest reasoning effort the host offers.

## Run

Each agent runs under the rules `deliberate` §Run sets for its agents, with these stages in place of its four, and every task but the counsellor's replaces the Deliverable the brief hands its reader. A sealed reading runs as `deliberate` §A sealed reading sets out, through `seal.py` in `deliberate`'s directory.

1. **Advise.** One advisor per angle, launched together, each handed its own angle. It researches as far as the situation needs, then writes at most 300 words: what it would do, the principle that decides it, the first step, and what would change its mind. Tell it the costs this skill opens with, that a plan the ask carries is tested rather than adopted, and that each fact it states carries its source or is marked as an assumption.
2. **Spar.** Once every advice is in, one agent per angle, handed its own advice and every other: within 150 words it holds, sharpens, switches or rebuts, and ends with the advice it would now give.
3. **Counsel.** One agent, handed every advice and spar. It chooses the course it would take, never a blend of the advisors', opens source only to settle a fact the choice turns on, and writes the deliverable. It cites no working file and no record of a conversation.
4. **Check.** One agent, handed the brief, the counsel and the mode's `check.md`, and nothing else the council wrote. It confirms against the source each fact that would change a step were it false, starting with what the counsel says the problem is, and checks the counsel against `check.md`. It leaves the judgement alone and adds no caveat of its own: it corrects each wrong fact in place, and writes at the head of the counsel each refuted fact a step rests on, each step that risks a harm no one could undo and that the counsel did not weigh, and each breach of `check.md` it cannot correct in place. It returns the corrected counsel and, apart from it, each correction with its source.

## The record

Write the record as `deliberate` §The record does, under these headings:

    # <the counsel's answer, in one line>

    <YYYY-MM-DD> · <model> · session <session-id> · read at <the commit of each repository the run read>

    ## Counsel — <your name> council, as checked
    ## Ask
    ## Rulings

Nothing else about the run stands above the counsel.

## Return

As `deliberate` §Return.
