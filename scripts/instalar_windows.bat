@echo off
rem Instala o Jarvis do Dr. Enrico no Windows 10/11, do zero.
rem Abra o Prompt de Comando (tecla Windows, digite cmd), entre na pasta do
rem repositorio e rode:  scripts\instalar_windows.bat
rem Maquina com pouca memoria (8 GB):  set MODELO=gemma4:e2b  antes de rodar.
setlocal enableextensions

if "%MODELO%"=="" set MODELO=gemma4:e4b
set "RAIZ=%~dp0.."
set "OJ=%RAIZ%\openjarvis"

echo.
echo ==^> 1/7 Ferramentas de base (uv, Node, Git, Ollama)
where uv >nul 2>nul || winget install -e --id astral-sh.uv --accept-source-agreements --accept-package-agreements
where node >nul 2>nul || winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
where git >nul 2>nul || winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements
where ollama >nul 2>nul || winget install -e --id Ollama.Ollama --accept-source-agreements --accept-package-agreements

rem O PATH so atualiza em janela nova. Se algo acima foi instalado agora, pare aqui.
where uv >nul 2>nul && where git >nul 2>nul && where ollama >nul 2>nul
if errorlevel 1 (
  echo.
  echo Programas instalados. FECHE este Prompt de Comando, abra outro e rode o script de novo.
  exit /b 0
)

echo.
echo ==^> 2/7 Baixando o OpenJarvis
if exist "%OJ%\.git" (git -C "%OJ%" pull --ff-only) else (git clone https://github.com/open-jarvis/OpenJarvis "%OJ%")
cd /d "%OJ%" || exit /b 1

echo.
echo ==^> 3/7 Pacotes: ouvidos, voz e leitura de PDF
uv sync --extra desktop --extra voice --extra memory-pdf || exit /b 1

echo.
echo ==^> 3b/7 Peca de memoria (Rust): necessaria para a base de conhecimento
where cargo >nul 2>nul || winget install -e --id Rustlang.Rustup --accept-source-agreements --accept-package-agreements
set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
uv run maturin develop --release -m rust\crates\openjarvis-python\Cargo.toml || echo AVISO: peca de memoria nao montou. Veja docs\SE-TRAVAR.md. O resto funciona.

echo.
echo ==^> 4/7 Baixando o cerebro: %MODELO% (pode levar alguns minutos)
ollama pull %MODELO% || (echo Abra o app Ollama ^(fica ao lado do relogio^) e rode de novo. & exit /b 1)

echo.
echo ==^> 5/7 Configuracao inicial
if not exist "%USERPROFILE%\.openjarvis\config.toml" uv run jarvis _bootstrap --write-config --engine ollama --model %MODELO%

echo.
echo ==^> 6/7 Aplicando o seu perfil (personas, voz pf_dora, portugues)
uv run python "%RAIZ%\scripts\aplicar_perfil.py" --modelo %MODELO%

echo.
echo ==^> 7/7 Interface web e verificacao
cd frontend && call npm install && call npm run build
cd /d "%OJ%"
uv run jarvis doctor
uv run jarvis ask "Em uma frase, quem e voce?"

echo.
echo Pronto, Doutor. Dentro de %OJ% use:
echo   uv run jarvis                          conversa por texto
echo   uv run jarvis chat --voice             conversa por voz
echo   uv run jarvis ask --persona opme "..." pergunta rapida no modo OPME
echo   %RAIZ%\scripts\show.bat                duas palmas abrem o Jarvis
echo Guia completo: docs\COMO-USAR.md
endlocal
