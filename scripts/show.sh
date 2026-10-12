#!/usr/bin/env bash
# Modo show (Mac): diga "Olá, Jarvis" (ou use --ativacao palmas) para conversar por voz.
# Ajustes: --mostrar (ver o que ele ouve), JARVIS_MIC=<número>, JARVIS_PERSONA=opme
# Contexto menor = menos memória e respostas mais rápidas no modo voz.
export JARVIS_NUM_CTX="${JARVIS_NUM_CTX:-8192}"
# Chave da nuvem (pesquisas), se configurada com scripts/chave.sh.
CHAVES="${OPENJARVIS_HOME:-$HOME/.openjarvis}/chaves.env"
# shellcheck disable=SC1090
[ -f "$CHAVES" ] && source "$CHAVES"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ/openjarvis" && exec uv run python "$RAIZ/scripts/jarvis_show.py" "$@"
