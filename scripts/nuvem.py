"""Cérebro na nuvem (Claude): pesquisa na internet e agente de ações.

- pesquisar(): só pesquisa na web (scripts/pesquisa.sh).
- agente(): pesquisa, age no Mac (scripts/acoes_mac.py) e repassa tarefas de
  navegador ao Claude in Chrome (via Claude Code). Pede confirmação antes de
  qualquer ação que crie ou altere algo.

Usado pelo modo voz e pelo app. Precisa de ANTHROPIC_API_KEY
(configurada com scripts/chave.sh). Não envie dados de pacientes: a pergunta
sai do computador.

Uso direto (de dentro de openjarvis/):
    uv run python ../scripts/nuvem.py "últimas resoluções da ANS sobre OPME"
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

MODELO = os.environ.get("JARVIS_MODELO_NUVEM", "claude-opus-5-5")
MAX_RETOMADAS = 5  # a busca longa pode pausar (pause_turn); retomamos até 5 vezes

SISTEMA = (
    "Você é o Jarvis, assistente pessoal do Dr. Enrico Stucchi, médico, diretor "
    "médico regional da MedSenior (ES) e coordenador nacional de autorização de OPME. "
    "Pesquise na internet sempre que a resposta depender de informação atual ou "
    "que você não tenha certeza. Responda em português do Brasil, direto ao ponto, "
    "e diga de onde veio a informação (nome do site ou órgão). Nunca invente número, "
    "norma, data ou fonte; se não encontrar, diga que não encontrou."
)
ESTILO_FALADO = (
    " A resposta será falada em voz alta: no máximo quatro frases curtas, "
    "sem listas, sem markdown e sem links."
)


def pesquisar(pergunta: str, falado: bool = False) -> str:
    import anthropic

    cliente = anthropic.Anthropic()
    mensagens: list[dict] = [{"role": "user", "content": pergunta}]
    resposta = None
    for _ in range(MAX_RETOMADAS + 1):
        resposta = cliente.beta.messages.create(
            model=MODELO,
            max_tokens=4000 if falado else 16000,
            system=SISTEMA + (ESTILO_FALADO if falado else ""),
            messages=mensagens,
            tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}],
            betas=["server-side-fallback-2026-07-01"],
            extra_body={
                "fallbacks": "default",
                # Voz pede rapidez; por texto, mais cuidado.
                "output_config": {"effort": "low" if falado else "medium"},
            },
        )
        if resposta.stop_reason != "pause_turn":
            break
        mensagens.append({"role": "assistant", "content": resposta.content})

    if resposta is None or resposta.stop_reason == "refusal":
        return "Não consegui fazer essa pesquisa, Doutor."
    texto = "".join(getattr(b, "text", "") for b in resposta.content if b.type == "text").strip()
    return texto or "Não encontrei uma resposta para isso, Doutor."


# ---------------- agente de ações ----------------

SISTEMA_AGENTE = SISTEMA + (
    " Você também executa tarefas para o Doutor usando as ferramentas disponíveis: "
    "ações no Mac (abrir programas, sites e arquivos, buscar arquivos, lembretes, eventos, "
    "notas, rascunhos de e-mail, volume) e tarefa_no_chrome para qualquer coisa que precise "
    "do navegador com os logins dele (TopSaúde, sistema da operadora, Outlook Web, sites). "
    "Escolha a ferramenta certa, use datas no formato AAAA-MM-DDTHH:MM a partir da data atual "
    "informada, e ao final diga em uma ou duas frases o que foi feito. Se o Doutor não "
    "autorizar uma ação, não insista. Nunca invente que fez algo que a ferramenta não confirmou."
)

REGRAS_CHROME = (
    "Você está agindo no Chrome do Dr. Enrico Stucchi, a pedido dele, pelo assistente Jarvis. "
    "Regras obrigatórias: 1) Não envie, confirme, autorize, assine, pague, exclua nem finalize "
    "nada; prepare tudo e pare antes do clique final, dizendo o que falta ele confirmar. "
    "2) Não digite senhas; se aparecer login ou CAPTCHA, pare e avise. 3) Dados de pacientes: "
    "não copie para fora do sistema onde estão. 4) Ao terminar, responda em português, em até "
    "quatro frases, o que fez e o que ficou para ele. Tarefa: "
)

DEF_CHROME = {
    "name": "tarefa_no_chrome",
    "description": ("Repassa uma tarefa ao Claude in Chrome, que age no Chrome do Doutor com os logins "
                    "dele (TopSaúde, sistema da operadora, Outlook Web, qualquer site). Descreva a tarefa "
                    "completa e objetiva, em português. Pode levar alguns minutos."),
    "strict": True,
    "input_schema": {"type": "object", "properties": {"tarefa": {"type": "string"}},
                     "required": ["tarefa"], "additionalProperties": False},
}


def _achar_claude_code() -> str | None:
    return shutil.which("claude") or next(
        (str(p) for p in (Path.home() / ".local/bin/claude", Path.home() / ".claude/local/claude",
                          Path("/opt/homebrew/bin/claude"), Path("/usr/local/bin/claude")) if p.exists()), None)


def tarefa_no_chrome(tarefa: str, timeout: int = 900) -> str:
    """Executa a tarefa no Chrome pelo Claude Code (claude -p --chrome)."""
    claude = _achar_claude_code()
    if not claude:
        return "O Claude Code não está instalado neste Mac. Veja docs/COMO-USAR.md, seção Chrome."
    # Com chave de API no ambiente, o Claude Code desliga a integração com o Chrome:
    # ele precisa usar o login da conta Claude do Doutor.
    env = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}
    cmd = [claude, "-p", REGRAS_CHROME + tarefa, "--chrome", "--output-format", "text",
           "--allowedTools", "mcp__claude-in-chrome"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return "A tarefa no Chrome demorou demais e foi interrompida."
    saida = (r.stdout or "").strip()
    if r.returncode != 0 or not saida:
        erro = (r.stderr or r.stdout or "").strip()[-400:]
        return f"O Claude no Chrome não conseguiu concluir. Detalhe: {erro or 'sem resposta'}"
    return saida


def _executar_ferramenta(nome: str, args: dict, confirmar: Callable[[str], bool]) -> str:
    if nome == "tarefa_no_chrome":
        if not confirmar(f"pedir ao Claude no Chrome: {args.get('tarefa', '')}"):
            return "O Doutor não autorizou esta tarefa. Não foi feita."
        return tarefa_no_chrome(args.get("tarefa", ""))
    import acoes_mac

    return acoes_mac.executar(nome, args, confirmar)


def agente(pedido: str, confirmar: Callable[[str], bool], falado: bool = False,
           avisar: Callable[[str], None] = lambda texto: None) -> str:
    """Pesquisa e/ou executa o pedido com ferramentas, pedindo confirmação quando preciso."""
    import anthropic
    import acoes_mac

    cliente = anthropic.Anthropic()
    ferramentas = ([{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}]
                   + [meta["definicao"] for _, meta in acoes_mac.ACOES.values()] + [DEF_CHROME])
    agora = datetime.now().strftime("%A, %d/%m/%Y %H:%M")
    mensagens: list[dict] = [{"role": "user", "content": f"(Data e hora atuais: {agora})\n\n{pedido}"}]
    resposta = None
    for _ in range(15):
        resposta = cliente.beta.messages.create(
            model=MODELO,
            max_tokens=8000,
            system=SISTEMA_AGENTE + (ESTILO_FALADO if falado else ""),
            messages=mensagens,
            tools=ferramentas,
            betas=["server-side-fallback-2026-07-01"],
            extra_body={"fallbacks": "default", "output_config": {"effort": "medium"}},
        )
        if resposta.stop_reason == "pause_turn":
            mensagens.append({"role": "assistant", "content": resposta.content})
            continue
        if resposta.stop_reason != "tool_use":
            break
        mensagens.append({"role": "assistant", "content": resposta.content})
        resultados = []
        for bloco in resposta.content:
            if bloco.type != "tool_use":
                continue
            avisar(bloco.name)
            saida = _executar_ferramenta(bloco.name, dict(bloco.input), confirmar)
            resultados.append({"type": "tool_result", "tool_use_id": bloco.id, "content": saida})
        mensagens.append({"role": "user", "content": resultados})

    if resposta is None or resposta.stop_reason == "refusal":
        return "Não consegui fazer isso, Doutor."
    texto = "".join(getattr(b, "text", "") for b in resposta.content if b.type == "text").strip()
    return texto or "Feito, Doutor."


def main() -> int:
    if len(sys.argv) < 2:
        print('Uso: nuvem.py "sua pergunta"')
        return 1
    if sys.argv[1] != "--chrome" and not os.environ.get("ANTHROPIC_API_KEY"):
        print("Falta a chave. Rode: bash ~/jarvis/scripts/chave.sh")
        return 1
    args = sys.argv[1:]
    if args[0] == "--agente":
        def confirmar(descricao: str) -> bool:
            return input(f"Vou {descricao}. Confirma? [s/n] ").strip().lower().startswith("s")
        print(agente(" ".join(args[1:]), confirmar))
    elif args[0] == "--chrome":
        print(tarefa_no_chrome(" ".join(args[1:])))
    else:
        print(pesquisar(" ".join(args)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
