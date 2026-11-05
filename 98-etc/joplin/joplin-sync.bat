@echo off
chcp 65001 >nul
echo [Joplin 동기화] 시작...
wsl.exe -d Ubuntu -- ~/miniconda3/envs/study-py312/bin/python ~/study-notes/98-etc/joplin/sync_to_joplin.py %*
echo.
pause
