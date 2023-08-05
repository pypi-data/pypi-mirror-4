
version = 2.7
python = bin/python
options =
quiet = --quiet

tests: bin/py.test
	bin/py.test $(quiet)

.installed.cfg: bin/buildout buildout.cfg
	bin/buildout $(options)

bin/py.test: bin/python setup.py
	bin/python setup.py $(quiet) dev
	@touch $@

bin/python:
	virtualenv-$(version) --no-site-packages $(quiet) .
	@touch $@

clean:
	@rm -rf *.egg-info/ bin/ lib/ include/ .Python .cache/ \
		.installed.cfg develop-eggs/

.PHONY: tests clean
