# Knowledge-Agent – minimales Test-Setup
# `test` fuehrt pytest aus (docs.pytest.org); die Mindest-Coverage steht in pytest.ini.
# venv bevorzugen (offizielles mcp-SDK braucht Python >=3.10)
PYTHON ?= $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)

.PHONY: test clean

test:
	$(PYTHON) -m pytest

clean:
	rm -rf .coverage coverage.xml htmlcov .pytest_cache
