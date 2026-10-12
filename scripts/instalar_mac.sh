#!/usr/bin/env bash
# Instala o Jarvis do Dr. Enrico no Mac, do zero.
# Uso, dentro da pasta do repositório:  bash scripts/instalar_mac.sh
# Máquina com pouca memória (8 GB):     MODELO=gemma4:e2b bash scripts/instalar_mac.sh
set -euo pipefail

MODELO="${MODELO:-gemma4:e4b}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
OJ="$RAIZ/openjarvis"

passo() { printf '\n\033[1;33m==> %s\033[0m\n' "$1"; }

passo "1/8 Ferramentas de base (Homebrew, uv, Node, Git, Ollama, áudio)"
if ! command -v brew >/dev/null; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
fi
command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"; }
HOMEBREW_NO_REQUIRE_TAP_TRUST=1 brew install node git ollama portaudio espeak-ng
brew services start ollama
sleep 3  # dá tempo do Ollama subir

passo "2/8 Baixando o OpenJarvis"
if [ -d "$OJ/.git" ]; then git -C "$OJ" pull --ff-only; else git clone https://github.com/open-jarvis/OpenJarvis "$OJ"; fi
cd "$OJ"

passo "3/8 Pacotes: ouvidos (faster-whisper), voz (Kokoro) e leitura de PDF"
uv sync --extra desktop --extra voice --extra memory-pdf

passo "4/8 Baixando o cérebro: $MODELO (pode levar alguns minutos)"
ollama pull "$MODELO"

passo "5/8 Configuração inicial"
[ -f "$HOME/.openjarvis/config.toml" ] || uv run jarvis _bootstrap --write-config --engine ollama --model "$MODELO"

passo "6/8 Aplicando o seu perfil (personas, voz pf_dora, português)"
BREW_PREFIX="$(brew --prefix)"
export PHONEMIZER_ESPEAK_LIBRARY="$BREW_PREFIX/lib/libespeak-ng.dylib"
export ESPEAK_DATA_PATH="$BREW_PREFIX/share/espeak-ng-data"
uv run python "$RAIZ/scripts/aplicar_perfil.py" --modelo "$MODELO"

passo "7/8 Interface web"
(cd frontend && npm install && npm run build) || echo "Interface web falhou; o resto funciona. Veja docs/SE-TRAVAR.md."

passo "8/8 Atalho 'jarvis' no terminal e verificação"
mkdir -p "$HOME/.local/bin"
ln -sf "$OJ/.venv/bin/jarvis" "$HOME/.local/bin/jarvis"
grep -q 'PHONEMIZER_ESPEAK_LIBRARY' "$HOME/.zshrc" 2>/dev/null || cat >> "$HOME/.zshrc" <<EOF

# Jarvis (voz Kokoro)
export PHONEMIZER_ESPEAK_LIBRARY="$BREW_PREFIX/lib/libespeak-ng.dylib"
export ESPEAK_DATA_PATH="$BREW_PREFIX/share/espeak-ng-data"
export PATH="\$HOME/.local/bin:\$PATH"
EOF
uv run jarvis doctor || true
uv run jarvis ask "Em uma frase, quem é você?"

cat <<EOF

Pronto, Doutor. Feche e abra o Terminal e use:
  jarvis                                   conversa por texto
  jarvis chat --voice                      conversa por voz
  jarvis ask --persona opme "..."          pergunta rápida no modo OPME
  bash $RAIZ/scripts/show.sh               duas palmas abrem o Jarvis
Guia completo: $RAIZ/docs/COMO-USAR.md
EOF
