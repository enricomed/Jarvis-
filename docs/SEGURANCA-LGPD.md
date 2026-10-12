# Segurança e LGPD

O ponto forte deste Jarvis é que **nada sai do seu computador**: o modelo (Ollama), a transcrição (faster-whisper) e a voz (Kokoro) rodam localmente. Mesmo assim, vale seguir algumas regras simples.

## O que pode
- Discutir casos **anonimizados**: idade, sexo, diagnóstico, procedimento, materiais.
- Colocar em `conhecimento/` documentos públicos (Rol, DUTs, RNs da ANS) e manuais internos sem dado pessoal.
- Redigir comunicados, pareceres e e-mails.

## O que evitar
- Nome, CPF, número de carteirinha, endereço ou telefone de paciente. Se precisar, troque por iniciais ou "Beneficiária, 82 anos".
- Preços negociados com fornecedores em arquivos da pasta `conhecimento/` se o computador for compartilhado.
- Ligar voz ou modelo na nuvem (OpenAI, Cartesia, ElevenLabs) para conversas com dado clínico. Na nuvem, o texto sai da máquina.

## O que já está protegido neste repositório
- `conhecimento/`, `openjarvis/`, `.env` e áudios pessoais estão no `.gitignore`: não vão para o GitHub.
- A configuração usa `security.profile = personal` (uso individual).
- As personas pedem para o Jarvis lembrar de anonimizar quando aparecer dado identificável.

## Lembre
- O Jarvis é um modelo pequeno e pode errar. **A decisão técnica e a assinatura são sempre suas.** Confira norma, código e dose na fonte oficial.
- Mantenha o computador com senha e disco criptografado (Mac: FileVault; Windows: BitLocker). Os arquivos do Jarvis ficam em `~/.openjarvis/`.
