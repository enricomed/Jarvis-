# Se travar

Antes de tudo: `cd openjarvis && uv run jarvis doctor`. Ele diz exatamente o que falta.

| Problema | Solução |
|---|---|
| **Mac:** brew recusa "tap não confiável" | `HOMEBREW_NO_REQUIRE_TAP_TRUST=1 brew install ollama` |
| **Windows:** winget não encontrado | Instale o "App Installer" pela Microsoft Store |
| **Windows:** comando não reconhecido logo após instalar | Feche e abra o Prompt de Comando (o PATH só atualiza em janela nova) |
| Erro com Python 3.14 | O projeto exige 3.10 a 3.13. Rode `uv python pin 3.12` dentro de `openjarvis/` e repita `uv sync --extra desktop --extra voice --extra memory-pdf` |
| `Failed to set up rate limiter: No module named 'openjarvis_rust'` ou "Rust extension: building" que nunca termina | Falta montar a peça de memória. Mac: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh -s -- -y`, feche e abra o Terminal, depois `cd ~/jarvis/openjarvis && uv run maturin develop --release -m rust/crates/openjarvis-python/Cargo.toml`. Windows: além do Rust, precisa do "Visual Studio Build Tools" (C++) |
| Pesquisa dá "Search error" ou "403" | O buscador gratuito recusou. Crie uma chave grátis em tavily.com e rode `echo 'export TAVILY_API_KEY=SUA_CHAVE' >> ~/.openjarvis/chaves.env` (troque SUA_CHAVE) |
| Pesquisa diz "Anthropic client not available" | Rode de novo `bash ~/jarvis/scripts/chave.sh` |
| Ollama não responde | Mac: `brew services start ollama`. Windows: abra o app Ollama (ícone ao lado do relógio). Ou rode `ollama serve` |
| Voz ou microfone mudos | Dê permissão de microfone ao Terminal. Mac: Ajustes → Privacidade e Segurança → Microfone. Windows: Configurações → Privacidade → Microfone |
| **Mac:** Kokoro não acha o espeak | `export PHONEMIZER_ESPEAK_LIBRARY=$(brew --prefix)/lib/libespeak-ng.dylib` e `export ESPEAK_DATA_PATH=$(brew --prefix)/share/espeak-ng-data` |
| **Windows:** Kokoro não acha o espeak (raro) | `winget install -e --id eSpeak-NG.eSpeak-NG` e `setx PHONEMIZER_ESPEAK_LIBRARY "C:\Program Files\eSpeak NG\libespeak-ng.dll"`, depois abra um terminal novo |
| Responde em inglês | Rode de novo `uv run python ../scripts/aplicar_perfil.py` e confira `uv run jarvis config show` (deve ter `language = "pt"` e `persona_name = "jarvis"`) |
| Muito lento | Troque para `gemma4:e2b` (veja COMO-USAR.md) e feche programas pesados |
| Palma abre sozinha | Suba `JARVIS_CLAP_THRESH` (ex.: 0.45) ou rode `--calibrar` |
| Palma não pega | Desça `JARVIS_CLAP_THRESH` (ex.: 0.20) ou escolha outro microfone com `JARVIS_MIC` |
| Jingle não toca | Converta para `.wav` e salve como `voz/jingle.wav` |
| Porta 8000 abre vazia | Falta o build da interface: `cd openjarvis/frontend && npm install && npm run build` |
| Instalação travou numa etapa | Plano B oficial. Mac: `curl -fsSL https://open-jarvis.github.io/OpenJarvis/install.sh \| bash`. Windows: `powershell -ExecutionPolicy ByPass -c "irm https://open-jarvis.github.io/OpenJarvis/install.ps1 \| iex"`. Depois rode só o `aplicar_perfil.py` |

**Fora da lista?** Abra o Claude Code nesta pasta, cole o erro inteiro e peça: "leia este erro, diga a causa e rode a correção".
