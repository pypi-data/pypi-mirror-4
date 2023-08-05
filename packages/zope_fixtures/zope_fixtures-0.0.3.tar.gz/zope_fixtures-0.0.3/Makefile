PYTHONPATH:=$(shell pwd)/lib:${PYTHONPATH}
PYTHON ?= python

all: check

check:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m testtools.run \
	    zope_fixtures.test_suite

clean:
	find . -name '*.pyc' -print0 | xargs -0 rm -f

TAGS: lib/zope_fixtures/*.py lib/zope_fixtures/tests/*.py
	ctags -e -R lib/zope_fixtures/

tags: lib/zope_fixtures/*.py lib/zope_fixtures/tests/*.py
	ctags -R lib/zope_fixtures/

.PHONY: all check clean
