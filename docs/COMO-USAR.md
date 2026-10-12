# Como usar o seu Jarvis

No Mac, depois da instalação, `jarvis` funciona de qualquer pasta. No Windows, entre na pasta `openjarvis` e use `uv run jarvis`.

## Os 4 modos

| Modo | Quando usar | Comando |
|---|---|---|
| `jarvis` (padrão) | dúvidas rápidas, organizar o dia, ideias | `jarvis` |
| `opme` | analisar pedido, montar parecer, checar pertinência | `jarvis chat --persona opme` |
| `comunicacao` | e-mail, comunicado, resposta a beneficiário | `jarvis chat --persona comunicacao` |
| `estudo` | atualização clínica, revisar conduta | `jarvis chat --persona estudo` |

Funciona com voz também: `jarvis chat --voice --persona opme`.

## Exemplos prontos

**OPME**
```bash
jarvis ask --persona opme "Pedido de artroplastia total de joelho em paciente de 82 anos, com 2 hastes, 3 placas e cimento com antibiótico. Indicação: gonartrose grau IV. O que está compatível e o que eu questiono?"
jarvis ask --persona opme "Escreva parecer técnico pedindo complemento: falta exame de imagem e justificativa para marca específica."
```

**Comunicação**
```bash
jarvis ask --persona comunicacao "E-mail para os cooperados ortopedistas explicando que pedidos de OPME agora precisam de 3 marcas com registro ANVISA. Tom amistoso."
jarvis ask --persona comunicacao "Resposta para filha de beneficiária explicando que o material foi autorizado parcialmente e como pedir reanálise."
```

**Estudo**
```bash
jarvis ask --persona estudo "Critérios atuais para desmame ventilatório em idoso frágil, com nível de evidência."
```

## Base de conhecimento (seus PDFs)

1. Coloque arquivos em `conhecimento/` (Rol da ANS, DUTs, manuais internos de OPME, protocolos, tabelas de referência sem preços sigilosos).
2. Indexe (rode de novo sempre que acrescentar arquivos):
   ```bash
   cd openjarvis
   uv run jarvis memory index ../conhecimento
   ```
3. Pronto: nas conversas, o Jarvis busca trechos relevantes antes de responder. Para conferir o que ele acha: `uv run jarvis memory search "DUT artroplastia"`.

## Modo show (duas palmas)

```bash
bash ~/jarvis/scripts/show.sh --calibrar        # mede ruído e palma, sugere a sensibilidade
bash ~/jarvis/scripts/show.sh                   # liga o modo palmas
```

Como funciona:
1. Bata **duas palmas**. Ele toca o jingle (se houver) e diz "Pois não, Doutor?".
2. **Fale normalmente.** Não precisa apertar nada: ele ouve, pensa e responde em voz. Depois volta a ouvir.
3. Para encerrar, diga **"obrigado, Jarvis"**, "pode encerrar" ou "até logo", ou simplesmente fique em silêncio duas vezes. Ele volta a esperar palmas.
4. **Ctrl + C** desliga o modo palmas.

Ajustes:
- Sensibilidade: `JARVIS_CLAP_THRESH=0.35 bash ~/jarvis/scripts/show.sh` (subir = menos sensível).
- Microfone: `bash ~/jarvis/scripts/show.sh --listar-mics` e depois `JARVIS_MIC=<número> bash ~/jarvis/scripts/show.sh`.
- Abrir já no modo OPME: `JARVIS_PERSONA=opme bash ~/jarvis/scripts/show.sh`.

No Windows: `scripts\show.bat`, com `set JARVIS_CLAP_THRESH=0.35` antes para ajustar.

Jingle de abertura: coloque `jingle.mp3` (ou `.wav`) na pasta `voz/`.

## Pesquisa na internet (cérebro na nuvem)

O Jarvis usa o Claude, na nuvem, **só quando você pede uma pesquisa**. Todo o resto continua local.

**Ligar (uma vez):**
1. Crie uma chave em **console.anthropic.com → API Keys → Create Key** (precisa de crédito na conta).
2. No Terminal: `bash ~/jarvis/scripts/chave.sh` e cole a chave quando ele pedir. Nada aparece na tela enquanto você cola, e isso é normal.

**Usar:**
- Por texto: `bash ~/jarvis/scripts/pesquisa.sh "últimas resoluções da ANS sobre OPME"`
- Por voz (modo palmas): comece a frase com **"pesquise…"**, "procure…" ou "busque na internet…". Ele avisa "Pesquisando na internet…".

**Regras:**
- Não use pesquisa com nome ou dados de paciente: a pergunta sai do computador.
- Modelo padrão: Claude Opus 5.5 (o mais capaz para pesquisa). Para mudar, defina `JARVIS_MODELO_NUVEM` antes do comando, por exemplo `JARVIS_MODELO_NUVEM=claude-sonnet-5-5`.

**Ações em sistemas (TopSaúde, sistema da operadora, Outlook Web):** use a extensão oficial **Claude no Chrome**, não o Jarvis. Antes, confirme a liberação com a TI/DPO da MedSenior.

## Interface web

```bash
cd openjarvis && uv run jarvis start     # abre em http://127.0.0.1:8000
uv run jarvis stop                       # desliga
```

## Ajustar o jeito dele

- Quem você é e como prefere as respostas: `perfil/USER.md`
- Fatos fixos para ele lembrar: `perfil/MEMORY.md`
- Personalidade de cada modo: `perfil/personas/<modo>/SOUL.md`

Depois de editar: `cd openjarvis && uv run python ../scripts/aplicar_perfil.py`

## Trocar o cérebro

| Situação | Comando |
|---|---|
| Ficou lento | `ollama pull gemma4:e2b` e depois `uv run python ../scripts/aplicar_perfil.py --modelo gemma4:e2b` |
| Máquina forte (32 GB+), quer respostas melhores | teste um modelo maior do Ollama do mesmo jeito |
| Transcrição errando muito | `--whisper medium` no `aplicar_perfil.py` (mais pesado) |

## Voz premium (opcional, só se quiser)

A voz grátis (`pf_dora`) é boa. Use uma semana antes de pensar em pagar. Se quiser OpenAI ou Cartesia, veja a página 7 do guia original. Atenção: aí o texto das respostas sai do computador. Não use voz na nuvem para assuntos com dado de paciente.
