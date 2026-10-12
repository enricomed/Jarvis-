"""Aplica o perfil do Dr. Enrico ao OpenJarvis instalado.

Copia as personas para ~/.openjarvis/personas/ e grava as configurações
(modelo, voz em português, segurança, memória) com `jarvis config set`.

Rodar a partir da pasta openjarvis/:
    uv run python ../scripts/aplicar_perfil.py [--modelo gemma4:e2b]

Só usa a biblioteca padrão. Pode rodar quantas vezes quiser.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PERFIL = RAIZ / "perfil"


def pasta_openjarvis() -> Path:
    if os.environ.get("OPENJARVIS_HOME"):
        return Path(os.environ["OPENJARVIS_HOME"]).expanduser()
    if os.environ.get("XDG_DATA_HOME"):
        return Path(os.environ["XDG_DATA_HOME"]).expanduser() / "openjarvis"
    return Path.home() / ".openjarvis"


# Substitui o texto-base do OpenJarvis ("identifique-se como OpenJarvis"),
# que sobrepõe a persona em modelos pequenos.
PROMPT_BASE = (
    "Você é o Jarvis, assistente pessoal do Dr. Enrico Stucchi, rodando "
    "localmente no computador dele, sem nuvem. Responda sempre em português "
    "do Brasil. Se perguntarem quem você é, diga que é o Jarvis do Dr. Enrico. "
    "Siga a persona e as informações sobre o usuário abaixo. Seja direto, "
    "útil e preciso; nunca invente fatos."
)


def configuracoes(modelo: str, whisper: str) -> list[tuple[str, str]]:
    return [
        ("agent.default_system_prompt", PROMPT_BASE),
        ("engine.default", "ollama"),
        ("intelligence.default_model", modelo),
        ("security.profile", "personal"),
        ("speech.backend", "faster-whisper"),
        ("speech.model", whisper),
        ("speech.language", "pt"),
        ("speech.tts_backend", "kokoro"),
        ("speech.voice_id", "pf_dora"),
        ("memory_files.persona_name", "jarvis"),
        ("agent.context_from_memory", "true"),
    ]


def copiar_personas(home: Path) -> None:
    destino_base = home / "personas"
    for origem in sorted((PERFIL / "personas").iterdir()):
        if not origem.is_dir():
            continue
        destino = destino_base / origem.name
        destino.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origem / "SOUL.md", destino / "SOUL.md")
        # USER.md é o mesmo para todas as personas.
        shutil.copy2(PERFIL / "USER.md", destino / "USER.md")
        # MEMORY.md não é sobrescrito: o Jarvis pode ter anotado coisas nele.
        if not (destino / "MEMORY.md").exists():
            shutil.copy2(PERFIL / "MEMORY.md", destino / "MEMORY.md")
        print(f"  persona '{origem.name}' -> {destino}")


def gravar_config(chave: str, valor: str) -> bool:
    cmd = [sys.executable, "-m", "openjarvis.cli", "config", "set", chave, valor]
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = r.returncode == 0
    mostrar = valor if len(valor) <= 60 else valor[:57] + "..."
    print(f"  {'ok ' if ok else 'ERRO'} {chave} = {mostrar}")
    if not ok:
        print("       " + (r.stderr or r.stdout).strip().replace("\n", "\n       "))
    return ok


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--modelo", default="gemma4:e4b",
                   help="modelo do Ollama (máquina fraca: gemma4:e2b)")
    p.add_argument("--whisper", default="small",
                   help="tamanho do faster-whisper: base (leve), small (melhor em português)")
    a = p.parse_args()

    home = pasta_openjarvis()
    print(f"Pasta do OpenJarvis: {home}")
    if not (home / "config.toml").exists():
        print("Não achei config.toml. Rode antes:\n"
              f"  uv run jarvis _bootstrap --write-config --engine ollama --model {a.modelo}")
        return 1

    print("\n1) Personas")
    copiar_personas(home)

    print("\n2) Configurações")
    falhas = [k for k, v in configuracoes(a.modelo, a.whisper) if not gravar_config(k, v)]

    print("\nPronto." if not falhas else f"\nTerminou com {len(falhas)} falha(s): {', '.join(falhas)}")
    print("Teste: uv run jarvis ask \"Em uma frase, quem é você?\"")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
