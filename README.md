# Install uv on Windows

PowerShellで以下のコマンドを実行する

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Genetate ui_state.c

-e excel template
-i input file, 古い版ui_state.c
-o output file, 新しいui_state.c

始めて実行する時に、空のui_state.cを用意してください

uv run ui_state/main.py -e resource/キー操作によるモード管理仕様v0.0.2.xlsx -i output/ui_state.c -o output/ui_state.c

# modbot

初回実行する時に、以下のコマンドで、必要なpackageをinstallする、visual studio build toolsがない時に、失敗になる、エラー情報を確認して、visual studioのC++ compilerをいれてください

uv sync

以下のコマンドで、実行してください

uv run python -m modbot.main
