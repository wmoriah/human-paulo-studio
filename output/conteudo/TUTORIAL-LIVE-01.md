# 🎬 Tutorial Completo: Da Ideia ao Projeto — Criação Visual e Audiovisual com IA
**Fonte:** Live 01 · Human Academy (Mário e Nando Blum) & PAULO.IA (Paulo Aguiar)  
**Vídeo Oficial:** [Assista no YouTube](https://www.youtube.com/watch?v=y62nWkfsoQs) | **Suíte de Skills:** [output/sistema/skills/](../sistema/skills/)

---

## 📌 Parte 1: Mentalidade, Processo Criativo e Ecossistema de Ferramentas

Antes de abrir qualquer gerador, o método apresentado na aula parte de uma premissa central: **a execução técnica está virando commodity; o diferencial real está no controle criativo, repertório e roteiro.**

### 1.1 A Equação do Controle Criativo
$$\text{Resultado} = \frac{(\text{Processo Criativo} + \text{Melhores Ferramentas}) \times \text{Repertório}}{\text{Controle}}$$
- **Sem Briefing (Livre):** É fácil gerar uma imagem ou vídeo bonito dizendo *"crie um trailer cinematográfico"*. Porém, você não tem controle.
- **Com Briefing / Cliente:** Quanto mais específico for o que você precisa manter (roupa, embalagem de produto, atuação, continuidade de cenário), **mais etapas intermediárias e assets separados** você precisa construir.

### 1.2 O Fluxo "Alternado" (Humano ↔ IA) em Uma Única Conversa
Para projetos completos (como o case comercial da **Fanta Halloween** ou o hyperlapse **Messi & Yamal**), nunca jogue tudo num único comando esperando o vídeo pronto. Siga este pipeline **dentro de um único chat/projeto** (ChatGPT, Claude ou Antigravity) para preservar 100% do contexto:

1. **Validação e Descarte de Ideias Óbvias:**
   - Peça ideias iniciais para a IA sobre o tema. **Descarte as primeiras sugestões** — são exatamente as ideias clichês que todo mundo vai fazer.
   - **Técnica de Refutação (Devil's Advocate):** Apresente a sua ideia para a IA e pergunte: *"Tive essa ideia. Por que ela pode dar errado? Por que ela floparia nas redes sociais?"* Use as críticas para blindar o conceito (faça isso 1 a 2 vezes para refinar sem travar o projeto).
2. **Roteiro (Iteração Medíocre → Roteiro Humano):**
   - Peça para a IA gerar vários rascunhos de roteiro para destravar caminhos e estruturas, mas **reescreva/finalize o roteiro você mesmo** (formato de 2 colunas: *Áudio/Fala* vs. *Ação/Vídeo*).
3. **Criação de Assets (Os "Ingredientes" da Cena):**
   - Hoje não se gera mais uma imagem inteira pronta para só depois animar tudo no escuro. Você gera **os assets isolados** (Personagem/Character Sheet, Produto/Product Sheet, Objetos/Props, Veículo, e Cenários limpos inspirados na paleta do produto).
4. **Storyboard no Mesmo Chat:**
   - Com o roteiro aprovado e a pasta de assets definida na mesma conversa, peça ao LLM (ex: ChatGPT) para gerar os quadros do storyboard (ex: 60 quadros para 1 minuto de vídeo).
   - **Dica de Ouro para Storyboard:** Sempre anexe uma referência de **traço de desenho/ilustração** para o storyboard. Se você não direcionar o estilo para desenho, a IA tentará fazer imagens realistas genéricas que distorcem a aprovação com o cliente.

### 1.3 Stack de Ferramentas: Modelos vs. Hubs (Marketplaces)
Não confunda **Hub (Agregador)** com **Modelo (Motor de IA)**:

| Categoria | Ferramentas Citadas na Aula | Função Principal |
| :--- | :--- | :--- |
| **Orquestradores / Agentes** | **ChatGPT (Work / Codex)**, **Claude (Claude Code)**, **Google Antigravity** | Cérebro do projeto: analisa imagens/vídeos, roda *Skills*, escreve prompts técnicos e se conecta via MCP/Plugins aos Hubs. |
| **Hubs (Marketplaces)** | **Higgsfield**, **Magnific (Freepik)**, **Flora**, **Google Flow**, **CapCut (Mobile)** | "Lojas" onde você acessa vários modelos num só lugar e pode conectá-los diretamente dentro do ChatGPT/Antigravity. |
| **Modelos de Imagem** | **Nano Banana 2.1**, **Seedream 5 Pro**, **ChatGPT Nativo** | Consistência extrema de personagem, edição de ângulos e criação de assets. |
| **Modelos de Vídeo** | **Seedance 2.0 / 2.5**, **Kling 4.0 (e O1)**, **Google Omni**, **Minimax (Hailuo)** | Geração de vídeo multi-cenas com áudio/lip sync (Seedance), transições (Kling 4.0) e custo-benefício (Minimax). |
| **Substituição / Movimento** | **Higgsfield Genjutsu**, **Kling Motion Control**, **Google Omni** | Troca de personagens em vídeos reais e transferência de atuação/movimento. |

> [!TIP]
> **Conectando o Hub dentro do Chat (Fim do "Office Boy de Prompt"):**
> Em vez de copiar e colar 20 prompts manualmente entre janelas, digite no ChatGPT Work/Codex ou Antigravity: `"Vamos conectar o Higgsfield"` (ou `"Quero conectar o Magnific"`), autorize o login e peça: *"Gere todas as opções em paralelo lá usando o modelo X"*.

---

## 📸 Parte 2: Passo a Passo dos 5 Tutoriais Práticos da Live

Abaixo estão os 5 fluxos executados ao vivo durante a transmissão, com todas as regras práticas e segredos de execução.

---

### Tutorial 1: Variação de Ângulos Inusitados a partir de 1 Foto
**Objetivo:** Transformar uma única foto comum (mesmo tirada de celular) em múltiplos enquadramentos radicais no mesmo ambiente, mantendo roupa, sapato, luz e estética originais.

#### Passo a Passo:
1. **Capture ou selecione a foto base:** Pode ser uma foto simples de celular da pessoa no ambiente real.
2. **Gere os Prompts de Câmera no LLM:**
   - Abra um novo chat no ChatGPT/Claude/Antigravity.
   - Anexe a foto original e use a skill [experimental-angles-studio](../sistema/skills/experimental-angles-studio/SKILL.md) (ou o template em [prompt-template.md](../sistema/skills/experimental-angles-studio/references/prompt-template.md)).
   - O agente atuará como um diretor de fotografia experimental e devolverá **5 prompts em inglês** com posições físicas extremas (ex: câmera no chão entre os pés, câmera no teto em zenital, câmera escondida atrás de um objeto em primeiro plano).
3. **Gere as Imagens no Modelo de Consistência:**
   - Abra seu Hub (Higgsfield, Flow ou Magnific) ou peça geração direta via integração.
   - Selecione o modelo **Nano Banana 2.1** (resolução **2K**, qualidade **High**) ou **Seedream 5 Pro**.
   - **Importante:** Em cada geração, suba **a foto original como imagem de referência** junto com o respectivo prompt em inglês gerado no passo anterior.
4. **Iteração Livre Sob Demanda:**
   - Como o contexto técnico já está carregado no chat, basta pedir variações curtas em linguagem natural:
     - *"Agora me dê um ângulo Fisheye bem distorcido de baixo para cima."*
     - *"Faça um ângulo onde ele segura a câmera com a mão bem perto da lente (estilo selfie grande-angular)."*

> [!IMPORTANT]
> **Por que funciona tão bem?** O prompt proíbe o modelo de "embelezar" ou mudar a iluminação para algo artificialmente cinematográfico; ele exige **duas evidências visuais concretas** de que a câmera mudou de lugar no espaço físico real.

---

### Tutorial 2: Criando um Character Sheet Perfeito (Sem Perder Identidade)
**Objetivo:** Criar a folha de referência definitiva de um personagem real (ou produto) para usar em ensaios fotográficos e vídeos sem distorcer o rosto.

#### As Regras de Ouro do Character Sheet (Dicas Pro):
- **NUNCA coloque a cabeça gerada por IA junto ao corpo ou dezenas de poses na mesma folha:** Character sheets poluídos com 20 poses diminuem a resolução útil de cada rosto e fazem a IA misturar traços, destruindo a semelhança facial. **Menos é mais.**
- **Preserve a foto real no rosto:** A melhor técnica mantém os recortes reais das fotos do rosto (frente e perfis) no topo e gera apenas o corpo padronizado abaixo.
- **Tatuagens, Óculos e Detalhes Específicos:** Se a pessoa tem tatuagens complexas (ex: no pescoço) ou usa um óculos/relógio específico, tire fotos em close desses itens e suba-os separadamente quando a cena exigir fidelidade máxima.
- **Altura do Personagem:** Se o vídeo terá mais de uma pessoa (ex: casal ou dupla), especifique a altura em centímetros tanto no Character Sheet quanto no prompt para a IA não criar desproporções.

#### Passo a Passo com a Skill `character-sheet-studio`:
1. **Tire 3 a 4 fotos rápidas com o celular:**
   - 1 foto de rosto de frente.
   - 1 ou 2 fotos de rosto de perfil (esquerdo/direito).
   - 1 foto de corpo inteiro de frente (para referência da roupa/caimento). *(A foto de costas é opcional se a roupa for lisa).*
2. **Ative a Skill no Agente:**
   - Não precisa descompactar o arquivo! Arraste o arquivo [character-sheet-studio.zip](../entregaveis/character-sheet-studio.zip) (ou aponte para a pasta [character-sheet-studio](../sistema/skills/character-sheet-studio/)) direto no chat do Codex/Claude/Antigravity e digite: `"Quero usar essa skill"`.
3. **Envie as Fotos (e Mudanças de Look, se quiser):**
   - Suba as fotos tiradas.
   - *Dica:* Se quiser trocar a roupa real por outra (ex: um look do Pinterest, camisa de time ou tênis específico), basta anexar a foto da peça e dizer: *"Use o rosto das minhas fotos, mas vista o corpo com esta jaqueta e este tênis"*.
4. **Consolidação da Prancha:**
   - A skill gera os corpos limpos e monta automaticamente a prancha final combinando os rostos reais de alta definição com o corpo consistente.
   - **Adaptação para Produtos (Product Sheet):** Você pode pedir ao agente: *"Adapte esta skill de Character Sheet para criar um Product Sheet"* e enviar frente, verso, lateral e detalhe de rótulo da embalagem.

---

### Tutorial 3: Ensaio Fotográfico Editorial com Referências Estéticas
**Objetivo:** Gerar um ensaio fotográfico autoral completo (10 a 20 fotos) mantendo 100% da pessoa e do figurino do Character Sheet, mas absorvendo a iluminação, textura e direção de arte de referências do Pinterest/Savee.it.

#### Passo a Passo:
1. **Separe os Materiais:**
   - **Imagem 1 (Identidade e Figurino):** O seu **Character Sheet** gerado no Tutorial 2.
   - **Imagens 2 a 6 (Referências Estéticas):** Escolha de 3 a 5 fotos incríveis no Pinterest ou Savee.it que tenham a iluminação, cor, granulação e atmosfera que você deseja.
2. **Rode o Prompt de Direção de Ensaio:**
   - Em um novo chat, suba o Character Sheet + as Referências Estéticas e use a skill [editorial-photoshoot-studio](../sistema/skills/editorial-photoshoot-studio/SKILL.md) (ou o template em [prompt-template.md](../sistema/skills/editorial-photoshoot-studio/references/prompt-template.md)).
   - **Regra Crítica:** O prompt instrui a IA a **não copiar a composição exata** da referência e **não transferir traços físicos do modelo da referência** para você. Ele extrai a *linguagem fotográfica* (luz lateral, fundo quente, espaço negativo, grão de filme) e cria poses inéditas.
3. **Geração em Volume e Paralelo:**
   - Com o Higgsfield ou Magnific conectado ao chat, peça:
     > *"Agora vá no Higgsfield e gere 20 imagens do personagem inspiradas nessas referências usando o Nano Banana 2.1 (ou Seedream 5 Pro). Gere tudo em paralelo."*
   - **Por que gerar em volume (15 a 20 fotos)?** Imagem estática consome pouquíssimo crédito (muitas vezes é gratuita em planos mensais) e permite fazer curadoria manual, descartando rapidamente qualquer imagem com micro-erros (ex: sapato sem meia) e selecionando as obras-primas.

---

### Tutorial 4: Vídeo Comercial Multi-Cenários com Lip Sync Real (Seedance 2.0 / 2.5)
**Objetivo:** Criar um vídeo dinâmico (estilo comercial/Reels de alta retenção) onde o seu personagem caminha e fala por 5 cenários diferentes com cortes rápidos, movimentos de câmera de cinema e sincronia labial perfeita a partir de um áudio real seu.

#### Passo a Passo:
1. **Grave o Áudio Guia (O Segredo do Realismo):**
   - Grave a fala no celular mesmo (10 a 15 segundos).
   - **Dica Pro de Atuação Vocal:** Grave o áudio fazendo a ação física do vídeo! Se no vídeo o personagem estará caminhando, **grave o áudio andando**. Se estiver correndo ou deitado, grave nessa condição. A respiração e a cadência natural da voz mudam completamente o realismo do lip sync.
2. **Suba os Assets + Prompt de Direção no Agente:**
   - Em um novo chat, anexe:
     1. O **Character Sheet** do personagem.
     2. O **arquivo de áudio** gravado (`.m4a`, `.mp3` ou `.wav`).
     3. *(Opcional)* Fotos de cenários ou objetos específicos se quiser forçar locais exatos.
   - Use a skill [seedance-commercial-director](../sistema/skills/seedance-commercial-director/SKILL.md) (ou o template em [prompt-template.md](../sistema/skills/seedance-commercial-director/references/prompt-template.md)).
3. **O que o Agente Faz Automaticamente:**
   - Mede a duração exata do áudio (ex: `10.47s`), transcreve cada frase e pausa, e monta uma **Shot List baseada nas frases** dividida em 5 cenários contínuos, com movimentos físicos de câmera (*whip pans*, *dolly-in*, arcos de 60°–90°) e estética de película IMAX 65mm.
4. **Estratégia Profissional de Renderização: Fluxo Draft (480p) → Upscale (1080p):**
   - Gerar vídeo multi-cenas direto em 1080p no Seedance é caro. Em projetos reais, siga o fluxo **Draft**:
     1. Peça para gerar primeiro em **Seedance Draft (480p)** (custa de 1/3 a 1/5 dos créditos e renderiza muito mais rápido).
     2. Monte a edição prévia no DaVinci Resolve / Premiere / CapCut com os arquivos em 480p e aprove com o cliente.
     3. **Atenção ao Prazo:** Você tem **7 dias** para dar o "OK" nos takes aprovados e pedir ao Seedance para converter exatamente a mesma geração (mesma *seed*) para **1080p Full HD**.
     4. *Workaround caso sua plataforma não tenha botão de Draft→1080p ou passem os 7 dias:* Suba o vídeo 480p aprovado como anexo junto com os mesmos assets e o mesmo prompt, adicionando no início: *"Utilize este vídeo em anexo como base para todos os movimentos e controle de câmera"*.
5. **Dica Pro de Sonoplastia (Sound Design):**
   - O Seedance já gera excelentes efeitos sonoros ambientes (passos, vento, ambiência). **Sempre peça no prompt para gerar SEM música/trilha sonora** (`no background music`). Se ele gerar música junto, cada corte terá uma música diferente e você não conseguirá aproveitar os efeitos sonoros (SFX) na edição final.

---

### Tutorial 5: Efeitos Visuais (VFX) e Substituição de Personagens em Vídeos Reais
**Objetivo:** Pegar um vídeo gravado na hora com o celular e (A) substituir a pessoa por uma criatura/personagem mantendo a atuação e a voz, ou (B) transformar o ambiente real gradualmente com efeitos dignos de cinema (ex: uma floresta crescendo no estúdio).

#### Modalidade A: Substituição Direta de Personagem (Character Swap)
Existem dois caminhos principais mostrados na aula:

- **Caminho 1 — Rápido (Higgsfield Genjutsu / Kling Motion Control / Google Omni):**
  1. Grave um vídeo falando e gesticulando normalmente.
  2. Tenha uma imagem do personagem/fantasia alvo (ex: um homem-pantera negra de terno).
  3. No chat conectado ao Higgsfield, acione o **Genjutsu**, suba o vídeo original + a imagem do personagem e peça a geração em 1080p (não precisa de prompt complexo).
  4. *Alternativa fora do Higgsfield:* Use o **Kling Motion Control** ou o **Google Omni** (subindo o vídeo base para transferir o movimento exato e o áudio para o novo personagem).

- **Caminho 2 — Transformação no Meio do Vídeo via Seedance (Sem Genjutsu):**
  1. Use a skill [cinema-vfx-supervisor](../sistema/skills/cinema-vfx-supervisor/SKILL.md) (ou o template em [prompt-template.md](../sistema/skills/cinema-vfx-supervisor/references/prompt-template.md)).
  2. Anexe o vídeo original + a imagem do personagem alvo.
  3. Descreva o efeito: *"A partir dos 2 segundos de vídeo, faça uma transformação com névoa escura de Halloween que transforme a pessoa do vídeo neste personagem da imagem (onça preta de terno), mantendo o personagem transformado até o final com todos os movimentos e sincronia labial idênticos."*

#### Modalidade B: Transformação de Cenário em Vídeo Real (VFX de Ambiente)
1. **Grave o Vídeo Base com Movimento Natural:**
   - Grave o ambiente e o personagem com um movimento de câmera orgânico (ex: a pessoa aponta para a sala, sai rapidamente do quadro enquanto a câmera mostra o ambiente e volta para o quadro). Movimentos naturais de câmera de mão aumentam drasticamente a credibilidade do VFX.
2. **Aplique o Prompt de Supervisor de VFX:**
   - Em um novo chat, use a skill [cinema-vfx-supervisor](../sistema/skills/cinema-vfx-supervisor/SKILL.md) e anexe o vídeo gravado.
   - Quando o agente perguntar qual efeito você deseja, responda em linguagem simples:
     > *"Quero que comecem a crescer raízes, trepadeiras e folhas pelo chão e paredes, transformando o estúdio inteiro em uma floresta densa. Isso deve acontecer gradualmente acompanhando o movimento da câmera, mantendo total consistência do personagem e da iluminação original."*
3. **Renderize com o Vídeo Original como Referência:**
   - Envie o prompt técnico gerado em inglês junto com o vídeo original para o **Seedance 2.5** (ou **Minimax**, excelente alternativa de baixo custo para VFX).
   - O prompt garante **oclusão física, sombras de contato, paralaxe e continuidade** (as plantas que cresceram permanecem no mesmo lugar quando a câmera volta).

---

## 🛠️ Resumo Rápido: Como Criar Suas Próprias Skills
Durante a live, foi ensinado como transformar qualquer prompt longo que você usa repetidamente em uma **Skill** reutilizável (no Claude Code, Codex ou Antigravity):
1. Pegue um prompt estruturado que já funciona bem (como os 4 arquivos `.md` desta pasta).
2. Abra seu agente e peça:
   > *"Quero transformar este prompt em uma Skill instalável. Configure para que, antes de gerar o resultado final, a Skill faça perguntas objetivas ao usuário caso falte alguma informação ou anexo."*
3. Salve a pasta/zip da Skill e acione-a sempre com `/` ou arrastando para o chat.
