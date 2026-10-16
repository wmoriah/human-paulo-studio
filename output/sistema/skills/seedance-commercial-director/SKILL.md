---
name: seedance-commercial-director
description: Dirige filmes publicitários e vídeos dinâmicos multi-cenários com Lip Sync real para Seedance 2.5. Mede automaticamente a duração do áudio via ffprobe, transcreve frases/pausas via mlx_whisper, orienta gravação física do áudio, aplica estética IMAX 65mm, força SFX sem música de fundo (no background music) e gerencia o fluxo econômico Draft 480p para 1080p (com controle de prazo de 7 dias e workaround de vídeo-base). Use quando o usuário quiser criar vídeos falados com lip sync, comerciais multi-cenas ou prompts para Seedance 2.5.
---

# Seedance Commercial Director (Vídeo Multi-Cenários & Lip Sync)

Transforme um *Character Sheet* + um arquivo de áudio gravado em um filme publicitário dinâmico no **Seedance 2.5**, onde o personagem caminha e fala por 5 cenários contínuos com cortes rápidos, movimentos físicos de câmera e sincronia labial perfeita.

---

> **Conectores:** esta skill gera imagens/vídeos via hub. Antes de iniciar, confirme se Higgsfield, Magnific ou Google Flow está conectado neste chat. Se não estiver, lembre o usuário de habilitar o conector (passo a passo em `references/providers.md`) ou ofereça o modo manual (apenas prompts).

## Fluxo Conversacional Passo a Passo

### Passo 1: Orientação de Gravação Física & Coleta de Materiais

1. Se o usuário ainda não enviou o áudio ou vai gravá-lo agora, dê imediatamente a **Dica Pro de Atuação Vocal (Paulo.IA)** antes da gravação:
   > *"Para começar, envie o **Character Sheet** do personagem e o **arquivo de áudio** da fala.*
   > 💡 **Dica de Ouro se for gravar o áudio agora:** Grave fazendo a mesma ação física do vídeo! Se o personagem vai caminhar pelos cenários, **grave o áudio andando**; se vai estar sentado, correndo ou deitado, grave nessa condição. A respiração e o peso natural da voz deixam o Lip Sync 10x mais realista!"
2. Assim que receber o arquivo de áudio (`.m4a`, `.mp3`, `.wav`, `.mp4`), inspecione sua duração real exata usando o script local:
   ```bash
   python3 scripts/media_tools.py probe "<caminho_do_audio>"
   ```
   Se houver silêncio morto longo no início ou fim da gravação, ofereça apará-lo com `python3 scripts/media_tools.py trim`.
3. Se a transcrição exata ainda não foi informada, transcreva localmente via `mlx_whisper` (ou `whisper`) para extrair as frases, palavras de destaque e pausas reais com precisão de milissegundos.

---

### Passo 2: Portão de Personalização (Direção Criativa & Orçamento Draft)

Com a duração exata do áudio medida (ex: `10.47s`) e o texto transcrito, apresente a leitura e faça as perguntas de direção:
> **Áudio analisado (`XX.XX segundos`):* *"[Transcrição da fala]"*
>
> **Como você quer personalizar este filme?**
> 1. **Os 5 Cenários Contínuos:** Você já tem 5 ambientes específicos em mente (ou imagens de cenários/assets para anexar) ou quer que eu proponha uma rota espacial contínua coerente com a sua fala?
> 2. **Assets Extras (Opcional):** Vai incluir algum produto na mão, veículo, óculos ou close separado de tatuagem? (E qual a altura do personagem se houver mais alguém em cena?)
> 3. **Estratégia de Renderização (Economia de Créditos):**
>    - **Opção A (Recomendada — Modo Estúdio):** Gerar primeiro em **Seedance 2.5 Draft (480p)** (custa de 1/3 a 1/5 dos créditos e renderiza super rápido). Você aprova ou edita na timeline e tem **7 dias** para dar o OK e converter a mesma *seed* para **1080p Full HD**.
>    - **Opção B (All-In Direto):** Gerar direto 3 opções em **1080p (9:16)**.

---

### Passo 3: Construção do Prompt Mestre para Seedance 2.5

Leia integralmente [references/prompt-template.md](references/prompt-template.md) e construa o prompt em inglês contendo obrigatoriamente os 8 blocos estruturados:

1. `OBJECTIVE AND FORMAT` (Padrão: `9:16 vertical`, duração adaptada exatamente aos segundos do áudio).
2. `REFERENCE AND CHARACTER LOCK` (Interpretando todas as vistas do Character Sheet como uma única pessoa real, sem reproduzir a colagem na tela; incluindo altura e detalhes de tatuagem/óculos).
3. `AUDIO MASTER AND SUPPORTING TRANSCRIPT` (A gravação anexada é a autoridade máxima de ritmo e pronúncia; o diálogo permanece em português sem acelerar a fala).
4. `PHOTOGRAPHY` (Incluir literalmente o bloco *IMAX 65mm photochemical film* com grão natural e início estilo rede social evoluindo para espetáculo cinematográfico).
5. `PERFORMANCE` (Caminhada com peso real, olhar envolvente, piscadas espontâneas e gestos assimétricos motivados pelas palavras).
6. `SPATIAL AND LIGHTING CONTINUITY` (5 cenários conectados por portas, corredores, vidros ou colunas com continuidade de luz do dia e atividade em segundo plano).
7. `PHRASE-BASED SHOT LIST` (~8 planos para um áudio de 10–16s, detalhando *Posição Inicial $\rightarrow$ Trajetória Física $\rightarrow$ Aceleração $\rightarrow$ Enquadramento Final $\rightarrow$ Motivo do Corte* em cada frase: *whip pans*, *dolly-in*, arcos rápidos de 60°–90°, *crane/boom*).
8. `EDITING, SOUND AND FINISH` (**Regra de Ouro de Áudio da Live:** Exigir **SFX nativo realista** de passos e ambiente e proibir expressamente trilha sonora — `STRICTLY NO BACKGROUND MUSIC, SFX AND VOICE ONLY` — para permitir corte e mixagem limpa na pós-produção).

---

### Passo 4: Disparo Conectado, Controle de 7 Dias (Draft) & Segunda Rodada

1. **Se conectado ao Hub (Higgsfield / Magnific):**
   - Suba o **Character Sheet** + **Áudio** + **Assets extras** junto com o prompt.
   - Se o usuário escolheu **Draft 480p**, registre o job imediatamente no gerenciador de sessão para ativar o contador de 7 dias:
     ```bash
     python3 scripts/session_manager.py add-draft --file work/project-session.json --job-id "<JOB_ID>" --scene "<NOME_CENA>"
     ```
2. **Workaround para Plataformas sem Botão Draft$\rightarrow$1080p (ou após 7 dias):**
   - Se o usuário estiver no CapCut, Flora ou Magnific sem vínculo direto de Draft, ou se o prazo de 7 dias tiver expirado, aplique a técnica do Paulo:
   - Suba o **vídeo 480p aprovado como anexo** junto com os mesmos assets e o mesmo prompt, adicionando esta instrução no topo do prompt:
     > `MOTION AND CAMERA REFERENCE LOCK: Use the attached 480p video strictly as the base reference for all camera movements, framing transitions, timing, and character blocking. Render at full 1080p high-definition fidelity.`
3. **Atalho de Pós-Geração ("Versão Mais Dinâmica"):**
   - Após o primeiro resultado, pergunte: *"Curtiu o timing? Quer que eu gere uma segunda variação ainda mais animada, com movimentos de câmera mais agressivos e transições de cenário mais rápidas?"*
