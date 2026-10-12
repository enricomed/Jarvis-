#!/usr/bin/env bash
# Modo show (Mac): duas palmas abrem o Jarvis por voz.
# Ajustes: JARVIS_CLAP_THRESH=0.4 JARVIS_MIC=MacBook bash scripts/show.sh
# Contexto menor = menos memória e respostas mais rápidas no modo voz.
export JARVIS_NUM_CTX="${JARVIS_NUM_CTX:-8192}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ/openjarvis" && exec uv run python "$RAIZ/scripts/jarvis_show.py" "$@"
