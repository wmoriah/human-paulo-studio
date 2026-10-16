---
name: experimental-angles-studio
description: Gera 5+ variações de ângulos de câmera inusitados, radicais e fisicamente plausíveis a partir de uma única foto real, mantendo 100% da identidade, roupa, calçado, iluminação e estética original (inclusive estética de celular). Inclui conversão automática de arquivos .HEIC/.WEBP e menu de ângulos extras sob demanda (Fisheye, Selfie mão na lente, etc.). Use quando o usuário quiser criar novos ângulos de uma mesma foto ou cena.
metadata:
  version: "1.0.0"
---

# Experimental Angles Studio (Variação de Ângulos Inusitados)

Transforme uma única fotografia em múltiplos enquadramentos surpreendentes no mesmo espaço físico, preservando a estética original da foto (mesmo quando tirada de celular) e enviando para geração em **Nano Banana 2.1 (2K High)** ou **Seedream 5 Pro**.

---

> **Conectores:** esta skill gera imagens/vídeos via hub. Antes de iniciar, confirme se Higgsfield, Magnific ou Google Flow está conectado neste chat. Se não estiver, lembre o usuário de habilitar o conector (passo a passo em `references/providers.md`) ou ofereça o modo manual (apenas prompts).

## Fluxo Conversacional Passo a Passo

### Passo 1: Receber e Preparar a Imagem Base (Auto-Conversão `.HEIC`)

1. Se o usuário ainda não anexou a foto, peça:
   > *"Envie a foto que você quer usar como base para criarmos os novos ângulos de câmera."*
2. **Regra de Compatibilidade iPhone (`.HEIC` / `.WEBP`):**
   - Fotos enviadas direto do iPhone em `.HEIC` falham ao subir no Higgsfield e outros hubs.
   - Sempre verifique a extensão do arquivo recebido. Se for `.heic`, `.heif`, `.tif` ou `.webp`, converta imediatamente usando o script local antes de qualquer envio:
     ```bash
     python3 scripts/media_tools.py convert-image "<caminho_da_foto>" --out-dir work/angles-input --ext jpg
     ```
3. Inspecione visualmente a foto (`view_file`) para mapear:
   - Roupa exata, calçado (ex: tênis/sapato e meias), acessórios (óculos, relógio), tatuagens visíveis e pose.
   - Mobiliário, paredes, chão e objetos reais do ambiente (que servirão de primeiro plano ou oclusão parcial).
   - Estética da câmera original (se é foto crua de celular ou câmera profissional).

---

### Passo 2: Portão de Personalização (Antes de Gerar)

Faça uma pergunta rápida e direta ao usuário:
> **Como você prefere dirigir esses ângulos?**
> 1. **Pacote Surpresa de 5 Ângulos Radicais:** Eu escolho as 5 melhores posições físicas extremas para o seu ambiente (rente ao chão entre os pés, zenital no teto, escondida atrás de um objeto, grande-angular de escala extrema, etc.).
> 2. **Escolher Ângulos Específicos:** Me diga quais você quer (ex: *Fisheye bem distorcida de baixo*, *Selfie segurando a câmera com a mãozona perto da lente*, *Over-the-shoulder*, etc.).
> 3. **Onde vamos gerar as imagens?** Você quer apenas os prompts em inglês para colar no seu Hub (Google Flow / Higgsfield / Magnific) ou quer que eu já dispare a geração conectada agora (recomendado: **Nano Banana 2.1 em 2K High** ou **Seedream 5 Pro**, 2 opções por prompt)?

---

### Passo 3: Construir os Prompts Técnicos em Inglês

Leia integralmente as diretrizes em [references/prompt-template.md](references/prompt-template.md) e siga estas regras obrigatórias ao redigir cada prompt em inglês:

1. **Posição Física Concreta:** Comece especificando altura exata da câmera, distância, direção, inclinação e distância focal (ex: `14mm ultra-wide lens`).
2. **Duas Evidências Visuais de Mudança de Lugar:** Descreva o que fica gigante no primeiro plano (ex: sola/bico do sapato, quina da mesa), o que fica distante, o que encobre parcialmente a pessoa e quais superfícies novas aparecem (teto, parte de baixo do móvel).
3. **Preservação Estrita da Estética Original (Dica Live):**
   - Mantenha a estética de captura original (se a foto base for de celular em luz de sala/estúdio, **proíba** o modelo de aplicar iluminação cinematográfica dramática falsa ou mudar a cor do ambiente).
   - Preserve 100% da roupa, sapato exato, meia, barba, cabelo, óculos e tatuagens.
   - **Não obrigue a pessoa a olhar para a nova câmera** — ela mantém a ação/olhar original enquanto a câmera se move ao redor dela.

Entregue cada um dos 5 prompts no formato:
- **Título curto em português**
- **1 frase explicando onde a câmera foi colocada**
- **Bloco de código em inglês pronto para copiar** (instruindo a anexar sempre a foto original como referência).

---

### Passo 4: Disparo Conectado (Opcional) & Menu de Pós-Ângulos Rápidos

1. Se o usuário optou por gerar via conexão (Higgsfield / Magnific / Nativo), consulte [references/providers.md](references/providers.md), anexe **sempre a foto original convertida em `.jpg`** como referência de imagem e gere **2 variações por prompt** em paralelo usando **Nano Banana 2.1 (2K, High)** ou **Seedream 5 Pro**.
2. **Menu de Pós-Ângulos Sob Demanda (Dica Live):**
   Logo após entregar os 5 primeiros ângulos, ofereça proativamente os atalhos que mais funcionaram ao vivo:
   > *"Quer testar mais algum ponto de vista rápido? Posso gerar agora:*
   > - **A) Lente Fisheye (Olho de Peixe):** Bem distorcida vista de baixo para cima.
   > - **B) Selfie Mão na Lente:** Personagem segurando/alcançando a câmera com a mãozona gigante perto da lente (estilo foto de perfil).
   > - **C) Câmera de Segurança (CCTV Alta):** No canto superior do teto olhando toda a sala.
   > - **D) Outro ângulo específico que você imaginar.**"
