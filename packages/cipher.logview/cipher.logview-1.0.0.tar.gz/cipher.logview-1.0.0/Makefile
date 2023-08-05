# Which Python interpreter do you want to use
PYTHON = python

# Directory that will be nuked and created by 'make distcheck'
TMPDIR = tmp

# Used by make release
FILE_WITH_VERSION = setup.py
FILE_WITH_CHANGELOG = CHANGES.rst


.PHONY: all
all: bin/test

.PHONY: test
test: bin/test
	bin/test -vc

.PHONY: coverage
coverage: bin/test
	bin/test -vc --coverage=coverage

bin/test: bin/buildout buildout.cfg setup.py
	bin/buildout
	touch -c $@

bin/buildout: bootstrap.py
	$(PYTHON) bootstrap.py

.PHONY: dist
dist:
	$(PYTHON) setup.py sdist

.PHONY: distcheck
distcheck:
	@test -z "`git status -s 2>&1`" || \
	  { echo; echo "Your working tree is not clean" 1>&2; git status; exit 1; }
	$(MAKE) dist
	pkg_and_version=`$(PYTHON) setup.py --name`-`$(PYTHON) setup.py --version` && \
	  rm -rf $(TMPDIR) && \
	  mkdir $(TMPDIR) && \
	  git archive --format=tar --prefix=$(TMPDIR)/tree/ HEAD | tar -xf - && \
	  cd $(TMPDIR) && \
	  tar xvzf ../dist/$$pkg_and_version.tar.gz && \
	  diff -ur $$pkg_and_version tree -x PKG-INFO -x setup.cfg -x '*.egg-info' && \
	  cd $$pkg_and_version && \
	  $(MAKE) dist test && \
	  cd .. && \
	  mkdir one two && \
	  cd one && \
	  tar xvzf ../../dist/$$pkg_and_version.tar.gz && \
	  cd ../two/ && \
	  tar xvzf ../$$pkg_and_version/dist/$$pkg_and_version.tar.gz && \
	  cd .. && \
	  diff -ur one two -x SOURCES.txt && \
	  cd .. && \
	  rm -rf $(TMPDIR) && \
	  echo "sdist seems to be ok"

.PHONY: releasechecklist
releasechecklist:
	@$(PYTHON) setup.py --version | grep -qv dev || { \
	    echo "Please remove the 'dev' suffix from the version number in $(FILE_WITH_VERSION)"; exit 1; }
	@$(PYTHON) setup.py --long-description | rst2html --exit-status=2 > /dev/null
	@ver_and_date="`$(PYTHON) setup.py --version` (`date +%Y-%m-%d`)" && \
	    grep -q "^$$ver_and_date$$" $(FILE_WITH_CHANGELOG) || { \
	        echo "$(FILE_WITH_CHANGELOG) has no entry for $$ver_and_date"; exit 1; }
	make distcheck

.PHONY: release
release: releasechecklist
	# I'm chicken so I won't actually do these things yet
	@echo "Please run"
	@echo
	@echo "  $(PYTHON) setup.py sdist register upload && git tag v`$(PYTHON) setup.py --version`"
	@echo
	@echo "Please increment the version number in $(FILE_WITH_VERSION)"
	@echo "and add a new empty entry at the top of the changelog in $(FILE_WITH_CHANGELOG), then"
	@echo
	@echo '  git commit -a -m "Post-release version bump" && git push && git push --tags'
	@echo


