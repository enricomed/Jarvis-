#!/usr/bin/env bash
# Liga o cérebro na nuvem (Claude) para pesquisas na internet.
# Pede a chave de API sem mostrá-la na tela e guarda só neste computador.
# Uso: bash ~/jarvis/scripts/chave.sh
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
HOME_OJ="${OPENJARVIS_HOME:-$HOME/.openjarvis}"
ARQ="$HOME_OJ/chaves.env"

echo "Cole a chave da Anthropic (começa com sk-ant-) e aperte Enter."
echo "(Por segurança, nada aparece enquanto você cola.)"
read -rs CHAVE; echo
case "$CHAVE" in
  sk-ant-*) ;;
  *) echo "Isso não parece uma chave da Anthropic (deveria começar com sk-ant-). Nada foi salvo."; exit 1 ;;
esac

mkdir -p "$HOME_OJ"
umask 077
printf 'export ANTHROPIC_API_KEY=%q\n' "$CHAVE" > "$ARQ"
chmod 600 "$ARQ"
echo "Chave guardada em $ARQ (só o seu usuário consegue ler)."

echo "Instalando as peças de nuvem e pesquisa..."
cd "$RAIZ/openjarvis"
uv sync --inexact --extra desktop --extra voice --extra memory-pdf --extra inference-cloud --extra tools-search

echo "Testando..."
bash "$RAIZ/scripts/pesquisa.sh" "Qual é a data de hoje e uma notícia importante de saúde no Brasil desta semana? Responda em duas frases."
