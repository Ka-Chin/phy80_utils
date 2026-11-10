# Install uv on Windows

PowerShellで以下のコマンドを実行する

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Genetate ui_state.c

-e excel template
-i input file, 古い版ui_state.c
-o output file, 新しいui_state.c

始めて実行する時に、空のui_state.cを用意してください

uv run ui_state/main.py -e resource/キー操作によるモード管理仕様v0.0.2.xlsx -i output/ui_state.c -o output/ui_state.c
