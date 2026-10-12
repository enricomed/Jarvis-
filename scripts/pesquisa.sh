#!/usr/bin/env bash
# Pesquisa na internet com o cérebro na nuvem (Claude), em português.
# Uso: bash ~/jarvis/scripts/pesquisa.sh "sua pergunta"
# Não use com dados de pacientes: a pergunta sai do computador.
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
ARQ="${OPENJARVIS_HOME:-$HOME/.openjarvis}/chaves.env"
[ -f "$ARQ" ] || { echo "Falta a chave. Rode: bash ~/jarvis/scripts/chave.sh"; exit 1; }
# shellcheck disable=SC1090
source "$ARQ"
MODELO="${JARVIS_MODELO_NUVEM:-claude-opus-5-5}"
cd "$RAIZ/openjarvis"
exec uv run jarvis ask -e cloud -m "$MODELO" -a orchestrator --tools web_search --persona jarvis "$*"
