.PHONY: lint test smoke ci

lint:
	pre-commit run --all-files

test:
	cd packages/sdk && pytest -q

smoke:
	python packages/sdk/examples/run_example.py

ci: lint test
