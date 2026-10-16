---
name: editorial-photoshoot-studio
description: Dirige e produz um ensaio fotográfico editorial completo (10 a 20 retratos autorais) combinando um Character Sheet (fonte exclusiva de identidade e figurino) com múltiplas referências estéticas do Pinterest/Savee.it (fonte exclusiva de luz, cor, textura e atmosfera). Inclui disparo em volume e paralelo em Nano Banana 2.1 e Seedream 5 Pro e checklist de revisão de detalhes (tatuagens, óculos, meias/sapatos). Use quando o usuário quiser criar um ensaio fotográfico profissional ou fotos editoriais com IA.
metadata:
  version: "1.0.0"
---

# Editorial Photoshoot Studio (Ensaio Fotográfico Editorial)

Conduza a direção de arte e fotografia de um ensaio profissional completo a partir do *Character Sheet* da pessoa e de suas referências visuais favoritas, garantindo que cada foto pareça um clique autoral inédito (nunca uma colagem ou cópia literal da referência).

---

> **Conectores:** esta skill gera imagens/vídeos via hub. Antes de iniciar, confirme se Higgsfield, Magnific ou Google Flow está conectado neste chat. Se não estiver, lembre o usuário de habilitar o conector (passo a passo em `references/providers.md`) ou ofereça o modo manual (apenas prompts).

## Fluxo Conversacional Passo a Passo

### Passo 1: Coleta e Identificação dos Materiais

1. Peça os materiais caso ainda não tenham sido enviados:
   > *"Para começarmos o seu Ensaio Fotográfico Editorial, envie:*
   > 1. **O seu Character Sheet** (se ainda não tiver um, posso acionar a skill `character-sheet-studio` agora para criarmos em 2 minutos).
   > 2. **De 3 a 5 imagens de referência estética** (fotos do Pinterest, Savee.it, etc. cuja iluminação, cor e atmosfera você ama)."
2. Se alguma imagem estiver em `.HEIC`/`.WEBP`, converta automaticamente com:
   ```bash
   python3 scripts/media_tools.py convert-image "<arquivo>" --out-dir work/photoshoot-refs --ext jpg
   ```
3. Inspecione todas as imagens (`view_file`) e confirme explicitamente qual arquivo é o **Character Sheet** e quais são as **Referências Estéticas**.

---

### Passo 2: Portão de Personalização do Ensaio

Antes de escrever os prompts ou disparar gerações, pergunte de forma concisa:
> **Vamos alinhar a direção do seu ensaio:**
> 1. **Figurino:** Mantemos exatamente a roupa do Character Sheet em toda a série ou você quer testar algum figurino diferente?
> 2. **Detalhes Críticos:** Há algum detalhe que exige atenção redobrada na revisão (ex: tatuagem específica no pescoço/braço, modelo dos óculos, relógio, sapato/meia)?
> 3. **Volume e Formato:** O padrão é **10 prompts** em formato vertical **4:5 (2K)**. Quando formos gerar no Hub (Higgsfield / Magnific / Flow), quer gerar **20 imagens em paralelo** dividindo entre **Nano Banana 2.1** e **Seedream 5 Pro** para fazermos curadoria das melhores?

---

### Passo 3: Planejamento da Série & Escrita dos Prompts Independentes

Leia integralmente [references/prompt-template.md](references/prompt-template.md) e entregue na ordem exata:

1. **Leitura Breve do Character Sheet + Referências:**
   - Liste as características físicas imutáveis da pessoa (rosto, barba/cabelo, óculos, tatuagens com lado e desenho exatos, roupa e calçado).
   - Liste o que cada referência estética empresta ao ensaio (luz lateral, fundo quente, preto e branco de alto contraste, espaço negativo, grão 35mm).
2. **Tabela de Planejamento da Série:**
   | Nº | Nome do Retrato | Referência Utilizada | Enquadramento | Luz e Atmosfera | Proposta Original (Pose/Cenário) |
   - Varie intencionalmente entre *Close, Busto, Meio Corpo e Corpo Inteiro*; *Frontal, 3/4 e Perfil*; *Em pé e Sentado*; *Olhar direto e fora da câmera*.
3. **Prompts Completos e Independentes em Inglês:**
   - Antes de cada bloco de código, indique exatamente quais arquivos anexar:
     - `Image 1: Character Sheet (Identity & Wardrobe Lock)`
     - `Image 2: Aesthetic Reference #X (Lighting, Color & Texture Only)`
   - **Proibição Absoluta:** Nunca escreva *"recreate this photo"* ou *"replace the model"*. Crie uma nova combinação de pose, gesto e cenário inspirada na estética da referência.
   - **Pele e Textura Real:** Exija textura de pele natural com poros e granulação orgânica de filme, proibindo pele plastificada ou aparência de render 3D.

---

### Passo 4: Disparo de Volume em Paralelo & Curadoria (Dica Live)

1. Se o usuário autorizar a geração conectada (via Higgsfield ou Magnific MCP/CLI, conforme [references/providers.md](references/providers.md)):
   - **Dispare tudo em paralelo** (não gere de 4 em 4 sequencialmente).
   - Gere **2 opções por prompt** no **Nano Banana 2.1 (2K, 4:5)** e ofereça rodar uma leva comparativa no **Seedream 5 Pro**.
2. **Checklist de Curadoria Pós-Geração:**
   - Ao entregar ou revisar as imagens geradas, confira especificamente os pontos onde a IA costuma escorregar em volume:
     - Símbolos e posição das tatuagens (ex: Kitsune no pescoço).
     - Olhos legíveis atrás das lentes dos óculos.
     - Anatomia das mãos e detalhes de calçado (ex: verificar se não gerou sapato social sem meia quando deveria ter meia).
