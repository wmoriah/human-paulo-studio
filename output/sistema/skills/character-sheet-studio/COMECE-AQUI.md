# Character Sheet Studio

1. Extraia o ZIP.
2. Abra a pasta `character-sheet-studio` como pasta de trabalho/projeto no Codex ou Claude Code. O assistente precisa poder ler os arquivos e salvar resultados nela; apenas mencionar o nome do ZIP não dá esse acesso.
3. Escreva: **“Leia esta pasta e vamos começar.”**

O assistente vai pedir suas fotos de rosto frontal, perfil e corpo inteiro frente/costas. Depois perguntará como gerar: no próprio chat quando disponível no Codex, ou por Higgsfield/Magnific via CLI, MCP ou API. A prioridade é GPT Image 2.5, com Seedream 5.0 e Nano Banana 2.1 como opções. Se faltar conexão, ele guia o login e retoma depois. Modelo e acesso são verificados na sua conta.

As fotos do rosto ficam intactas. Só os dois corpos são gerados. Você recebe o board 8:3 em PNG e um HTML que incorpora os originais, mais relatório de integridade. O cenário é ocultado por máscaras separadas; os rostos entram em close-up, com escala proporcional convencional, sem geração ou retoque. O pacote mantém quatro vistas, incluindo perfil real.

Não precisa instalar como skill. Se quiser reutilizar em outras pastas, diga **“Instale este pacote como skill no Codex”**, **“…no Claude Code”** ou **“…nos dois”**. O assistente executará o instalador incluído. Não é preciso copiar arquivos manualmente. Depois da instalação, use `$character-sheet-studio` no Codex ou `/character-sheet-studio` no Claude Code; se não aparecer, reabra a sessão.

Para instalação pelo terminal, dentro da pasta extraída, execute `python3 scripts/install.py --app codex` ou `python3 scripts/install.py --app claude`. O instalador verifica os arquivos copiados e recusa substituir uma versão diferente. Para compartilhar novamente, gere um novo pacote com `python3 scripts/package.py --out dist/character-sheet-studio.zip`; esse comando exclui sessões e resultados pessoais. O arquivo `MANIFEST.json` registra os hashes dos arquivos distribuídos.

Se o assistente apenas listar arquivos, diga **“Leia SKILL.md e execute a etapa 1 do fluxo.”** `AGENTS.md` e `CLAUDE.md` são as entradas dos respectivos aplicativos. Um pedido explícito de apenas revisar/explicar a pasta não inicia a geração.

Requisitos: acesso à pasta, Python 3.9+, Pillow para a composição e uma rota de geração habilitada. O pacote não inclui contas, chaves nem créditos. Não instale dependências para começar a conversa; elas só serão preparadas quando necessárias.
