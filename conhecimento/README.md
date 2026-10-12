# Base de conhecimento

Coloque aqui os PDFs, textos e planilhas que o Jarvis deve consultar. **Nada desta pasta vai para o GitHub** (só este README).

Sugestões:
- Rol de Procedimentos e Eventos em Saúde da ANS (versão vigente) e o anexo das DUTs.
- RNs da ANS que você usa com frequência (ex.: junta médica, prazos de atendimento).
- Manuais e fluxos internos de autorização de OPME.
- Protocolos clínicos e diretrizes que você consulta.

Não coloque documentos com dados de pacientes.

Depois de adicionar arquivos:
```bash
cd openjarvis
uv run jarvis memory index ../conhecimento
```
