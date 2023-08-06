# convenience makefile to boostrap & run buildout
# use `make options=-v` to run buildout with extra options

version = 2.7
python = bin/python
options =

all: tests

.installed.cfg: bin/buildout buildout.cfg buildout.d/*.cfg setup.py
	bin/buildout $(options)

bin/buildout: $(python) buildout.cfg bootstrap.py
	$(python) bootstrap.py -d
	@touch $@

$(python):
	virtualenv -p python$(version) --no-site-packages .
	@touch $@

tests: .installed.cfg
	@bin/test
	@bin/flake8 src/niteoweb/aweber
	@for pt in `find src/niteoweb/aweber -name "*.pt"` ; do bin/zptlint $$pt; done
	@for xml in `find src/niteoweb/aweber -name "*.xml"` ; do bin/zptlint $$xml; done
	@for zcml in `find src/niteoweb/aweber -name "*.zcml"` ; do bin/zptlint $$zcml; done

clean:
	@rm -rf .installed.cfg .mr.developer.cfg bin parts develop-eggs \
		src/niteoweb.aweber.egg-info lib include .Python

.PHONY: all tests clean
