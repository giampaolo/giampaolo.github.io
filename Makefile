BASEDIR=$(CURDIR)
VENV=$(BASEDIR)/.venv
export PATH:=$(VENV)/bin:$(PATH)

PYTHON?=python3
PIP?=$(PYTHON) -m pip
PELICAN?=pelican
PELICANOPTS=

INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
CONFFILE=$(BASEDIR)/pelicanconf.py
PUBLISHCONF=$(BASEDIR)/publishconf.py

PYTEST_ARGS = -v -s --tb=short
ARGS =
DPRINT = ~/.dprint/bin/dprint
DPRINT_FILES = '*.md' '*.json' '*.jsonc' '*.yml' '*.yaml' '*.js' '*.css'

DEBUG ?= 0
ifeq ($(DEBUG), 1)
	PELICANOPTS += -D
endif

RELATIVE ?= 0
ifeq ($(RELATIVE), 1)
	PELICANOPTS += --relative-urls
endif

clean:  ## Remove build files
	rm -rf $(OUTPUTDIR)
	@rm -rfv `find . \
		-type d -name __pycache__ \
		-o -type f -name \*.pyc`
	@rm -rfv \
		.pytest_cache \
		.ruff_cache/

install-sysdeps:  ## Install system deps
	test -x $(DPRINT) || curl -fsSL https://dprint.dev/install.sh | sh
	$(DPRINT) --version

install-pydeps:  ## Install python deps into .venv
	test -d $(VENV) || python3 -m venv --upgrade-deps $(VENV)
	$(PIP) install --group dev

install-git-hooks:  ## Install the git pre-commit hook, which rejects badly formatted commits.
	ln -sf ../../scripts/git_pre_commit.sh .git/hooks/pre-commit

html:  ## Generate html.
	$(PYTHON) -m pelican $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

build-prod:  ## Generate html for production.
	$(PYTHON) -m pelican $(INPUTDIR) -o $(OUTPUTDIR) -s $(PUBLISHCONF) $(PELICANOPTS)

autoreload:  ## HTTP serve in dev mode
	$(PYTHON) -m pelican -lr $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

create-blogpost-rst:  ## Create a new RST blog post template.
	@$(PYTHON) scripts/create_blogpost.py rst

create-blogpost-md:  ## Create a new Markdown blog post template.
	@$(PYTHON) scripts/create_blogpost.py md

update-contributions:  ## Regenerate the contributions page from GitHub.
	@$(PYTHON) scripts/update_contributions.py
	@rstwrap -q content/contributions.rst

update-inventories:  ## Refresh the Sphinx inventories used by RST roles.
	@curl -sSfL -o plugins/inventories/psutil.inv https://psutil.io/objects.inv
	@curl -sSfL -o plugins/inventories/python.inv https://docs.python.org/3/objects.inv

.PHONY: resume
resume:  ## Build resume HTML into resume/_build/ and open it.
	$(PYTHON) resume/build.py
	xdg-open resume/_build/resume.html >/dev/null 2>&1 &

test:  ## Run tests.
	$(PYTHON) -m pytest $(PYTEST_ARGS) $(ARGS) tests.py

# ===================================================================
# Linters
# ===================================================================

# Usage: $(call _ls,'*.c' '*.h'). List the tracked files matching the
# given glob(s), quoted for xargs. With STAGED=1 (set by the git hook)
# list only the staged ones, minus deletions.
_git_files = git $(if $(STAGED),diff --cached --name-only --diff-filter=d,ls-files)
_ls = $(_git_files) -- $(1) | sed 's/.*/"&"/'

ruff:  ## Run ruff linter.
	@$(call _ls,'*.py') | xargs -r $(PYTHON) -m ruff check --no-cache --output-format=concise

black:  ## Python files linting (via black)
	@$(call _ls,'*.py') | xargs -r $(PYTHON) -m black --check --safe

lint-rst:  ## Lint rst files.
	@$(call _ls,'*.rst') | xargs -r rstcheck --config=pyproject.toml
	@$(call _ls,'*.rst') | xargs -r rstwrap --check

dprint:  ## Run linter for .md / .json / .yml / .js / .css files.
	@$(call _ls,$(DPRINT_FILES)) | xargs -r $(DPRINT) check --allow-no-files

lint-toml:  ## Lint pyproject.toml.
	@$(call _ls,'*.toml') | xargs -r toml-sort --check

lint-all:  ## Run all linters
	${MAKE} black
	${MAKE} ruff
	${MAKE} lint-rst
	${MAKE} dprint
	${MAKE} lint-toml

# ===================================================================
# Fixers
# ===================================================================

fix-black:
	@$(call _ls,'*.py') | xargs -r $(PYTHON) -m black

fix-ruff:
	@$(call _ls,'*.py') | xargs -r $(PYTHON) -m ruff check --no-cache --fix --output-format=concise $(ARGS)

fix-toml:
	@$(call _ls,'*.toml') | xargs -r toml-sort

fix-rst:  ## Re-wrap .rst files.
	@$(call _ls,'*.rst') | xargs -r rstwrap

fix-dprint:  ## Reformat .md / .json / .yml / .js / .css files.
	@$(call _ls,$(DPRINT_FILES)) | xargs -r $(DPRINT) fmt --allow-no-files

fix-all:  ## Run all code fixers.
	${MAKE} fix-ruff
	${MAKE} fix-black
	${MAKE} fix-toml
	${MAKE} fix-rst
	${MAKE} fix-dprint

# ===================================================================
# Misc
# ===================================================================

help: ## Display callable targets.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
