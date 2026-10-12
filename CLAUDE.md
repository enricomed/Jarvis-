# Instruções para o Claude Code neste repositório

Este repositório personaliza o OpenJarvis (https://github.com/open-jarvis/OpenJarvis) para o Dr. Enrico Stucchi, médico, diretor médico regional da MedSenior (ES) e coordenador nacional de autorização de OPME.

## Como falar com ele
- Português do Brasil, direto e prático. Linguagem simples: ele é médico, não programador.
- Antes de cada etapa, uma frase dizendo o que vai fazer. Erros: explique a causa em português simples.

## Regras
- Tudo roda local. Não troque o backend para nuvem (OpenAI, Cartesia, ElevenLabs) sem ele pedir.
- Nunca peça senha ou chave de API em campo de navegador. Chaves: diga o nome da variável e deixe ele digitar.
- Nunca envie, cole ou suba arquivos de `conhecimento/` para serviços externos. Podem conter documentos internos.
- Não faça commit de `openjarvis/`, `conhecimento/*` (exceto o README), `.env` ou áudios pessoais.

## Mapa
- `scripts/instalar_mac.sh`, `scripts/instalar_windows.bat`: instalação completa, podem ser rodados de novo.
- `scripts/aplicar_perfil.py`: copia `perfil/personas/*` para `~/.openjarvis/personas/` e grava a config com `jarvis config set`. Rodar de dentro de `openjarvis/` com `uv run python ../scripts/aplicar_perfil.py`.
- `scripts/jarvis_show.py`: detector de duas palmas que abre `jarvis chat --voice`. Flags `--listar-mics` e `--calibrar`.
- OpenJarvis guarda tudo em `~/.openjarvis/` (`config.toml`, personas, memória).

## Fatos do OpenJarvis (conferidos no código)
- Personas: `~/.openjarvis/personas/<nome>/{SOUL,USER,MEMORY}.md`; padrão em `memory_files.persona_name`; por comando com `--persona`.
- Voz: `speech.tts_backend=kokoro`, `speech.voice_id=pf_dora`, `speech.language=pt`, `speech.backend=faster-whisper`, `speech.model=small`.
- Documentos: `jarvis memory index <pasta>` (precisa do extra `memory-pdf`); `agent.context_from_memory=true` injeta trechos na conversa.
- Python 3.10 a 3.13 (não 3.14). Não há wake word nativa; a palma é nossa.
