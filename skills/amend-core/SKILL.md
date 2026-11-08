---
name: amend-core
description: Change the rules or skills every knowledge base shares — invoke before the first edit to any file in `core/` but its suggestions
---

1. **Read `core/RUBRIC.md`.** Read it at this step, never from memory of an
   earlier read. It governs the change as it governs any document, and its §3
   governs changing a rule. A script is code as well: read `core/IMPLEMENTATION.md` §§1–2
   before editing one, and invoke `audit-comments` over it before step 6. Then
   read the suggestions file `suggest` names for each skill or root document the
   change touches, delete each line the change settles, and put each it leaves
   to the user, deleting those they decline; git keeps both.

2. **Edit the target, not the link.** Edit the file under `core/`, never a link to
   it from the knowledge base: a tool that writes by replacing a file turns a link
   into a plain copy that no longer reaches the core.

3. **Subtract first.** Where the change answers a failure, apply **Fix by
   Subtraction** before adding anything. A test that is added or changed checks
   the document, never the writer's memory.

4. **Stay domain-free.** Name no noun of one knowledge base's own. A role any
   knowledge base could fill is a binding, whether or not every one does: the core
   names the role, each knowledge base answers it among its bindings, and a step
   that uses it runs only where one is declared. A directory any knowledge base
   would keep for the same purpose is a slot the core fixes instead, its row
   saying whether git tracks it, and a step writes there unconditionally. A skill is shared when binding
   its nouns leaves its steps unchanged and it sequences no other skill through a
   knowledge base's homes, tracking or tests. Invoking a core skill or running a
   repository's own tests is not that sequencing.

5. **Keep every home true.** A rule keeps the reason its reader needs in order to
   act, and every other reason is cut. A reason cut from a rule leaves behind, in
   the rule's own words, any action it implied. A new role to bind, slot to fix or
   skill to supply takes its row in `core/README.md`. `core/sync` reads two of its
   tables: it looks for each Bind role's name, before any gloss, in each knowledge
   base's Bindings section, wherever the third cell says `Always`, and it creates
   each slot the Slots table names, with a `.gitignore` line where its row says
   ignored. It holds the read-only core's role name itself, so renaming that row
   renames its constant too. Renaming a skill or a rubric, or changing what
   one promises, breaks each file that invokes or cites it, so search this
   knowledge base for those before the edit lands, and name the rename or the
   changed promise in the commit title, which every other knowledge base's `checkin` reports when its
   sync pulls the commit.

6. **Cold read.** Run `core/sync --no-pull` where the change adds or renames a
   skill or a slot, so the knowledge base discovers it, then invoke `cold-read`
   over the change.

7. **Leave the commit to `checkin`.** Report the core's change apart from the
   knowledge base's, since every knowledge base inherits it.
