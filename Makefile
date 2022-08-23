PYTHON = python3
PIP = pip3

install:
	$(PYTHON) setup.py install

uninstall:
	$(PIP) uninstall -y easy-plotly

upgrade: uninstall install

dev-install:
	$(PYTHON) setup.py develop

dev-uninstall:
	$(PYTHON) setup.py develop -u

version:
	@$(PIP) list | grep easy-plotly || echo 'Not found: easy-plotly'

lab:
	jupyter-lab

clean-notebook:
	scripts/clear_notebook_output.sh

.PHONY: install uninstall dev-install dev-uninstall version lab clean-notebook
