PY?=python3
PELICAN?=pelican
PELICANOPTS=

BASEDIR=$(CURDIR)
INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
CONFFILE=$(BASEDIR)/pelicanconf.py
PUBLISHCONF=$(BASEDIR)/publishconf.py

GITHUB_PAGES_BRANCH=master


DEBUG ?= 0
ifeq ($(DEBUG), 1)
	PELICANOPTS += -D
endif

RELATIVE ?= 0
ifeq ($(RELATIVE), 1)
	PELICANOPTS += --relative-urls
endif

help: ## Display callable targets.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-pydeps:  ## Install Pelican / pydeps
	$(PY) -m pip install pelican

html:  ## Generate html.
	$(PY) -m pelican $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

clean:  ## Remove build files
	[ ! -d $(OUTPUTDIR) ] || rm -rf $(OUTPUTDIR)
	@rm -rfv `find . -type d -name __pycache__ \
		-o -type f -name \*.pyc`

regenerate:  ## Regenerate
	$(PY) -m pelican $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

serve:  ## HTTP serve in dev mode
ifdef PORT
	$(PY) -m pelican -lr $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS) -p $(PORT)
else
	$(PY) -m pelican -lr $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)
endif

publish:  ## Publish
	$(PY) -m pelican $(INPUTDIR) -o $(OUTPUTDIR) -s $(PUBLISHCONF) $(PELICANOPTS)

github:  ## Git push and publish changes on GitHub.
	${MAKE} clean
	${MAKE} publish
	git push
	ghp-import -m "Generate Pelican site" -b $(GITHUB_PAGES_BRANCH) $(OUTPUTDIR)
	git push origin $(GITHUB_PAGES_BRANCH)

create-blogpost:  ## Create a new blog post template.
	@$(PY) -c \
		"import os, datetime; \
		now = datetime.datetime.now(); \
		root = os.path.join('content', 'blog', str(now.year)); \
		os.mkdir(root) if not os.path.exists(root) else 0; \
		fname = input('file name (e.g. new-blog-post.rst): '); \
		file = os.path.join(root, fname); \
		f = open(file, 'w'); \
		f.write('title\n'); \
		f.write('#####\n\n'); \
		f.write(':date: %s\n' % (now.strftime('%Y-%m-%d'))); \
		f.write(':tags: psutil, python\n\n'); \
		f.close(); \
		print(file);"
