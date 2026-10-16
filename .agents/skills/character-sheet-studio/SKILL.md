---
name: character-sheet-studio
description: Conduz a criação de character sheets (com rostos reais intocados + corpos sem cabeça) e product sheets (vistas consistentes de embalagens/produtos), incluindo suporte a troca de figurino (wardrobe swap), trava de altura relativa e closes separados de tatuagens/óculos. Use para character sheet de pessoa real, product sheet de marca ou começar/ler esta pasta dedicada. Funciona no Antigravity, Codex e Claude Code.
---

# Character Sheet & Product Sheet Studio

Você opera um estúdio guiado. Conclua o character sheet (ou product sheet) depois de receber referências e escolha de geração. Não entregue só um prompt ou instruções para o usuário fazer a imagem sozinho. Responda no idioma do usuário. Caminhos relativos deste documento partem da pasta que contém este SKILL.md, inclusive após instalação.

## Regras invariáveis

- Fotos reais frontal e de perfil: manter arquivos originais e bytes, sem geração/retoque facial, reconstrução ou crop destrutivo. Remover apenas cenário por máscara separada está autorizado; manter RGB original, face opaca e arquivo inteiro incorporado. Não enviá-las para ferramentas generativas, nem implicitamente como anexos recentes. Para análise visual local pelo assistente, pode inspecioná-las.
- IA gera somente dois corpos sem cabeça, frente e costas, mesma roupa/proporções observadas (ou a roupa-alvo escolhida pelo usuário em caso de *wardrobe swap*). Referências corporais enviadas ao provedor devem ser cópias derivadas sem rostos; nunca alterar fontes.
- Composição local em HTML com originais incorporados e PNG: 8:3, cinza #808080, zonas 29/39/32. Fotos apenas posicionadas e escaladas proporcionalmente. O compositor exige enquadramento pela cabeça e máscaras separadas para integrar os retratos ao cinza. Nunca encaixar a foto inteira como padrão. Detalhes em [references/production.md](references/production.md).
- Prioridade de modelo: GPT Image 2.5. Alternativas permitidas: Seedream 5.0 e Nano Banana 2.1. “GPT-ME 2.5” é tratado nesta experiência como referência a GPT Image 2.5, sem virar um ID de API. Resolver ID exato na conexão e respeitar a preferência da pessoa; nunca usar outro modelo ou modo Auto silenciosamente.

> **Conectores:** esta skill gera imagens/vídeos via hub. Antes de iniciar, confirme se Higgsfield, Magnific ou Google Flow está conectado neste chat. Se não estiver, lembre o usuário de habilitar o conector (passo a passo em `references/providers.md`) ou ofereça o modo manual (apenas prompts).

## Fluxo conversacional — seguir em ordem

### 1. Começar: pedir as imagens e personalizações (Rosto, Roupa, Altura ou Produto)

Ao ler esta pasta a pedido do usuário ou receber “começar”, inicie a coleta imediatamente. Não exigir instalação, escolha de ferramenta ou login antes das fotos. Aproveitar anexos/arquivos já enviados, perguntando apenas o que falta.

Mensagem inicial sugerida:

> Vamos criar seu **Character Sheet** (ou **Product Sheet**, se for para uma embalagem/produto).
> - **Para Personagem:** Envie 1 foto real do rosto de frente, 1 de perfil e 1 foto de corpo inteiro de frente (a de costas é opcional se a roupa for lisa).
> - **Personalizações opcionais (Dicas Pro da Live):**
>   1. **Troca de Look:** Quer manter a roupa da foto ou vestir outra roupa/tênis (basta anexar a referência da peça)?
>   2. **Altura (cm) e Detalhes:** Qual a altura aproximada do personagem (importante para cenas com 2+ pessoas)? Tem tatuagem no pescoço/braço ou óculos específico para guardarmos em close separado?

Se o chat não aceitar anexos, orientar a pessoa a salvar as imagens localmente e informar a pasta. Criar uma pasta de sessão no workspace atual, nunca dentro de uma skill global: `work/character-sheet-<id>/`. Mapear os papéis dos arquivos, inspecionar visualmente e registrar caminho/hash SHA-256 dos originais em `session.json` antes de transformar qualquer referência. Se o anexo estiver acessível apenas como preview, solicitar o arquivo original ou acesso local para preservar os bytes; não tirar screenshot do preview como substituto.

Foto frontal ou perfil ausente: pedir a foto real, sem fabricar vista. Sem referência corporal traseira (ex: usuário disse *"pode fazer sem a foto de costas, ele está todo de preto"*): inferir as costas com o mesmo tecido e modelagem da frente. Roupa inconsistente ou pedido de **Troca de Figurino (Wardrobe Swap)**: usar a referência de roupa/calçado enviada pelo usuário para gerar os dois corpos sem cabeça. Se o usuário pedir um **Product Sheet**, adapte o board para documentar frente, verso, lateral e close de leitura das letras/logotipo da embalagem.

### 2. Após as fotos: perguntar como e com qual modelo gerar

Inspecionar ferramentas expostas e, se útil, executar `python3 scripts/preflight.py` (somente leitura). Isso localiza CLIs, mas NÃO prova autenticação, geração nativa nem modelo disponível. Ler [references/providers.md](references/providers.md). Identificar o app pelo contexto confiável; perguntar se desconhecido.

No Codex, adaptar a pergunta às capacidades reais:

> Como prefere gerar os corpos? No próprio chat, se a geração nativa estiver disponível, ou usando Higgsfield/Magnific por conexão? Minha primeira opção é GPT Image 2.5; você também pode escolher Seedream 5.0 ou Nano Banana 2.1.

No Claude Code:

> Para gerar os corpos aqui, vamos usar uma ferramenta conectada. Você prefere Higgsfield ou Magnific, por CLI, MCP ou API? A prioridade é GPT Image 2.5; também podemos usar Seedream 5.0 ou Nano Banana 2.1, conforme o catálogo da conexão. Se ainda não estiver conectado, eu guio a configuração.

Mostrar o que já está disponível e recomendar a rota que exige menos configuração. Não oferecer rota nativa indisponível como funcional. Aceitar rota e modelo em uma única resposta. Se o usuário escolher só a rota, aplicar a prioridade anunciada quando confirmada nessa rota; se escolher só o modelo e houver mais de uma rota possível, perguntar qual conexão usar. “Pode escolher” autoriza recomendar e executar a melhor opção compatível verificada. Preferências explícitas anteriores dispensam repetir a pergunta. Não gerar enquanto espera resposta. Não afirmar que GPT Image 2.5 foi usado quando a ferramenta não informa/permite fixar a versão.

### 3. Conectar somente se necessário

Verificar conexão existente com uma operação autenticada de leitura. Não pedir novo login se funciona. Se faltar, conduzir UM passo de cada vez conforme o adaptador em providers.md: instalar ferramenta oficial quando autorizado, abrir login oficial ou configurar MCP/API. O usuário conclui autenticação/consentimento; o agente verifica conexão e catálogo depois. Nunca pedir senha/token no chat nem gravar segredos em session.json, prompts, logs ou pacote.

Não instalar software remoto só porque a pasta foi aberta. A escolha “conectar Higgsfield/Magnific” autoriza preparar essa conexão; respeitar permissões do aplicativo. Não inventar endpoint, CLI, nome de pacote ou argumento. Se não for possível verificar documentação, explicar o ponto pendente e pedir o link oficial/configuração ao usuário.

Resolver modelo e suas capacidades. Versões ausentes: explicar e perguntar entre as opções permitidas disponíveis ou outra conexão. Não trocar Nano Banana 2.1 por 2/Pro, Seedream 5.0 por 4.5, nem GPT Image 2.5 por outro GPT. Se a rota nativa não identificar o modelo, oferecer uma rota com seleção explícita; só usar versão desconhecida se a pessoa aceitar expressamente relaxar esse requisito.

### 4. Gerar, compor e verificar

Com fotos válidas, rota escolhida e conexão funcional, EXECUTAR. Não terminar com “posso gerar”. Ler [references/production.md](references/production.md) e [references/body-prompt.md](references/body-prompt.md). Preparar cópias corporais sem rostos e o prompt; gerar apenas o painel central. Se 26:25 não for aceito pelo modelo, escolher a proporção suportada mais próxima com margens e encaixar sem deformar.

Informar custo quando disponível; cumprir exigências de confirmação do provedor e orçamento autorizado, sem inventar um segundo aceite quando a escolha já autoriza a geração. Registrar ID do job assim que retornado; acompanhar até conclusão. Em timeout de envio com resultado desconhecido, consultar esse job/execução antes de reenviar; não duplicar cobrança. Download do resultado pelo método permitido pela integração. Se só houver preview, obter exportação original do centro antes de declarar entrega completa.

Inspecionar corpos e corrigir somente o centro, conforme limite de produção. Seguir [references/framing.md](references/framing.md) para close-ups e máscaras; compor com `scripts/compose.py`; não pós-processar o board. Verificar hashes iniciais dos rostos contra os arquivos de `originals/` no resultado, além de executar `--verify`. Se divergirem, não entregar como íntegro. Mostrar o PNG e entregar o HTML e relatório juntos. Registrar o modelo real, provedor, detalhes inferidos e limites em arquivo separado, sem escrever texto no board.

### 5. Retomar sem reiniciar

Manter `session.json` no workspace com `stage` (awaiting_images, awaiting_choice, awaiting_connection, ready, generating, composing, complete), fontes e hashes iniciais, roupa-alvo, inferências autorizadas, rota, modelo solicitado/ID resolvido, evidência do catálogo, orçamento se informado, job IDs e caminhos de saída. Não armazenar credenciais. Só avançar estado após evidência; esse registro é memória de progresso, não um executor automático.

Ao usuário enviar fotos, avançar para escolha. Ao escolher modelo, conectar/gerar. Ao dizer “conectei”, verificar e retomar. Ao dizer “continue”, ler sessão e continuar do ponto pendente. Não repetir perguntas respondidas nem iniciar outro job se há um pendente. Ao concluir, entregar em `outputs/character-sheet-<id>/` no workspace e marcar complete.

## Instalação opcional, feita pelo agente

### Compartilhar o pacote

Se a pessoa pedir uma skill para compartilhar, preparar um ZIP limpo com `python3 scripts/package.py --out dist/character-sheet-studio.zip` (usar outro nome se já existir). O ZIP inclui instruções de entrada e instalação, scripts, referências e metadados. Nunca compactar a pasta de trabalho inteira: excluir fotos, sessões, saídas, credenciais e caches. Compartilhar não implica instalar globalmente nem enviar o pacote a terceiros; entregar o arquivo ao usuário. A instalação abaixo só ocorre quando solicitada.

### Instalar

Se a pessoa disser “instale como skill”, execute o instalador para o app atual. Esse pedido autoriza a instalação, sem perguntar de novo. Se não houver contexto do app, perguntar Codex, Claude Code ou ambos. “Começar” ou “ler a pasta” funciona sem instalar.

```bash
python3 scripts/install.py --app codex
python3 scripts/install.py --app claude
python3 scripts/install.py --app both
```

Default: skill pessoal em `~/.agents/skills/character-sheet-studio` para Codex e `~/.claude/skills/character-sheet-studio` para Claude Code. Para projeto: acrescentar `--scope project --project /caminho/do/projeto`; o destino Codex é `.agents/skills/`, Claude é `.claude/skills/`. Para uma instalação Codex que use local legado/customizado confirmado, usar `--skills-root /caminho/exato/skills` com um só app. Não instalar cópias duplicadas em vários diretórios do mesmo app.

O instalador copia só a skill e seus recursos, sem fotos, sessões, outputs, credenciais ou arquivos de configuração global. É idempotente para a mesma versão e recusa substituir uma versão diferente. Se já existir versão diferente, explicar o conflito; atualizar somente sob pedido explícito de atualização, preservando backup. Verificar os caminhos retornados e informar a invocação: `$character-sheet-studio` no Codex ou `/character-sheet-studio` no Claude Code. Se descoberta não atualizar, reabrir a sessão ou usar o mecanismo de recarga disponível. Não declarar a skill “reconhecida pelo app” só porque a cópia funcionou.

## Dependências e falhas

Python 3.9+; Pillow para compor (requirements.txt). Segmentação local opcional: Rembg em Python compatível, conforme references/framing.md. Se faltar, preparar ambiente virtual local e instalar a dependência quando autorizado pelo trabalho/ambiente. Instalação da skill não depende de Pillow. O pacote guia um agente com acesso à pasta e ferramentas; não cria conta, créditos ou capacidade generativa nativa sozinho. Bloqueio de rede, login, modelo ou permissão: explicar o passo concreto pendente e preservar a sessão; não simular geração bem-sucedida.
