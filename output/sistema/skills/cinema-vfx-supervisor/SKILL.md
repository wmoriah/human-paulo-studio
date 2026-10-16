---
name: cinema-vfx-supervisor
description: Dirige e produz efeitos visuais de cinema (VFX fotorrealistas) e substituição de personagens (Character Swap / Motion Transfer) sobre vídeos reais. Extrai frames automaticamente via ffmpeg para analisar a cena, apara inícios mortos do vídeo, conduz perguntas de direção de VFX e suporta Seedance 2.5, Minimax, Higgsfield Genjutsu, Kling Motion Control e Google Omni. Use quando o usuário quiser aplicar efeitos especiais em um vídeo real, transformar cenários ou trocar uma pessoa por outro personagem mantendo atuação e voz.
metadata:
  version: "1.0.0"
---

# Cinema VFX Supervisor (Efeitos Visuais & Character Swap em Vídeo Real)

Transforme filmagens reais (mesmo gravadas de celular) adicionando efeitos visuais fotorrealistas (ex: floresta crescendo no estúdio, derretimento, portal, destruição) ou substituindo o ator por um personagem/criatura mantendo 100% da atuação, movimento de câmera e sincronia labial.

---

> **Conectores:** esta skill gera imagens/vídeos via hub. Antes de iniciar, confirme se Higgsfield, Magnific ou Google Flow está conectado neste chat. Se não estiver, lembre o usuário de habilitar o conector (passo a passo em `references/providers.md`) ou ofereça o modo manual (apenas prompts).

## Fluxo Conversacional Passo a Passo

### Passo 1: Orientação de Gravação, Coleta e Inspeção Automática do Vídeo

1. Se o usuário ainda for gravar o vídeo no celular, dê a **Dica Pro de Credibilidade de VFX (Paulo & Mário)**:
   > *"💡 **Dica antes de gravar:** Faça um movimento natural de câmera! Por exemplo: comece falando no quadro, saia rapidamente do enquadramento enquanto a câmera mostra o ambiente onde o efeito vai acontecer e depois volte para o quadro. Esse movimento orgânico faz o efeito parecer 100% real!"*
2. Assim que o usuário anexar ou indicar o caminho do vídeo real:
   - Execute o script local para medir a duração exata e extrair **6 frames ao longo do vídeo** para você enxergar a filmagem de verdade:
     ```bash
     python3 scripts/media_tools.py extract-frames "<caminho_do_video>" --out-dir work/vfx-frames --count 6
     ```
   - Use `view_file` nos 6 frames extraídos (`work/vfx-frames/frame_01.jpg` ... `frame_06.jpg`).
3. **Corte de Início/Fim Morto (`ffmpeg trim` — Dica Live):**
   - Se notar nos frames iniciais que há segundos mortos onde a pessoa ainda está apertando o botão de gravar ou ajeitando o celular (como aconteceu na live), pergunte ou apare automaticamente com:
     ```bash
     python3 scripts/media_tools.py trim "<video_original>" --out work/vfx-frames/video_trimmed.mp4 --start <SEGUNDOS_INICIO>
     ```

---

### Passo 2: Portão de Personalização (Escolha da Modalidade de Efeito)

Após analisar os frames do vídeo, descreva brevemente o que você viu na cena (pessoa, roupa, ambiente, movimento de câmera e duração) e pergunte:

> **Analisei sua filmagem (`XX.Xs`). Qual tipo de transformação você quer criar?**
>
> **Modalidade A — Transformação de Ambiente / Efeito Visual (VFX de Cinema):**
> *(Ex: raízes e plantas tomando conta do estúdio, lava entrando, cenário derretendo, objetos ganhando vida)*
> - Conte do seu jeito: **o que deve acontecer, de onde o efeito surge e em qual momento/ação ele começa?**
>
> **Modalidade B — Substituição de Personagem (Character Swap / Fantasia):**
> *(Trocar você por outro personagem, criatura ou outro figurino mantendo sua voz e movimentos)*
> - Envie a **imagem do personagem alvo** e me diga se prefere:
>   1. **Troca 100% do início ao fim** (via **Higgsfield Genjutsu**, **Kling Motion Control** ou **Google Omni** — não precisa nem de prompt complexo).
>   2. **Transformação no meio da cena** (via **Seedance 2.5**: ex: você começa normal e aos 2 segundos uma névoa/efeito transforma você no personagem mantendo a atuação até o fim).
>
> **Modalidade C — Controle de Movimento de Objeto/Embalagem (`Kling Motion Control`):**
> *(Quando um produto precisa abrir ou se mover de um jeito mecânico específico que a IA erra sozinha — ex: campanha Nescau).*

---

### Passo 3: Direção Técnica e Geração do Prompt Final

#### Se o usuário escolheu Modalidade A (VFX de Ambiente) ou Modalidade B.2 (Transformação no meio do take):
1. Caso falte algum detalhe crítico, faça no máximo **3 perguntas curtas** sobre:
   - A estética do efeito (mágica, assustadora, pós-apocalíptica, épica, sutil).
   - A progressão (rápida ou gradual acompanhando o movimento da câmera).
   - Se a transformação permanece até o último frame.
2. Leia integralmente [references/prompt-template.md](references/prompt-template.md) e entregue o prompt final em inglês estruturado nos **7 blocos obrigatórios**:
   - `1. OBJECTIVE` (Deixar explícito que é uma edição sobre o vídeo anexado).
   - `2. PRESERVATION` (Travar identidade do ator, roupas, voz original sem música adicionada e trajetória exata da câmera).
   - `3. EFFECT ORIGIN AND TRIGGER` (Quadros anteriores ao gatilho permanecem 100% inalterados).
   - `4. TEMPORAL PROGRESSION` (Início, crescimento gradual, auge e estabilização dentro da duração real verificada pelo `ffprobe`).
   - `5. CONTINUITY` (Tudo que foi transformado permanece fixo no espaço 3D mesmo quando a câmera sai e volta para o quadro).
   - `6. PHYSICAL INTEGRATION AND PHOTOREALISM` (Paralaxe, oclusão real atrás das pessoas, sombras de contato, desfoque de movimento e grão idênticos ao vídeo de celular/câmera).
   - `7. SPECIFIC RESTRICTIONS` (Sem deformar rostos, sem efeito atravessando o corpo do ator, sem cortes falsos ou visual de videogame).

#### Se o usuário escolheu Modalidade B.1 (Character Swap Direto — Genjutsu / Motion Control):
- Oriente ou dispare diretamente via conexão ([references/providers.md](references/providers.md)):
  - **No Higgsfield:** Usar ferramenta **Genjutsu** $\rightarrow$ anexar Vídeo Base (aparado) + Imagem do Personagem Alvo $\rightarrow$ Resolução **1080p**.
  - **Fora do Higgsfield (Alternativa econômica ou sem Genjutsu):** Usar **Kling Motion Control (Kling 4.0)** ou **Google Omni**, subindo o vídeo real como referência de movimento/atuação e a imagem do personagem como referência visual.

---

### Passo 4: Recomendação de Motor & Custo-Benefício (Dica Live)

Ao entregar o prompt de VFX ou iniciar a geração conectada, oriente o usuário sobre os dois melhores motores para VFX:
- **Seedance 2.5:** Máxima assertividade na primeira tentativa (*first-try hit*) para transformações graduais complexas com câmera em movimento e preservação de áudio.
- **Minimax (Hailuo):** Excelente alternativa para cenas únicas de efeitos especiais quando o orçamento de créditos estiver curto (custa cerca de 10% a 20% do valor do Seedance).
