# Prompt para o Claude Code

Abra o Claude Code **dentro da pasta deste repositório** e cole o bloco abaixo inteiro.

```text
Instale o meu Jarvis local seguindo este repositório. Leia o CLAUDE.md e o README.md antes de começar.

Detecte o meu sistema (Mac ou Windows) e rode o instalador certo:
- Mac: bash scripts/instalar_mac.sh
- Windows (Prompt de Comando): scripts\instalar_windows.bat

Antes de rodar, veja quanta memória RAM o computador tem. Se tiver 8 GB ou menos, use MODELO=gemma4:e2b; senão, gemma4:e4b.

Antes de cada etapa, diga em uma frase o que vai fazer. Se um comando falhar, leia o erro inteiro, explique a causa em português simples, consulte docs/SE-TRAVAR.md e tente corrigir antes de me pedir ajuda.

No fim:
1. Rode o "jarvis doctor" e corrija o que ele apontar.
2. Teste: jarvis ask "Em uma frase, quem é você?" e jarvis ask --persona opme "Quais pontos você analisa num pedido de OPME?"
3. Rode o modo palma com --calibrar e me diga qual JARVIS_CLAP_THRESH usar.
4. Me mostre um resumo: o que foi instalado, onde ficou, quanto de disco ocupou e os comandos do dia a dia.

Regras: rode tudo local. NÃO me peça senhas nem chaves em campos do navegador. Se alguma etapa precisar de chave de API, me diga o nome da variável e eu mesmo coloco. Não envie nenhum arquivo da pasta conhecimento/ para fora do computador.
```
