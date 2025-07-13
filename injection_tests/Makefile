# standard dance to make make sane
SHELL := /bin/bash
.SHELLFLAGS := -norc -euo pipefail -c
.DEFAULT_GOAL := help

# all checks
.PHONY: all
all: lint test ## Run all checks: lint + test

# Linting
.PHONY: lint lint-ruff lint-ruff-format lint-ruff-imports lint-ruff-problems lint-ty
lint: lint-ruff lint-ty ## Lint problems in sources

lint-ruff: lint-ruff-format lint-ruff-problems ## Check python with ruff

lint-ruff-format: ## Validate python formatting
	# validate python formatting, 'make -k fix' will address issues
	uv run ruff format --diff

lint-ruff-problems: ## Check python for problems
	# check python for problems, 'make -k fix' may address some issues
	uv run ruff check

lint-ty: ## Type-check python with ty
	# check python types
	uv run ty check

# Autofixing
.PHONY: fix fix-ruff fix-ruff-format fix-ruff-imports fix-ruff-problems
fix: fix-ruff ## Fix problems in sources

.NOPARALLEL: fix-ruff
fix-ruff: fix-ruff-problems fix-ruff-format ## Fix python with ruff

fix-ruff-format: ## Fix python formatting
	# reformat python sources
	uv run ruff format

fix-ruff-problems: ## Fix python problems
	# autofix python sources: safe fixes only
	uv run ruff check --fix

# Testing git repositories
TEST_REPOS := $(wildcard data/.*.repo)
TEST_CHECKOUTS := $(patsubst data/.%.repo,data/%/.git/HEAD,$(TEST_REPOS))
TEST_CASES := $(patsubst data/%/.git/HEAD,%.testcase,$(TEST_CHECKOUTS))

# checks out a repository
.PRECIOUS: data/%/.git/HEAD
data/%/.git/HEAD: data/.%.repo
	# remove stale data: $*
	rm -rf data/$*
	# checkout: $*
	grep -v '#' $< | (cd data && xargs git clone --depth 1 --single-branch --filter=blob:none)

# run injection tests on a repository
%.testcase: data/%/.git/HEAD
	# run test: $*
	grep -v '^#' data/.$*.patterns | xargs uv run injection_tester data/$*

.PHONY: test
test: $(TEST_CASES) ## Run test cases

# Dumping syntax trees from git repositories
TEST_TREES := $(patsubst data/%/.git/HEAD,%.tree,$(TEST_CHECKOUTS))

# print syntax trees
%.tree: data/%/.git/HEAD
	# dump trees: $*
	uv run injection_tester --print --cores 1 data/$* '*.java' > data/$*-parse.txt

DUMP_OUTPUT := data/parse-dump.txt
dump: $(TEST_TREES) ## Dump syntax trees to a file
	# create combined tree dump: $(DUMP_OUTPUT)
	cat data/*-parse.txt > $(DUMP_OUTPUT)

# Development
.PHONY: env
env: ## Create virtual environment
	uv venv

.PHONY: clean
clean: ## Remove build files
	rm -rf .venv data/*-parse.txt data/*-dump.txt

# Help: ripped from cargo with small mods
.PHONY: help
help: ## Display this help screen
	@grep -E '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
