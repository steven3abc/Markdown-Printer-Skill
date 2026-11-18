@echo off
rem 開啟 Markdown Printer 圖形介面
rem 若存在 run.local.bat (自訂 Python 路徑用，不會進版本庫) 就交給它，否則使用 PATH 上的 pythonw
if exist "%~dp0run.local.bat" (
    call "%~dp0run.local.bat"
) else (
    start "" pythonw "%~dp0md_beautify.py"
)
