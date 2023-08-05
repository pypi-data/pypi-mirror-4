# convenience makefile to boostrap & run buildout
# use `make options=-v` to run buildout with extra options

version = 2.7
python = bin/python
options =

all: docs tests

.installed.cfg: bin/buildout buildout.cfg buildout.d/*.cfg setup.py
	bin/buildout $(options)

bin/buildout: $(python) buildout.cfg bootstrap.py
	$(python) bootstrap.py -d
	@touch $@

$(python):
	virtualenv-$(version) --no-site-packages .
	@touch $@

tests: .installed.cfg
	@bin/test
	@bin/flake8 src/niteoweb/ipn/jvzoo
	@for pt in `find src/niteoweb/ipn/jvzoo -name "*.pt"` ; do bin/zptlint $$pt; done
	@for xml in `find src/niteoweb/ipn/jvzoo -name "*.xml"` ; do bin/zptlint $$xml; done
	@for zcml in `find src/niteoweb/ipn/jvzoo -name "*.zcml"` ; do bin/zptlint $$zcml; done

clean:
	@rm -rf .installed.cfg bin parts develop-eggs \
		src/niteoweb.ipn.jvzoo.egg-info lib include .Python

.PHONY: all tests clean
