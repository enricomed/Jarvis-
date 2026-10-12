"""Modo show: duas palmas abrem a conversa por voz com o Jarvis.

Fica ouvindo o microfone. Ao detectar duas palmas seguidas, toca
voz/jingle.mp3 ou voz/jingle.wav (se existir) e abre uma conversa por voz
mãos-livres: você fala, ele responde, sem apertar Enter. A conversa termina
quando você diz "obrigado, Jarvis" (ou "pode encerrar", "até logo") ou fica
em silêncio duas vezes seguidas; aí ele volta a esperar palmas.
Ctrl+C encerra tudo.

Rodar a partir da pasta openjarvis/:
    uv run python ../scripts/jarvis_show.py
    uv run python ../scripts/jarvis_show.py --listar-mics
    uv run python ../scripts/jarvis_show.py --calibrar

Ajustes (variáveis de ambiente ou argumentos):
    JARVIS_CLAP_THRESH  sensibilidade, 0.05 a 0.9 (padrão 0.30).
                        Subir = menos sensível; descer = mais sensível.
    JARVIS_MIC          número ou parte do nome do microfone.
    JARVIS_PERSONA      persona da conversa (padrão: jarvis).
"""

from __future__ import annotations

import argparse
import dataclasses
import os
import json
import re
import sys
import threading
import urllib.request
import unicodedata
import time
from pathlib import Path

import numpy as np
import sounddevice as sd

RAIZ = Path(__file__).resolve().parent.parent
JINGLES = [RAIZ / "voz" / "jingle.mp3", RAIZ / "voz" / "jingle.wav"]

TAXA = 16_000
BLOCO = 512  # ~32 ms
INTERVALO_MIN = 0.12  # s entre as duas palmas
INTERVALO_MAX = 0.80
REFRATARIO = 0.08  # ignora o eco da mesma palma

FRASES_SAIDA = ("obrigado jarvis", "obrigada jarvis", "pode encerrar", "encerrar conversa",
                "ate logo", "tchau jarvis", "pode descansar")
SILENCIOS_PARA_SAIR = 2
TURNOS_DE_HISTORICO = 6
TOKENS_POR_RESPOSTA = 220  # resposta falada curta = gera e fala mais rápido
MANTER_CARREGADO_A_CADA = 240  # s; o Ollama descarrega o modelo após 5 min parado

# Pedidos que dependem da internet vão para a nuvem; o resto fica local.
GATILHOS_PESQUISA = (
    "pesquis", "procur", "busqu", "busca", "internet", "na web", "google", "site",
    "noticia", "hoje", "agora", "atual", "ultim", "recente", "esta semana", "este mes",
    "cotacao", "dolar", "euro", "bolsa", "previsao do tempo", "clima", "temperatura",
    "quem ganhou", "resultado", "placar", "preco", "quanto custa", "endereco", "horario",
)
# Se o cérebro local responder que não tem acesso à internet, refazemos na nuvem.
SINAIS_SEM_INTERNET = (
    "nao tenho acesso", "nao consigo acessar", "tempo real", "informacoes atualizadas",
    "dados atualizados", "acesso a internet", "nao posso navegar", "minha data de corte",
    "meu conhecimento", "nao tenho como verificar",
)


def escolher_mic(valor: str | None) -> int | None:
    if not valor:
        return None
    if valor.isdigit():
        return int(valor)
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0 and valor.lower() in d["name"].lower():
            return i
    print(f"Microfone '{valor}' não encontrado; usando o padrão.")
    return None


def listar_mics() -> None:
    padrao = sd.default.device[0]
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0:
            marca = " (padrão)" if i == padrao else ""
            print(f"  {i:>2}  {d['name']}{marca}")


def tocar_jingle() -> None:
    jingle = next((j for j in JINGLES if j.exists()), None)
    if jingle is None:
        return
    try:
        import soundfile as sf

        dados, taxa = sf.read(str(jingle), dtype="float32")
        sd.play(dados, taxa)
        sd.wait()
    except Exception as erro:  # jingle é enfeite: nunca impede a conversa
        print(f"(não consegui tocar o jingle: {erro})")


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", "", sem_acento.lower()).strip()


def _para_fala(texto: str) -> str:
    """Remove marcações de texto (markdown) que soariam estranhas faladas."""
    texto = re.sub(r"[*_`#>]+ ?", "", texto)
    texto = re.sub(r"^\s*[-•]\s*", "", texto, flags=re.MULTILINE)
    return texto.strip()


class Conversa:
    """Conversa por voz mãos-livres usando as peças do próprio OpenJarvis."""

    def __init__(self, persona: str) -> None:
        from openjarvis import Jarvis
        from openjarvis.cli._voice_chat import VoiceSession
        from openjarvis.core.config import load_config
        from rich.console import Console

        config = load_config()
        config.memory_files = dataclasses.replace(config.memory_files, persona_name=persona)
        self.console = Console()
        self.jarvis = Jarvis(config=config)
        self.voz = VoiceSession(config)
        self.modelo = config.intelligence.default_model or None
        self.nuvem = bool(os.environ.get("ANTHROPIC_API_KEY"))
        self.host_ollama = getattr(getattr(config.engine, "ollama", None), "host", "") or "http://localhost:11434"

    def aquecer(self) -> None:
        """Carrega cérebro, ouvidos e voz antes da primeira palma."""
        t = time.monotonic()
        self.console.print("[dim]1/3 Carregando o cérebro (pode levar até 1 minuto)…[/dim]")
        try:
            self.jarvis.ask("Responda só: ok", agent="simple", model=self.modelo, max_tokens=5)
        except Exception as erro:
            self.console.print(f"[yellow]Aviso: o cérebro não respondeu no aquecimento ({erro}).[/yellow]")
        self.console.print("[dim]2/3 Carregando os ouvidos…[/dim]")
        self.voz.get_stt_backend()
        self.console.print("[dim]3/3 Carregando a voz…[/dim]")
        tts = self.voz.get_tts_backend()
        if tts is not None:
            try:
                voz_id, _ = self.voz.voice_for_backend(tts)
                tts.synthesize("ok", voice_id=voz_id, output_format="wav")
            except Exception:
                pass
        self.console.print(f"[dim]Pronto em {time.monotonic() - t:.0f} s.[/dim]")
        threading.Thread(target=self._manter_carregado, daemon=True).start()

    def _manter_carregado(self) -> None:
        """Pede ao Ollama para manter o modelo na memória (evita recarregar a cada palma)."""
        if not self.modelo:
            return
        # Mesmo num_ctx que o OpenJarvis usa nas perguntas: se for diferente,
        # o Ollama recarrega o modelo inteiro a cada pedido.
        try:
            from openjarvis.engine.ollama import _default_num_ctx
            num_ctx = _default_num_ctx()
        except Exception:
            num_ctx = int(os.environ.get("JARVIS_NUM_CTX", "16384"))
        corpo = json.dumps({"model": self.modelo, "keep_alive": "30m",
                            "options": {"num_ctx": num_ctx}}).encode()
        while True:
            # O aquecimento já carregou o modelo; o primeiro sinal vem depois do intervalo.
            time.sleep(MANTER_CARREGADO_A_CADA)
            try:
                req = urllib.request.Request(f"{self.host_ollama.rstrip('/')}/api/generate", data=corpo,
                                             headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=60).read()
            except Exception:
                pass

    def falar(self, texto: str) -> None:
        from openjarvis.cli._voice_chat import speak

        speak(_para_fala(texto), self.console, self.voz)

    def rodar(self) -> None:
        from openjarvis.cli._voice_chat import VOICE_EXIT, record_voice

        historico: list[tuple[str, str]] = []
        silencios = 0
        self.falar("Pois não, Doutor?")
        while True:
            t_ouvir = time.monotonic()
            fala = record_voice(self.console, self.voz)
            if isinstance(fala, str) and fala:
                self.console.print(f"[dim](ouvir + transcrever {time.monotonic() - t_ouvir:.1f} s)[/dim]")
            if fala is VOICE_EXIT:
                return
            if not fala:
                silencios += 1
                if silencios >= SILENCIOS_PARA_SAIR:
                    self.falar("Estarei por aqui, Doutor.")
                    return
                continue
            silencios = 0
            if any(f in _normalizar(fala) for f in FRASES_SAIDA):
                self.falar("Até logo, Doutor.")
                return

            pesquisa = any(g in _normalizar(fala) for g in GATILHOS_PESQUISA)
            if pesquisa and not self.nuvem:
                self.falar("Para pesquisar na internet, falta configurar a chave da nuvem, Doutor.")
                continue
            t_pensar = time.monotonic()
            try:
                if pesquisa:
                    resposta = self._pesquisar(historico, fala)
                else:
                    self.console.print("[dim]Pensando…[/dim]")
                    resposta = self.jarvis.ask(self._montar_pergunta(historico, fala), agent="simple",
                                               model=self.modelo, max_tokens=TOKENS_POR_RESPOSTA)
                    if self.nuvem and any(x in _normalizar(resposta) for x in SINAIS_SEM_INTERNET):
                        resposta = self._pesquisar(historico, fala)
            except Exception as erro:
                self.console.print(f"[red]Erro ao gerar resposta: {erro}[/red]")
                self.falar("Desculpe, Doutor, tive um problema para responder.")
                continue
            t_falar = time.monotonic()
            self.console.print(f"[bold cyan]Jarvis:[/bold cyan] {resposta}")
            self.falar(resposta)
            self.console.print(f"[dim](pensar {t_falar - t_pensar:.1f} s · falar {time.monotonic() - t_falar:.1f} s)[/dim]")
            historico = (historico + [(fala, resposta)])[-TURNOS_DE_HISTORICO:]

    def _pesquisar(self, historico: list[tuple[str, str]], fala: str) -> str:
        from nuvem import pesquisar

        self.console.print("[dim]Pesquisando na internet…[/dim]")
        self.falar("Um momento, vou pesquisar.")
        return pesquisar(self._montar_pergunta(historico, fala), falado=True)

    @staticmethod
    def _montar_pergunta(historico: list[tuple[str, str]], fala: str) -> str:
        partes = []
        if historico:
            partes.append("Conversa até agora:")
            for doutor, jarvis in historico:
                partes.append(f"Doutor: {doutor}\nJarvis: {jarvis}")
            partes.append("")
        partes.append(f"Fala do Doutor agora: {fala}")
        partes.append("(Conversa por voz: responda curto, em frases faladas, sem listas nem markdown.)")
        return "\n".join(partes)


def calibrar(mic: int | None) -> None:
    print("Calibrando por 6 segundos: fique em silêncio 3 s e depois bata palmas.")
    picos: list[float] = []

    def cb(indata, *_):
        picos.append(float(np.max(np.abs(indata))))

    with sd.InputStream(samplerate=TAXA, blocksize=BLOCO, channels=1, device=mic, callback=cb):
        time.sleep(6)
    meio = len(picos) // 2
    silencio = max(picos[:meio], default=0.0)
    palma = max(picos[meio:], default=0.0)
    print(f"Ruído ambiente: {silencio:.2f} | palma: {palma:.2f}")
    if palma < 0.05 or palma < 3 * silencio:
        print("O microfone quase não captou as palmas. Confira:")
        print("  1. Permissão: Ajustes do Sistema > Privacidade e Segurança > Microfone > ligue o Terminal")
        print("     (depois feche e abra o Terminal).")
        print("  2. Microfone certo: rode com --listar-mics e use JARVIS_MIC=<número>.")
        print("  3. Bata as palmas depois dos 3 primeiros segundos, perto do computador.")
        return
    sugestao = round(max(0.05, silencio + (palma - silencio) * 0.4), 2)
    print(f"Sugestão: JARVIS_CLAP_THRESH={sugestao}")


def esperar_duas_palmas(mic: int | None, limiar: float) -> None:
    estado = {"ultima": 0.0, "ruido": 0.01, "disparou": False}

    def cb(indata, *_):
        bloco = indata[:, 0]
        pico = float(np.max(np.abs(bloco)))
        rms = float(np.sqrt(np.mean(bloco**2)))
        agora = time.monotonic()
        # Palma = pico alto e bem acima do ruído de fundo (fala sustentada não passa).
        if pico >= limiar and pico > 6 * estado["ruido"]:
            dt = agora - estado["ultima"]
            if dt < REFRATARIO:
                return
            if INTERVALO_MIN <= dt <= INTERVALO_MAX:
                estado["disparou"] = True
            estado["ultima"] = agora
        else:
            estado["ruido"] = 0.95 * estado["ruido"] + 0.05 * rms

    with sd.InputStream(samplerate=TAXA, blocksize=BLOCO, channels=1, device=mic, callback=cb):
        while not estado["disparou"]:
            time.sleep(0.05)


def main() -> int:
    p = argparse.ArgumentParser(description="Duas palmas abrem o Jarvis por voz.")
    p.add_argument("--limiar", type=float, default=float(os.environ.get("JARVIS_CLAP_THRESH", "0.30")))
    p.add_argument("--mic", default=os.environ.get("JARVIS_MIC"))
    p.add_argument("--persona", default=os.environ.get("JARVIS_PERSONA", "jarvis"))
    p.add_argument("--listar-mics", action="store_true")
    p.add_argument("--calibrar", action="store_true")
    a = p.parse_args()

    if a.listar_mics:
        listar_mics()
        return 0
    mic = escolher_mic(a.mic)
    if mic is not None:
        # A gravação da conversa (OpenJarvis) usa o microfone padrão.
        sd.default.device = (mic, sd.default.device[1])
    if a.calibrar:
        calibrar(mic)
        return 0

    print("Carregando o Jarvis (ouvidos, voz e cérebro)...")
    conversa = Conversa(a.persona)
    conversa.aquecer()
    print(f"Jarvis em espera. Bata duas palmas. (limiar {a.limiar}, persona {a.persona}, Ctrl+C sai)")
    try:
        while True:
            esperar_duas_palmas(mic, a.limiar)
            print("\nPalmas detectadas.")
            tocar_jingle()
            conversa.rodar()
            print("\nDe volta à espera. Duas palmas para chamar.")
    except KeyboardInterrupt:
        print("\nAté logo, Doutor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
