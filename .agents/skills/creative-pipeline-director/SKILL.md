---
name: creative-pipeline-director
description: Orquestra a pipeline criativa ponta a ponta (Da Ideia ao Projeto Final) segundo a metodologia da Human Academy e PAULO.IA. Conduz ideação com descarte de clichês, refutação Devil's Advocate, roteiro humano de 2 colunas, criação de assets isolados (Character Sheet, Product Sheet, Props GTA-style, Locações guiadas por cor), Storyboard ilustrado e geração final de imagem/vídeo/VFX via Sub-Skills. Use quando o usuário pedir para criar um comercial, campanha, filme curto, projeto completo com IA, ou iniciar o fluxo "Da Ideia ao Projeto".
---

# Creative Pipeline Director (Playbook & Orquestrador Mestre)

Conduza a produção criativa completa em **uma única conversa acumulativa**, alternando decisões humanas e execução de IA com **Portões de Personalização (Question Gates)** obrigatórios antes de qualquer gasto de créditos.

Inicialize ou retome sempre o estado do projeto executando:
```bash
python3 scripts/session_manager.py init --file work/project-session.json
```

---

## Arquitetura do Ecossistema (Sub-Skills Especialistas)

Acione cada especialista na etapa correspondente (ou diretamente quando o usuário quiser apenas uma tarefa avulsa):
1. **`character-sheet-studio`**: Criação de *Character Sheet* (rostos reais intocados + corpos sem cabeça) e *Product Sheet* (vistas de embalagem/produto), com suporte a troca de look e trava de altura.
2. **`experimental-angles-studio`**: Geração de 5+ ângulos radicais de câmera a partir de 1 foto (com conversão automática de `.HEIC` e atalhos para *Fisheye* / *Selfie mão na lente*).
3. **`editorial-photoshoot-studio`**: Ensaio fotográfico editorial (10 a 20 retratos em paralelo) combinando *Character Sheet* com referências estéticas do Pinterest/Savee.it.
4. **`seedance-commercial-director`**: Direção de filme publicitário multi-cenários com *Lip Sync* real (Seedance 2.5), *Shot List* sincronizada via `ffprobe`, regra `SFX Only / No Music` e fluxo econômico **Draft 480p $\rightarrow$ 1080p** (com controle de prazo de 7 dias).
5. **`cinema-vfx-supervisor`**: Direção de efeitos visuais fotorrealistas em vídeos reais (transformação gradual de cenário no Seedance/Minimax) e *Character Swap* (via Higgsfield Genjutsu, Kling Motion Control, Google Omni ou transformação no meio do take).

---

## Fluxo Guiado Ponta a Ponta (Siga em Ordem com Portões de Perguntas)

### Gate 0: Conectores (Higgsfield, Magnific, Google Flow)
Antes de qualquer etapa, verifique com uma leitura autenticada (nunca presuma) quais hubs já estão conectados e pergunte:
> **Qual hub de geração você tem conectado neste chat?**
> 1. **Higgsfield** (CLI ou conector MCP)
> 2. **Magnific** (conector MCP em `https://mcp.magnific.com`)
> 3. **Google (Flow / Omni / Nano Banana)**
> 4. **Nenhum ainda**

- Se escolher **4** ou a conexão falhar: lembre que é preciso habilitar o conector no aplicativo (Codex, Claude Code ou Antigravity), explique UM passo por vez conforme `references/providers.md`, e deixe o usuário concluir o login. Nunca peça senha ou token no chat.
- Se o usuário preferir não conectar: ofereça o **modo manual**, em que você só entrega os prompts finais para ele colar no hub.

---

### Etapa 0: Roteamento Inicial (Pergunta de Entrada)
Ao iniciar, apresente as opções de forma direta:
> **Como você quer trabalhar hoje?**
> 1. **Pipeline Completa (Da Ideia ao Projeto):** Vamos juntos desde o conceito, refutação, roteiro, assets e storyboard até o vídeo final.
> 2. **Executar uma Técnica Específica Direto:**
>    - **A)** Criar *Character Sheet* ou *Product Sheet* (`character-sheet-studio`)
>    - **B)** Variar ângulos inusitados de uma foto (`experimental-angles-studio`)
>    - **C)** Fazer um Ensaio Fotográfico Editorial (`editorial-photoshoot-studio`)
>    - **D)** Gerar Vídeo Comercial com Lip Sync e múltiplos cenários (`seedance-commercial-director`)
>    - **E)** Aplicar Efeitos Visuais (VFX) ou Trocar Personagem em vídeo real (`cinema-vfx-supervisor`)

Se o usuário escolher uma opção de **2A a 2E**, carregue imediatamente o `SKILL.md` da respectiva sub-skill. Se escolher **1 (Pipeline Completa)**, siga as etapas abaixo.

---

### Etapa 1: Ideação Anti-Clichê & Refutação (*Devil's Advocate*)

1. **Coleta do Briefing Inicial:** Pergunte sobre a marca/produto, objetivo do vídeo, duração desejada (ex: 15s, 30s, 60s) e referências de universo (ex: *"Mistura de Constantine + The Witcher + Caça-Fantasmas com leveza de Pokémon"*).
2. **Descarte Explícito da 1ª Leva (Regra Paulo.IA):**
   - Liste rapidamente **3 ideias óbvias/clichês** que todo mundo faria para esse tema e **declare-as descartadas**.
   - Proponha **3 caminhos criativos originais** que misturem técnica difícil + forte narrativa humana.
3. **Pesquisa Factual/Histórica (Quando Aplicável):**
   - Se o projeto envolver evolução temporal, personalidades reais ou marcas históricas (como o case *Messi & Yamal*), pesquise dados factuais exatos (altura em cada época, uniforme, patrocinadores, detalhes visuais do ano) antes de avançar.
4. **Portão de Refutação (*Devil's Advocate* — Método Vassão):**
   - Assim que o usuário escolher a ideia favorita, execute **1 rodada (máximo 2)** de crítica construtiva severa:
     > *"Antes de avançarmos para o roteiro, aqui estão os 3 maiores riscos pelos quais essa ideia pode dar errado ou flopar nas redes sociais: [listar]. Como você quer ajustar ou blindar esses pontos?"*
   - *Regra:* Nunca faça mais de 2 rodadas de refutação para não paralisar a produção.

---

### Etapa 2: Roteiro em Duas Colunas (Iteração IA $\rightarrow$ Toque Humano)

1. Gere uma primeira estrutura de roteiro dividida em **duas colunas**:
   | Tempo Estimado | 🗣️ Áudio / Fala / SFX | 🎥 Ação / Cena / Movimento de Câmera |
2. **Portão de Personalização do Roteiro:**
   - Peça ao usuário para revisar e reescrever com suas próprias palavras as falas principais (pois a voz e o texto humano são o coração da originalidade).
   - Confirme se haverá fala sincronizada (*Lip Sync*) ou apenas narração/SFX.

---

### Etapa 3: Fábrica de Assets Isolados ("Os Ingredientes")

Explique ao usuário que **nunca geramos a cena final no escuro**: primeiro construímos e aprovamos cada ingrediente separadamente no mesmo contexto:

1. **Personagens (`character-sheet-studio`):**
   - Acione o fluxo de *Character Sheet* (fotos reais de rosto intactas + corpo gerado).
   - **Perguntas obrigatórias:**
     - Qual a **altura aproximada (em cm)** de cada personagem? (Essencial quando há 2+ personagens na mesma cena).
     - Há **tatuagens complexas (ex: pescoço), óculos específicos ou relógios** que precisam de foto em close-up separada?
     - Vai manter a roupa da foto ou **trocar o figurino** usando uma referência externa?
2. **Produtos (`character-sheet-studio` modo Product Sheet):**
   - Se houver produto físico (ex: lata, embalagem com letras pequenas ou abertura especial), peça fotos de frente, verso e close do rótulo para montar o *Product Sheet*.
3. **Props & Veículos (Regra "GTA-Style" Livre de Direitos):**
   - Liste os objetos de cena (ex: maleta, dispositivo lançador, veículo).
   - Se houver carro ou objeto de marca famosa (ex: *Porsche 911 Rally*), crie o prompt descaracterizando logotipos proprietários (*estilo carro de GTA*) para evitar bloqueios de direitos autorais nos geradores de vídeo, aplicando a identidade visual do projeto.
4. **Cenários / Locações Guiadas por Cor:**
   - Crie os prompts de cada locação limpa usando **as cores e a personalidade do produto/personagem como elemento-chave da direção de arte**, mantendo continuidade de horário e luz entre os cenários (ex: sair de madrugada de um cenário e chegar ao amanhecer no próximo).

---

### Etapa 4: Storyboard Ilustrado no Mesmo Contexto

Antes de gastar créditos de vídeo no Seedance/Kling:
1. **Portão de Personalização do Storyboard:**
   - Pergunte: *"Quer gerar o Storyboard visual agora para aprovar os enquadramentos? Qual estilo de traço/desenho você prefere (ex: sketch P&B, concept art ilustrado, storyboard a lápis)?"*
2. **Regra Anti-Realismo Tosco:**
   - **Nunca** gere storyboard sem especificar traço de ilustração/desenho (prompts de storyboard sem direção de traço geram imagens realistas genéricas que confundem a aprovação).
   - Planeje aproximadamente **1 quadro por segundo de vídeo** (ou 1 quadro por ação chave do roteiro de 2 colunas), vinculando explicitamente quais assets entram em cada quadro.

---

### Etapa 5: Produção de Vídeo, Lip Sync, VFX e Pós-Produção

Com roteiro, assets e storyboard aprovados:
1. **Cenas com Lip Sync e Múltiplos Cenários:** Acione a skill `seedance-commercial-director`.
2. **Cenas com Efeitos Visuais / Transformações / Motion Control:** Acione a skill `cinema-vfx-supervisor` (ou indique **Kling Motion Control** quando uma embalagem/objeto tiver mecânica específica de abertura, como abrir um pacote pelo topo e não como saco de salgadinho).
3. **Estratégia Draft 480p $\rightarrow$ 1080p:**
   - Gere todas as cenas primeiro em **480p Draft**.
   - Oriente o usuário a montar o corte na timeline (DaVinci Resolve, Premiere ou CapCut).
   - Registre cada job de draft via `scripts/session_manager.py add-draft` e lembre do **prazo de 7 dias** para fazer o upscale em 1080p apenas dos takes que entraram na edição final.
4. **Diretriz Final de Áudio:**
   - Todos os vídeos são gerados com **SFX nativo limpo e SEM trilha sonora** (`no background music`), permitindo adicionar trilha licenciada ou produtora de áudio na finalização.
