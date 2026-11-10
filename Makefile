.PHONY: check debug lint run test

check: lint test

debug:
	@uv run ./testbot.py -d

lint:
	@basedpyright .

run:
	@uv run ui_state/main.py -e resource/キー操作によるモード管理仕様v0.0.2.xlsx -i output/ui_state.c -o output/ui_state.c

test:
	@uv run pytest test/*.py
