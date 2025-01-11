PYTHON?=python3
PELICAN?=pelican
PELICANOPTS=

BASEDIR=$(CURDIR)
INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
CONFFILE=$(BASEDIR)/pelicanconf.py
PUBLISHCONF=$(BASEDIR)/publishconf.py

GITHUB_PAGES_BRANCH=master
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
	rm -rfv `find . -type d -name __pycache__ \
		-o -type f -name \*.pyc`

install-pydeps:  ## Install Pelican / pydeps
	$(PYTHON) -m pip install -r requirements.txt

html:  ## Generate html.
	$(PYTHON) -m pelican $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

publish:  ## Publish
	$(PYTHON) -m pelican $(INPUTDIR) -o $(OUTPUTDIR) -s $(PUBLISHCONF) $(PELICANOPTS)

serve:  ## HTTP serve in dev mode
	$(PYTHON) -m pelican -lr $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

github:  ## Git push and publish changes on GitHub.
	${MAKE} clean
	${MAKE} publish
	git push
	ghp-import -m "Generate Pelican site" -b $(GITHUB_PAGES_BRANCH) $(OUTPUTDIR)
	git push origin $(GITHUB_PAGES_BRANCH)

create-blogpost:  ## Create a new blog post template.
	@$(PYTHON) scripts/create_blogpost.py

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

lint-all:  ## Run all linters
	${MAKE} black
	${MAKE} ruff
	${MAKE} lint-rst

# ===================================================================
# Fixers
# ===================================================================

fix-black:
	@git ls-files '*.py' | xargs $(PYTHON) -m black

fix-ruff:
	@git ls-files '*.py' | xargs $(PYTHON) -m ruff check --no-cache --fix --output-format=concise $(ARGS)

fix-all:  ## Run all code fixers.
	${MAKE} fix-ruff
	${MAKE} fix-black

# ===================================================================
# Misc
# ===================================================================

install-git-hook:  ## Install GIT pre-commit hook.
	ln -sf ../../scripts/internal/git_pre_commit.py .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

help: ## Display callable targets.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
