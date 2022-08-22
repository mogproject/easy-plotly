PYTHON = python3

dev-install:
	$(PYTHON) setup.py develop

dev-uninstall:
	$(PYTHON) setup.py develop -u

lab:
	jupyter-lab

clean-notebook:
	scripts/clear_notebook_output.sh

.PHONY: dev-install dev-uninstall lab clean-notebook
