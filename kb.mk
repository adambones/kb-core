# kb.mk — the task runner machinery every knowledge base shares
#
# The knowledge base's root Makefile sets these, each optional, then includes this file and adds its own targets:
#   KB_NAME    := <the name help prints>
#   KB_MODULES := $(wildcard <dir>/*/Makefile)   each unit's own targets, all run from the root
# It defines ROOT, ARGS and need, and the targets help, print-% and core-sync; a .DEFAULT_GOAL of its own goes after the include
# ROOT is defined from the modules on; a value a module needs at parse time is set before the include, on $(CURDIR)
# ARGS and need are defined after the modules, so a module uses them in recipes only
# Every line here runs under GNU make 3.81, which macOS ships: no .SHELLFLAGS, .ONESHELL, undefine or $(file)

ROOT := $(CURDIR)
.DEFAULT_GOAL := help

-include $(KB_MODULES)

# The words after the first goal are its arguments, so `make <goal> <arg> <arg>` runs one target, never several
GOAL_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
ARGS := $(GOAL_ARGS)

# Each word gets an empty rule so make does not build it as a target; a command-line ARGS= never reaches this line, where a colon in it would break the parse
$(GOAL_ARGS):
	@:

# Guard for required variables, itself @-silenced (Usage: $(call need,NAME OTHER,<usage line>)); a comma in the usage line splits it
need = @$(foreach v,$(1),test -n "$($(v))" &&) true || { echo "Usage: $(2)"; exit 2; }

.PHONY: help core-sync

help: ## Show available commands (this list)
	@echo "$(KB_NAME) — available commands"; echo
	@awk 'BEGIN {FS = ":.*?## "}; /^[a-zA-Z0-9_.-]+:.*?## / { printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST) | sort
	@echo

print-%:
	@echo $*=$($*)

core-sync: ## Pull the core and link its rubric and skills into the knowledge base (Usage: make core-sync [NO_PULL=1])
	@"$(ROOT)/core/sync" $(if $(NO_PULL),--no-pull)
