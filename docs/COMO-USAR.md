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

## Modo show ("Olá, Jarvis" ou duas palmas)

```bash
bash ~/jarvis/scripts/show.sh                     # ativação pela voz: "Olá, Jarvis" (padrão)
bash ~/jarvis/scripts/show.sh --ativacao palmas   # ativação por duas palmas
```

Como funciona:
1. Espere aparecer **"Jarvis em espera"**.
2. Diga **"Olá, Jarvis"**. Ele responde "Pois não, Doutor?". Também dá para falar tudo junto: *"Olá, Jarvis, qual a previsão do tempo para amanhã?"*.
3. **Fale normalmente.** Não precisa apertar nada: ele ouve, pensa e responde em voz. Depois volta a ouvir.
4. Para encerrar, diga **"obrigado, Jarvis"**, "pode encerrar" ou "até logo", ou fique em silêncio duas vezes. Ele volta a esperar.
5. **Ctrl + C** desliga.

Tudo é local: o computador só transcreve trechos em que há voz e procura a palavra "Jarvis". Nada sai da máquina enquanto ele espera.

Ajustes:
- Ver o que ele está ouvindo enquanto espera: `bash ~/jarvis/scripts/show.sh --mostrar`
- Microfone: `bash ~/jarvis/scripts/show.sh --listar-mics` e depois `JARVIS_MIC=<número> bash ~/jarvis/scripts/show.sh`
- Abrir já no modo OPME: `JARVIS_PERSONA=opme bash ~/jarvis/scripts/show.sh`
- Palmas: calibre com `--calibrar` e ajuste com `JARVIS_CLAP_THRESH=0.5`
- Jingle de abertura: coloque `jingle.mp3` (ou `.wav`) na pasta `voz/`

No Windows: `scripts\show.bat` (mesmas opções).

## Pesquisa na internet (cérebro na nuvem)

O Jarvis usa o Claude, na nuvem, **só quando você pede uma pesquisa**. Todo o resto continua local.

**Ligar (uma vez):**
1. Crie uma chave em **console.anthropic.com → API Keys → Create Key** (precisa de crédito na conta).
2. No Terminal: `bash ~/jarvis/scripts/chave.sh` e cole a chave quando ele pedir. Nada aparece na tela enquanto você cola, e isso é normal.

**Usar:**
- Por texto: `bash ~/jarvis/scripts/pesquisa.sh "últimas resoluções da ANS sobre OPME"`
- Por voz (modo palmas): pergunte normalmente. Ele pesquisa sozinho quando a pergunta depende da internet (palavras como "pesquise", "hoje", "notícia", "cotação", "previsão do tempo", "preço", "resultado"…) e diz "Um momento, vou pesquisar."
- Se o cérebro local responder que não tem acesso à internet, o Jarvis refaz a pergunta na nuvem automaticamente.
- A busca é feita pelo próprio Claude, nos servidores da Anthropic (não depende de buscadores gratuitos).

**Regras:**
- Não use pesquisa com nome ou dados de paciente: a pergunta sai do computador.
- Modelo padrão: Claude Opus 5.5 (o mais capaz para pesquisa). Para mudar, defina `JARVIS_MODELO_NUVEM` antes do comando, por exemplo `JARVIS_MODELO_NUVEM=claude-sonnet-5-5`.

## Ações por voz (no Mac e no Chrome)

Peça normalmente: *"Olá, Jarvis, crie um lembrete para amanhã às 9h: revisar OPME"*, *"abra o Outlook"*, *"entre no TopSaúde e veja os pedidos de OPME pendentes"*.

**Como ele confirma (tudo por voz):**
1. Antes de começar, ele diz o que vai fazer e pergunta **"Confirma?"**. Responda "sim" ou "não".
2. No Chrome, ele **prepara tudo e para antes do clique final**.
3. Para enviar, ele lê o que será enviado e pergunta **"Posso enviar?"**.
4. **Se envolver a MedSenior** (TopSaúde, operadora, OPME, guias, beneficiários, cooperados), ele pergunta de novo e **só envia se você disser "confirmo"**.

**O que ele faz no Mac:** abrir programas, sites e arquivos, buscar arquivos, criar lembretes, eventos e notas, abrir rascunho de e-mail (não envia) e ajustar volume. Não tem acesso livre ao Terminal.

**Preparar o Chrome (uma vez):**
1. Instale a extensão **Claude** (publicada pela Anthropic) na Chrome Web Store e entre com a sua conta Claude.
2. Instale o Claude Code no Mac: `curl -fsSL https://claude.ai/install.sh | bash`
3. Abra o Terminal, digite `claude`, faça login **com a sua conta Claude** (não com chave de API) e digite `/chrome` → ative **"Enabled by default"**.
4. Teste: `cd ~/jarvis/openjarvis && uv run python ../scripts/nuvem.py --chrome "Abra o site da ANS e diga o título da página"`

Na primeira vez que ele mexer em Lembretes, Calendário ou Notas, o Mac pergunta se o Terminal pode controlar esses apps: clique em **OK**.

**Antes de usar nos sistemas da MedSenior:** confirme a liberação com a TI e o DPO.

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
