# Implementation Quality

Code style, insight comments and structural health. Skills own procedure; a repository's own conventions live with its code or the docs written for it.

## 1. Code style

- No emojis in code
- No divider comments
- Abbreviate to a single letter or not at all, never by chomping middle letters
- Format with the repository's own formatter at the version it pins, so a change carries no formatting drift and masks none

## 2. Insight comments

Annotate any non-obvious constraint, decision or boundary. The **Cold Reader** question (`RUBRIC.md` §1) turned on a comment: what question does a reader of the *finished file* ask that it does not answer? No question, no comment. Your session is not a source of questions, and neither is the version you replaced.

Four rules govern every comment. Write each to all four; `audit-comments` grades them with a reader that never had the session.

**Format.** Single unwrapped line, no trailing period. Write a newspaper headline: the most insight in the fewest words. Cut words before splitting a line, and split before cutting the insight — a split line is a complete thought, not a continuation. No length cap; a constraint that needs the whole line gets it.

**Voice.** Code is the specification; comments narrate. The **Source Test** (`RUBRIC.md` §1) holds in a comment's form, the code being a comment's source of truth: never restate a mechanism or a symbol the source already shows. Name the mental frame, the unseen constraint, or the user-visible consequence. Two words are enough where they hand the reader a frame the code withholds.

**Tense.** Comment the present, not the change — **Ghost Correction** (`RUBRIC.md` §1) in a comment's form. A true, present-tense sentence explaining why this form is better than the one you replaced is the same failure, and survives every syntactic reading of this rule.

**Doc comments.** Where a language's tooling enforces a doc convention, the convention wins. It is an exemption from Voice, not a licence: the convention obeyed and nothing more, with insight on its own line beneath.

A comment is the deepest home a fact can have, and the cheapest: what it captures beside its line is substance no document has to hold.

## 3. Design and style review

Read the code as a senior engineer reads a colleague's PR before signing it off: for how it reads, and what the next change will cost. Correctness belongs to verification, not to this review. The output is a ranked review — the defects found, and what each remedy costs.

### Register one: the red pen

Defects visible in the code as written, each measured rather than argued.

- Functions or files past what a reader holds in one pass, or nested past enumerability
- Stages named in comments — a `// Step N` sequence is one function asking to be several
- One rule, constant or literal defined in two places, drifted or not
- A name that outlived its type or domain concept
- Dead surface — an unread field, an unreachable branch, a parameter every caller passes the same value
- Boolean parameters naming a branch the callee takes, where the caller could name the operation
- Mechanical repetition — one preamble, local type or conversion per call site
- Divergent implementations for identical jobs — one guards a case the other misses, one takes an options struct where the other takes positional flags
- Domain concepts carried as bare primitives, or values threaded through layers with no interest in them

### Register two: structural

Defects in boundaries and change propagation. These are what justify a redesign.

- **Cohesion and change amplification.** Things that change together live together; one logical change should not force edits across tiers
- **Duplication and parallel lifecycles.** Similar code is consequential duplication only where it expresses one constraint that should change once — combining paths that evolve for different reasons adds coupling
- **Ownership and boundary leakage.** A component reaching into another tier's state, bypassing its contract, or compensating repeatedly at one seam
- **Control and data flow.** Branching, temporal coordination or state passed through unrelated layers that obscures which boundary owns a decision
- **God units.** Transport, domain and persistence entangled in one package, whatever its file count

### Ranking and pricing

Rank findings by cost, dearest first, naming which cost — what the defect charges a reader, and what it charges the next change. Price each remedy beside it: fix now, park, or leave. Every abstraction charges indirection to future readers, so a remedy costing more than the friction it removes is parked with that reasoning recorded.

### Preservation inventory

Before proposing a structural move, inventory the observable contracts outside its intended delta: public inputs and outputs, persistent schemas, visible and accessibility landmarks, side effects, ordering and failure behavior. Tie each proposed boundary change to the inventory it preserves. A feature, behavior correction or contract migration is routed separately rather than riding inside the move.

### Correctness findings

A correctness defect found during a review is its own finding, reported with the contract it affects for a scope decision.

### Verification boundary

A review reads source. It can show that an implemented diff followed its agreed boundaries and declared its behavior changes; runtime preservation stays with running the app and its tests.
