@echo off
rem Modo show (Windows): duas palmas abrem o Jarvis por voz.
rem Ajustes antes de rodar:  set JARVIS_CLAP_THRESH=0.4   e   set JARVIS_MIC=Headset
if "%JARVIS_NUM_CTX%"=="" set JARVIS_NUM_CTX=8192
set "RAIZ=%~dp0.."
cd /d "%RAIZ%\openjarvis" && uv run python "%RAIZ%\scripts\jarvis_show.py" %*
