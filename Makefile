.PHONY: check debug lint run test

default: run

check: lint test

debug:
	@uv run ./testbot.py -d

lint:
	@basedpyright .

run:
	@uv run python -m modbot.main

test:
	@uv run pytest test/*.py
