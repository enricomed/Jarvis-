#!/usr/bin/env bash
# Liga o servidor do app do Jarvis (painel + voz) em http://127.0.0.1:8765.
# Normalmente quem chama é o próprio app (Jarvis.app); dá para rodar no Terminal também.
export JARVIS_NUM_CTX="${JARVIS_NUM_CTX:-8192}"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
if command -v brew >/dev/null; then
  BREW_PREFIX="$(brew --prefix)"
  export PHONEMIZER_ESPEAK_LIBRARY="$BREW_PREFIX/lib/libespeak-ng.dylib"
  export ESPEAK_DATA_PATH="$BREW_PREFIX/share/espeak-ng-data"
fi
CHAVES="${OPENJARVIS_HOME:-$HOME/.openjarvis}/chaves.env"
# shellcheck disable=SC1090
[ -f "$CHAVES" ] && source "$CHAVES"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ/openjarvis" && exec uv run python "$RAIZ/scripts/app_jarvis.py"
