"""Pesquisa na internet com o Claude (busca feita nos servidores da Anthropic).

Usado pelo modo palmas e por scripts/pesquisa.sh. Precisa de ANTHROPIC_API_KEY
(configurada com scripts/chave.sh). Não envie dados de pacientes: a pergunta
sai do computador.

Uso direto (de dentro de openjarvis/):
    uv run python ../scripts/nuvem.py "últimas resoluções da ANS sobre OPME"
"""

from __future__ import annotations

import os
import sys

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


def main() -> int:
    if len(sys.argv) < 2:
        print('Uso: nuvem.py "sua pergunta"')
        return 1
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Falta a chave. Rode: bash ~/jarvis/scripts/chave.sh")
        return 1
    print(pesquisar(" ".join(sys.argv[1:])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
