"""Ações que o Jarvis pode fazer no Mac, sempre por uma lista fechada de ferramentas.

Nada de comando livre no Terminal: cada ação é uma função pequena, com argumentos
passados como lista (sem shell). As que criam ou alteram algo pedem confirmação.
"""

from __future__ import annotations

import platform
import subprocess
from datetime import datetime
from typing import Callable


def _no_mac() -> bool:
    return platform.system() == "Darwin"


def _rodar(cmd: list[str], timeout: int = 20) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip()[:300] or "falhou")
    return r.stdout.strip()


def _texto_as(valor: str) -> str:
    """Texto seguro para dentro de AppleScript (aspas e barras escapadas)."""
    return '"' + str(valor).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _data_as(variavel: str, iso: str) -> str:
    """Linhas AppleScript que montam uma data a partir de '2026-10-13T09:30'."""
    d = datetime.fromisoformat(iso)
    return (f"set {variavel} to current date\n"
            f"set day of {variavel} to 1\n"
            f"set year of {variavel} to {d.year}\n"
            f"set month of {variavel} to {d.month}\n"
            f"set day of {variavel} to {d.day}\n"
            f"set hours of {variavel} to {d.hour}\n"
            f"set minutes of {variavel} to {d.minute}\n"
            f"set seconds of {variavel} to 0\n")


def _osascript(script: str) -> str:
    return _rodar(["osascript", "-e", script])


# ---------- ações ----------

def abrir_app(nome: str) -> str:
    _rodar(["open", "-a", nome])
    return f"Abri o {nome}."


def abrir_site(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    _rodar(["open", url])
    return f"Abri {url}."


def buscar_arquivos(termo: str, limite: int = 8) -> str:
    saida = _rodar(["mdfind", "-name", termo], timeout=30)
    achados = [linha for linha in saida.splitlines() if "/Library/" not in linha][:limite]
    if not achados:
        return f"Não encontrei arquivos com '{termo}' no nome."
    return "Encontrei:\n" + "\n".join(achados)


def abrir_arquivo(caminho: str) -> str:
    _rodar(["open", caminho])
    return f"Abri {caminho}."


def criar_lembrete(titulo: str, quando: str = "") -> str:
    props = f"name:{_texto_as(titulo)}"
    script = ""
    if quando:
        script += _data_as("d", quando)
        props += ", remind me date:d"
    script += f'tell application "Reminders" to make new reminder with properties {{{props}}}'
    _osascript(script)
    return f"Lembrete criado: {titulo}" + (f" ({quando})." if quando else ".")


def criar_evento(titulo: str, inicio: str, duracao_minutos: int = 60, agenda: str = "") -> str:
    script = _data_as("ini", inicio)
    script += f"set fim to ini + ({int(duracao_minutos)} * minutes)\n"
    alvo = f"calendar {_texto_as(agenda)}" if agenda else "first calendar whose writable is true"
    script += ('tell application "Calendar"\n'
               f"  tell {alvo}\n"
               f"    make new event with properties {{summary:{_texto_as(titulo)}, start date:ini, end date:fim}}\n"
               "  end tell\n"
               "end tell")
    _osascript(script)
    return f"Evento criado: {titulo} em {inicio}, {duracao_minutos} minutos."


def ver_agenda(dia: str) -> str:
    """Lista os eventos de um dia (AAAA-MM-DD) em todas as agendas. Só leitura."""
    script = _data_as("ini", f"{dia}T00:00")
    script += ("set fim to ini + (1 * days)\n"
               "set saida to \"\"\n"
               'tell application "Calendar"\n'
               "  repeat with ag in calendars\n"
               "    repeat with ev in (every event of ag whose start date ≥ ini and start date < fim)\n"
               "      set h to time string of (start date of ev)\n"
               "      set saida to saida & h & \" - \" & (summary of ev) & linefeed\n"
               "    end repeat\n"
               "  end repeat\n"
               "end tell\n"
               "return saida")
    saida = _rodar(["osascript", "-e", script], timeout=60)
    return ("Eventos de " + dia + ":\n" + saida) if saida else f"Nenhum evento em {dia}."


def criar_nota(titulo: str, texto: str) -> str:
    corpo = f"<h1>{titulo}</h1><p>{texto}</p>".replace("\n", "<br>")
    _osascript(f'tell application "Notes" to make new note with properties {{name:{_texto_as(titulo)}, body:{_texto_as(corpo)}}}')
    return f"Nota criada: {titulo}."


def rascunho_email(para: str, assunto: str, corpo: str) -> str:
    """Abre um rascunho no programa de e-mail padrão. Nunca envia sozinho."""
    from urllib.parse import quote

    _rodar(["open", f"mailto:{quote(para)}?subject={quote(assunto)}&body={quote(corpo)}"])
    return "Rascunho aberto no seu programa de e-mail. Revise e envie quando quiser."


def ajustar_volume(nivel: int) -> str:
    nivel = max(0, min(100, int(nivel)))
    _osascript(f"set volume output volume {nivel}")
    return f"Volume em {nivel}%."


# ---------- catálogo para o Claude ----------

def _f(nome, descricao, props, obrig, confirmar):
    return {"nome": nome, "confirmar": confirmar, "definicao": {
        "name": nome, "description": descricao, "strict": True,
        "input_schema": {"type": "object", "properties": props, "required": obrig,
                         "additionalProperties": False}}}


TXT = {"type": "string"}
ACOES = {
    "abrir_app": (abrir_app, _f("abrir_app", "Abre um programa do Mac pelo nome (ex.: Calendar, Notes, Microsoft Outlook, Google Chrome).",
                               {"nome": TXT}, ["nome"], False)),
    "abrir_site": (abrir_site, _f("abrir_site", "Abre um endereço da web no navegador.", {"url": TXT}, ["url"], False)),
    "buscar_arquivos": (buscar_arquivos, _f("buscar_arquivos", "Procura arquivos no Mac pelo nome (Spotlight). Devolve caminhos.",
                                           {"termo": TXT}, ["termo"], False)),
    "abrir_arquivo": (abrir_arquivo, _f("abrir_arquivo", "Abre um arquivo pelo caminho completo (use depois de buscar_arquivos).",
                                       {"caminho": TXT}, ["caminho"], False)),
    "criar_lembrete": (criar_lembrete, _f("criar_lembrete", "Cria um lembrete no app Lembretes. 'quando' no formato AAAA-MM-DDTHH:MM, ou vazio.",
                                         {"titulo": TXT, "quando": TXT}, ["titulo", "quando"], True)),
    "criar_evento": (criar_evento, _f("criar_evento", "Cria um evento no app Calendário. 'inicio' no formato AAAA-MM-DDTHH:MM.",
                                     {"titulo": TXT, "inicio": TXT, "duracao_minutos": {"type": "integer"}},
                                     ["titulo", "inicio", "duracao_minutos"], True)),
    "ver_agenda": (ver_agenda, _f("ver_agenda", "Lista os compromissos de um dia no app Calendário (só leitura). 'dia' no formato AAAA-MM-DD.",
                                 {"dia": TXT}, ["dia"], False)),
    "criar_nota": (criar_nota, _f("criar_nota", "Cria uma nota no app Notas.", {"titulo": TXT, "texto": TXT},
                                 ["titulo", "texto"], True)),
    "rascunho_email": (rascunho_email, _f("rascunho_email", "Abre um rascunho de e-mail (não envia).",
                                         {"para": TXT, "assunto": TXT, "corpo": TXT}, ["para", "assunto", "corpo"], True)),
    "ajustar_volume": (ajustar_volume, _f("ajustar_volume", "Ajusta o volume do Mac de 0 a 100.",
                                         {"nivel": {"type": "integer"}}, ["nivel"], False)),
}


def descrever(nome: str, args: dict) -> str:
    """Frase curta para pedir confirmação ao Doutor."""
    a = args
    return {
        "criar_lembrete": lambda: f"criar o lembrete '{a.get('titulo')}'" + (f" para {a.get('quando')}" if a.get("quando") else ""),
        "criar_evento": lambda: f"criar o evento '{a.get('titulo')}' em {a.get('inicio')}, com {a.get('duracao_minutos')} minutos",
        "criar_nota": lambda: f"criar a nota '{a.get('titulo')}'",
        "rascunho_email": lambda: f"abrir um rascunho de e-mail para {a.get('para')} com o assunto '{a.get('assunto')}'",
    }.get(nome, lambda: f"executar {nome}")()


def executar(nome: str, args: dict, confirmar: Callable[[str], bool]) -> str:
    if nome not in ACOES:
        return f"Ação desconhecida: {nome}."
    if not _no_mac():
        return "Essa ação só funciona no Mac."
    funcao, meta = ACOES[nome]
    if meta["confirmar"] and not confirmar(descrever(nome, args)):
        return "O Doutor não autorizou esta ação. Não foi feita."
    try:
        return funcao(**args)
    except Exception as erro:
        return f"Não consegui: {erro}"
