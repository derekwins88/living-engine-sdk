.PHONY: lint test ci
lint:
	pre-commit run --all-files
test:
	pytest -q
ci: lint test
