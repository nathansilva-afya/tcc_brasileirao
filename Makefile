PY = .venv/bin/python

.PHONY: install pipeline download databricks test clean

install:
	$(PY) -m pip install -r requirements.txt

pipeline:
	$(PY) -m src.pipeline

download:
	$(PY) -m src.pipeline --forcar-download

databricks:
	$(PY) -m src.pipeline --databricks

test:
	$(PY) -m pytest -q

clean:
	rm -f data/processed/*.csv data/analytics/*.csv data/exports/*.csv
