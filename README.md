# Jarvis do Dr. Enrico

Assistente de IA pessoal que roda **100% no seu computador**: ouve em português, pensa com um modelo local e responde com voz brasileira. Sem nuvem, sem conta, sem mensalidade. Por isso dá para usar com tranquilidade no dia a dia de diretoria e OPME.

Base: [OpenJarvis](https://github.com/open-jarvis/OpenJarvis) (Stanford), seguindo o guia do @marcondes.ai, com ajustes feitos para a sua rotina.

| Peça | O que faz | Escolha |
|---|---|---|
| Ouvidos | voz → texto | faster-whisper, modelo `small` (entende melhor o português que o `base` do guia) |
| Cérebro | pensa e responde | Ollama + `gemma4:e4b` (9,6 GB). Máquina com 8 GB: `gemma4:e2b` |
| Boca | texto → voz | Kokoro, voz `pf_dora` (português do Brasil) |
| Memória | lê os seus documentos | pasta `conhecimento/` (Rol, DUTs, manuais de OPME) |

## O que tem de diferente do guia original

1. **Quatro modos (personas)**, já escritos para você:
   - `jarvis`: assistente geral, direto, em português, respostas curtas na voz.
   - `opme`: analisa pedido de OPME na ordem que você usa (pertinência → cobertura → materiais → pendências → sugestão) e redige parecer.
   - `comunicacao`: e-mails e comunicados cordiais, claros, com tom amistoso e assinatura pronta.
   - `estudo`: atualização clínica de colega para colega (cirurgia geral, UTI, paciente idoso), sempre dizendo o nível da evidência.
2. **Regra de verdade embutida**: ele é instruído a nunca inventar resolução, código TUSS, registro ANVISA, dose ou referência, e a dizer quando não sabe.
3. **Cuidado com LGPD**: tudo local; ele lembra de anonimizar dado de paciente. Veja [docs/SEGURANCA-LGPD.md](docs/SEGURANCA-LGPD.md).
4. **Base de conhecimento**: coloque PDFs em `conhecimento/` e ele consulta antes de responder.
5. **App com painel holográfico**: abre pelo Dock ou Spotlight, ouve "Olá, Jarvis", mostra tudo o que ele faz e aceita comandos digitados.
6. **Ações por voz**: pesquisa na internet, lembretes, agenda, notas, arquivos e tarefas no Chrome (TopSaúde, Outlook Web), sempre com confirmação por voz e **dupla confirmação para a MedSenior**.

## Instalação (escolha uma)

Separe ~1 hora e 15 GB livres.

**A) A mais fácil: pelo Claude Code.** Abra o Claude Code dentro desta pasta e cole o texto de [PROMPT-INSTALACAO.md](PROMPT-INSTALACAO.md). Ele faz tudo e você só aprova.

**B) Mac, um comando:**
```bash
git clone https://github.com/enricomed/Jarvis- jarvis && cd jarvis
bash scripts/instalar_mac.sh
```

**C) Windows, um comando** (no Prompt de Comando, não no PowerShell):
```bat
git clone https://github.com/enricomed/Jarvis- jarvis && cd jarvis
scripts\instalar_windows.bat
```
No Windows, se o script instalar programas novos, ele pede para fechar e abrir o Prompt de Comando e rodar de novo. É normal.

Computador com 8 GB de memória: antes de instalar, use `MODELO=gemma4:e2b` (Mac) ou `set MODELO=gemma4:e2b` (Windows).

## Uso diário

```bash
jarvis                                         # conversa por texto
jarvis chat --voice                            # conversa por voz
jarvis chat --persona opme                     # modo OPME
jarvis ask --persona comunicacao "E-mail aos cooperados avisando a nova rotina de OPME"
bash scripts/criar_app_mac.sh                  # cria o app Jarvis (depois abra pelo Spotlight)
bash scripts/show.sh                           # versão Terminal: diga "Olá, Jarvis"
bash scripts/pesquisa.sh "..."                 # pesquisa na internet (nuvem, depois de scripts/chave.sh)
```

Mais exemplos em [docs/COMO-USAR.md](docs/COMO-USAR.md). Se algo travar: [docs/SE-TRAVAR.md](docs/SE-TRAVAR.md).

## Estrutura

```
perfil/            quem você é (USER.md), memória (MEMORY.md) e as 4 personas
scripts/           instalação, perfil, voz, ações, nuvem e servidor do app
app/               tela do app (painel) e ícone
conhecimento/      seus PDFs de referência (não vão para o GitHub)
voz/               jingle de abertura do modo show (opcional)
docs/              como usar, problemas comuns, segurança
openjarvis/        criado na instalação; é o OpenJarvis em si (não vai para o GitHub)
```

Para mudar o jeito do Jarvis, edite os arquivos em `perfil/` e rode de novo:
```bash
cd openjarvis && uv run python ../scripts/aplicar_perfil.py
```
