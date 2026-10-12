"""App do Jarvis: painel holográfico no navegador + voz ("Olá, Jarvis") ao mesmo tempo.

Sobe um servidor local em http://127.0.0.1:8765 (só neste computador) que:
- mostra a tela do app (app/index.html);
- roda a escuta por voz em segundo plano;
- recebe pedidos digitados na tela e devolve o estado do Jarvis em tempo real.

Rodar a partir da pasta openjarvis/ (o atalho scripts/app.sh já faz isso):
    uv run python ../scripts/app_jarvis.py
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import threading
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import jarvis_show as js  # noqa: E402
from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # noqa: E402
from fastapi.responses import FileResponse, JSONResponse  # noqa: E402

PORTA = int(os.environ.get("JARVIS_PORTA", "8765"))
PERSONAS = {"jarvis": "Geral", "opme": "OPME", "comunicacao": "Comunicação", "estudo": "Estudo"}

app = FastAPI()
clientes: set[WebSocket] = set()
laco: asyncio.AbstractEventLoop | None = None
estado = {"estado": "carregando", "etapa": "Iniciando", "persona": os.environ.get("JARVIS_PERSONA", "jarvis"),
          "voz_ligada": True, "nuvem": bool(os.environ.get("ANTHROPIC_API_KEY")), "modelo": ""}
conversa: js.Conversa | None = None
ativador: js.AtivadorPorVoz | None = None
_ultimo_nivel = 0.0


def transmitir(evento: dict) -> None:
    """Envia um evento para todas as telas abertas (chamado de qualquer thread)."""
    if evento.get("estado") not in (None, "nivel"):
        estado.update({k: v for k, v in evento.items() if k in ("estado", "etapa")})
    if laco is None:
        return
    texto = json.dumps(evento, ensure_ascii=False)
    for ws in list(clientes):
        asyncio.run_coroutine_threadsafe(_enviar(ws, texto), laco)


async def _enviar(ws: WebSocket, texto: str) -> None:
    try:
        await ws.send_text(texto)
    except Exception:
        clientes.discard(ws)


def _nivel(rms: float) -> None:
    global _ultimo_nivel
    agora = time.monotonic()
    if agora - _ultimo_nivel > 0.08:  # ~12 atualizações por segundo bastam para a animação
        _ultimo_nivel = agora
        transmitir({"estado": "nivel", "valor": round(min(1.0, rms * 12), 3)})


def _escuta_por_voz() -> None:
    """Carrega tudo e fica esperando "Olá, Jarvis" (em segundo plano)."""
    global conversa, ativador
    conversa = js.Conversa(estado["persona"])
    conversa.aviso = transmitir
    conversa.confirmar_sempre_por_voz = True  # o Doutor confirma falando, nunca clicando
    estado["modelo"] = conversa.modelo or ""
    conversa.aquecer()
    transmitir({"estado": "carregando", "etapa": "Carregando a escuta"})
    try:
        ativador = js.AtivadorPorVoz(None)
        ativador.nivel = _nivel
    except Exception as erro:
        transmitir({"estado": "erro", "texto": f"Escuta por voz indisponível ({erro}). Use o campo de comando."})
        transmitir({"estado": "espera", "modelo": estado["modelo"], "nuvem": estado["nuvem"]})
        return
    transmitir({"estado": "espera", "modelo": estado["modelo"], "nuvem": estado["nuvem"]})
    while True:
        try:
            primeira = ativador.esperar()
            transmitir({"estado": "chamado"})
            js.tocar_jingle()
            if estado["voz_ligada"]:
                conversa.rodar(primeira or None)
            else:
                conversa.responder(primeira or "Olá", falado=False)
            transmitir({"estado": "espera"})
        except Exception as erro:  # nunca deixa a escuta morrer
            transmitir({"estado": "erro", "texto": f"Escuta: {erro}"})
            time.sleep(2)


def _pedido_digitado(texto: str) -> None:
    if conversa is None:
        transmitir({"estado": "erro", "texto": "Ainda carregando, Doutor. Um instante."})
        return
    resposta = conversa.responder(texto, falado=False)
    if estado["voz_ligada"]:
        conversa.falar(resposta)
    transmitir({"estado": "espera"})


@app.on_event("startup")
async def _iniciar() -> None:
    global laco
    laco = asyncio.get_running_loop()
    threading.Thread(target=_escuta_por_voz, daemon=True).start()


@app.get("/")
async def pagina() -> FileResponse:
    return FileResponse(RAIZ / "app" / "index.html")


@app.get("/estado")
async def ver_estado() -> JSONResponse:
    return JSONResponse({**estado, "personas": PERSONAS})


@app.post("/desligar")
async def desligar() -> JSONResponse:
    threading.Timer(0.5, lambda: os._exit(0)).start()
    return JSONResponse({"ok": True})


@app.websocket("/ws")
async def canal(ws: WebSocket) -> None:
    await ws.accept()
    clientes.add(ws)
    await ws.send_text(json.dumps({**estado, "estado": estado["estado"], "inicial": True}, ensure_ascii=False))
    try:
        while True:
            msg = json.loads(await ws.receive_text())
            tipo = msg.get("tipo")
            if tipo == "texto" and msg.get("texto", "").strip():
                threading.Thread(target=_pedido_digitado, args=(msg["texto"].strip(),), daemon=True).start()
            elif tipo == "ouvir" and ativador is not None:
                ativador.chamar_agora.set()
            elif tipo == "voz":
                estado["voz_ligada"] = bool(msg.get("ligada"))
                transmitir({"estado": "config", "voz_ligada": estado["voz_ligada"]})
            elif tipo == "persona" and msg.get("nome") in PERSONAS and conversa is not None:
                await asyncio.to_thread(conversa.trocar_persona, msg["nome"])
                estado["persona"] = msg["nome"]
                transmitir({"estado": "config", "persona": msg["nome"]})
    except WebSocketDisconnect:
        pass
    finally:
        clientes.discard(ws)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=PORTA, log_level="warning")
