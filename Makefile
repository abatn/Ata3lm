# Knowledge-Agent – minimales Test-Setup
# `test` fuehrt pytest aus (docs.pytest.org); die Mindest-Coverage steht in pytest.ini.
PYTHON ?= python3

.PHONY: test clean

test:
	$(PYTHON) -m pytest

clean:
	rm -rf .coverage coverage.xml htmlcov .pytest_cache
