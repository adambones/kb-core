---
name: improve-docs
description: Rewrite a set of durable documents whole for the reader — redraw where they divide, gather what drifted apart, and write each from its points — changing no claim; invoke when documents have grown hard to read through incremental edits
---

**Bindings.** The lifecycles, and the shared repositories where declared.

**Input.** The documents to rewrite, a directory meaning every markdown file
in it, and any rubric or reference the blueprint and the writers read beside
`RUBRIC.md`. Where the input names no document, return that and stop.

The run's directory is `scratch/improve-docs-<stem>-<YYYY-MM-DD>/`, the stem a
kebab-case name for the set. Every agent is fresh, runs at the highest
reasoning effort the host offers, and changes nothing beyond what its step
names. Save each return to the run's directory as it arrives and hand a later
step those paths.

## 1. Decompose

One agent per document, all launched together, each handed its document
alone. It returns every point the document makes, one per line in the
document's own words with the lines it came from: the claim or contract, the
reason or failure mode behind it, and each symbol, path and link it carries. A
paragraph or bullet holding several points returns several lines, each naming
the subject it describes.

## 2. Blueprint

One agent, handed every return from step 1, `RUBRIC.md` and the rubrics the
input names. It searches the knowledge base and every checkout under `code/`
for references to the documents from outside the set, by path or by name, and
writes `blueprint.md` to the run's directory:

- The documents the set becomes, each with its subject in one sentence and its
  path beside the documents it draws on (**Altitude**, `RUBRIC.md` §2): a
  sub-area grown into a subject of its own becomes a document, a document whose
  points belong inside another's subject merges into it, and a boundary that
  cannot be stated in one sentence stays as it is
- Under each document, its sections in order from orientation to mechanics,
  and under each section the points it holds, each by its source document and
  lines (**One Home**, `RUBRIC.md` §1): the points on one concern sit in one
  section wherever they came from, and two points saying the same thing become
  one
- Each reference from outside the set, with the document and section it
  resolves to once the set is written

## 3. Check the blueprint

One agent, handed the blueprint and the input documents. It confirms that
every point in the input documents, read from the documents themselves and
never from step 1's returns, is routed to a section, and that each point the
blueprint merged says the same thing as the point it merged into. A miss it
fixes in the blueprint before any writer launches, and its return is what it
fixed.

## 4. Write

One agent per document in the blueprint, all launched together, each handed
that document's part of the blueprint, `RUBRIC.md`, the rubrics and
references the input names, and nothing else of the set. It writes the
document whole, over the path the blueprint names: a document a person or an
agent reads once and can act on, carrying every claim, reason, symbol and link
in its points.

## 5. Check each document

One agent per written document, once every writer has returned, handed the
written document, its part of the blueprint and the input documents it draws
on. It enumerates the points at the input lines the blueprint routes to this
document, from the input documents themselves, and confirms each is present
in the written document with its meaning intact, that the document asserts
nothing the input did not, and that every link and anchor in it resolves.
Each miss it fixes in the document, in the document's own voice, and its
return is what it fixed.

## 6. Land

Once every document is checked, delete each input document whose path the
blueprint's documents do not include, and point each reference from outside
the set at the document and section the blueprint names, reporting each the
run may not write. Report each boundary the set changed and each document
rewritten, one line each, and leave the commit to the knowledge base's
recording step.
