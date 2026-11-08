.PHONY: check debug lint run test

check: lint test

debug:
	@uv run ./testbot.py -d

lint:
	@basedpyright .

run:
	@uv run ./testbot.py

test:
	@uv run pytest test/*.py
