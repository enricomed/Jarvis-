#!/usr/bin/env bash
# Cria o app "Jarvis" na pasta Aplicativos do usuário (abre pelo Spotlight, Launchpad ou Dock).
# Uso: bash ~/jarvis/scripts/criar_app_mac.sh
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
APP="$HOME/Applications/Jarvis.app"
mkdir -p "$HOME/Applications"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"

cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>Jarvis</string>
  <key>CFBundleDisplayName</key><string>Jarvis</string>
  <key>CFBundleIdentifier</key><string>local.enrico.jarvis</string>
  <key>CFBundleVersion</key><string>1.0</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleExecutable</key><string>Jarvis</string>
  <key>CFBundleIconFile</key><string>Jarvis</string>
  <key>LSMinimumSystemVersion</key><string>12.0</string>
  <key>NSMicrophoneUsageDescription</key><string>O Jarvis usa o microfone para ouvir "Olá, Jarvis" e os seus comandos de voz. Tudo é processado neste Mac.</string>
  <key>NSAppleEventsUsageDescription</key><string>O Jarvis controla Lembretes, Calendário e Notas quando você pede, sempre com confirmação.</string>
</dict></plist>
PLIST

cat > "$APP/Contents/MacOS/Jarvis" <<SCRIPT
#!/bin/bash
# Liga o servidor do Jarvis (se ainda não estiver no ar) e abre a janela do painel.
RAIZ="$RAIZ"
LOG="\$HOME/.openjarvis/app.log"
URL="http://127.0.0.1:8765"
mkdir -p "\$HOME/.openjarvis"
if ! /usr/bin/curl -s -m 2 "\$URL/estado" >/dev/null; then
  # O motor roda dentro do Terminal: o Mac já deu ao Terminal a permissão de microfone
  # (apps caseiros como este não recebem o pedido de permissão).
  INICIO="\$HOME/.openjarvis/iniciar_jarvis.command"
  printf '#!/bin/bash\nprintf "\\\\e]0;Jarvis (motor - deixe aberto)\\\\a"\nbash "%s/scripts/app.sh" 2>&1 | tee "%s"\n' "\$RAIZ" "\$LOG" > "\$INICIO"
  chmod +x "\$INICIO"
  open -g -a Terminal "\$INICIO"
  for i in \$(seq 1 60); do /usr/bin/curl -s -m 1 "\$URL/estado" >/dev/null && break; sleep 1; done
fi
if [ -d "/Applications/Google Chrome.app" ]; then
  open -na "Google Chrome" --args --app="\$URL" --window-size=1440,880 --user-data-dir="\$HOME/.openjarvis/chrome-app"
else
  open "\$URL"
fi
SCRIPT
chmod +x "$APP/Contents/MacOS/Jarvis"

# Ícone (.icns) a partir de app/icone.png
TMP="$(mktemp -d)"; ICON="$TMP/Jarvis.iconset"; mkdir -p "$ICON"
for t in 16 32 128 256 512; do
  sips -z $t $t "$RAIZ/app/icone.png" --out "$ICON/icon_${t}x${t}.png" >/dev/null
  sips -z $((t*2)) $((t*2)) "$RAIZ/app/icone.png" --out "$ICON/icon_${t}x${t}@2x.png" >/dev/null
done
iconutil -c icns "$ICON" -o "$APP/Contents/Resources/Jarvis.icns"
rm -rf "$TMP"

# Assinatura local: ajuda o Mac a lembrar a permissão de microfone do app.
codesign --force --deep -s - "$APP" >/dev/null 2>&1 || true
touch "$APP"
echo "App criado em: $APP"
echo "Abra pelo Spotlight (Cmd+Espaço, digite Jarvis). Para fixar no Dock: com ele aberto, clique com o botão direito no ícone > Opções > Manter no Dock."
