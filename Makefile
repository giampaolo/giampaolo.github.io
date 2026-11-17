PYTHON?=python3
PIP?=$(PYTHON) -m pip
PELICAN?=pelican
PELICANOPTS=

BASEDIR=$(CURDIR)
INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
CONFFILE=$(BASEDIR)/pelicanconf.py
PUBLISHCONF=$(BASEDIR)/publishconf.py

PYTEST_ARGS = -v -s --tb=short
ARGS =

DEBUG ?= 0
ifeq ($(DEBUG), 1)
	PELICANOPTS += -D
endif

RELATIVE ?= 0
ifeq ($(RELATIVE), 1)
	PELICANOPTS += --relative-urls
endif

# install git hook
_ := $(shell mkdir -p .git/hooks/ && ln -sf ../../scripts/git_pre_commit.py .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit)

clean:  ## Remove build files
	rm -rf $(OUTPUTDIR)
	@rm -rfv `find . \
		-type d -name __pycache__ \
		-o -type f -name \*.pyc`
	@rm -rfv \
		.pytest_cache \
		.ruff_cache/

install-sysdeps:  ## Install system deps
	sudo apt install markdownlint

install-pydeps:  ## Install python deps
	$(PIP) install -r requirements.txt

html:  ## Generate html.
	$(PYTHON) -m pelican $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

build-prod:  ## Generate html for production.
	$(PYTHON) -m pelican $(INPUTDIR) -o $(OUTPUTDIR) -s $(PUBLISHCONF) $(PELICANOPTS)

autoreload:  ## HTTP serve in dev mode
	$(PYTHON) -m pelican -lr $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

create-blogpost:  ## Create a new blog post template.
	@$(PYTHON) scripts/create_blogpost.py

update-contributions:  ## Regenerate the contributions page from GitHub.
	@$(PYTHON) scripts/update_contributions.py

.PHONY: resume
resume:  ## Build resume HTML into resume/_build/ and open it.
	$(PYTHON) resume/build.py
	xdg-open resume/_build/resume.html >/dev/null 2>&1 &

test:  ## Run tests.
	$(PYTHON) -m pytest $(PYTEST_ARGS) $(ARGS) tests.py

# ===================================================================
# Linters
# ===================================================================

ruff:  ## Run ruff linter.
	@git ls-files '*.py' | xargs $(PYTHON) -m ruff check --no-cache --output-format=concise

black:  ## Python files linting (via black)
	@git ls-files '*.py' | xargs $(PYTHON) -m black --check --safe

lint-rst:  ## Lint rst files.
	@git ls-files '*.rst' | xargs rstcheck --config=pyproject.toml

lint-md:  ## Lint md files.
	@git ls-files '*.md' | xargs mdl -c .mdlrc

lint-toml:  ## Lint pyproject.toml.
	@git ls-files '*.toml' | xargs toml-sort --check

lint-all:  ## Run all linters
	${MAKE} black
	${MAKE} ruff
	${MAKE} lint-rst
	${MAKE} lint-md
	${MAKE} lint-toml

# ===================================================================
# Fixers
# ===================================================================

fix-black:
	@git ls-files '*.py' | xargs $(PYTHON) -m black

fix-ruff:
	@git ls-files '*.py' | xargs $(PYTHON) -m ruff check --no-cache --fix --output-format=concise $(ARGS)

fix-toml:
	@git ls-files '*.toml' | xargs toml-sort

fix-all:  ## Run all code fixers.
	${MAKE} fix-ruff
	${MAKE} fix-black
	${MAKE} fix-toml

# ===================================================================
# Misc
# ===================================================================

help: ## Display callable targets.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
