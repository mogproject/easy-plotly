PYTHON = python3

dev-install:
	$(PYTHON) setup.py develop

dev-uninstall:
	$(PYTHON) setup.py develop -u

lab:
	jupyter-lab

.PHONY: dev-install dev-uninstall lab
