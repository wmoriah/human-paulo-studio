# Retratos grandes e fundo integrado

O padrão é quatro vistas em 8:3: rosto frontal 29%, corpos frente/costas 39%, perfil 32%. A referência visual tem retrato em close-up e corpos sem cabeça; não copiar seu personagem, roupa ou número de vistas. Nunca entregar fotos inteiras com rostos pequenos como se fossem close-ups.

## 1. Inspecionar e anotar as fotografias originais

Abrir cada arquivo com orientação EXIF aplicada apenas para exibição. Identificar cabelo inteiro, topo da cabeça, orelhas, queixo e pescoço. Medir uma caixa `head_box` que englobe cabelo e cabeça até o queixo, em coordenadas normalizadas [esquerda, topo, direita, base], entre 0 e 1. Identificar também `protected_face_box`, uma região interior do rosto com olhos, nariz e boca, sem cenário. A máscara precisa ser opaca em TODO o rosto; a caixa é uma proteção verificável adicional, não uma prova semântica completa. Inspecionar as demais regiões faciais também.

Criar `framing.json` na sessão com os valores medidos em cada imagem. Exemplo de formato, NÃO usar estes números sem medir:

```json
{
  "front": {"head_box": [0.30, 0.15, 0.62, 0.55], "protected_face_box": [0.38, 0.28, 0.55, 0.46]},
  "profile": {"head_box": [0.25, 0.12, 0.60, 0.50], "protected_face_box": [0.35, 0.25, 0.48, 0.40]}
}
```

O compositor dimensiona a cabeça para até 74% da altura, reservando espaço para pescoço e ombros, com 4% de margem superior, limitada a 94% da largura da zona. Se ficar abaixo de 65% da altura, recusa o enquadramento. Fotos são posicionadas atrás de janelas recortadas, nunca salvas cortadas: o HTML guarda cada arquivo inteiro. Esse enquadramento mostra cabeça grande, pescoço e parte dos ombros; braços, cintura e cenários não dominam os retratos. Não distorcer para atingir as medidas.

Se faltar cabelo/queixo na foto, pedir outra. Se for uma vista em três quartos, não chamá-la de perfil nem girar/gerar rosto para corrigi-la. Pedir perfil real ou aceitar só com mudança de requisito explicitamente autorizada.

## 2. Remover cenário por máscara, sem gerar pixels

Remoção de cenário está autorizada no fluxo padrão desta versão. Manter o RGB original e aplicar uma máscara separada: preto oculta cenário, branco preserva sujeito, cinza apenas nas bordas naturais do cabelo/contorno. Não suavizar pele, reiluminar, corrigir cor, trocar roupa, reconstruir orelhas nem descontaminar as cores de borda. A segmentação pode estimar uma máscara; não pode pintar/recriar a pessoa. Todo rosto visível precisa permanecer opaco. Corrigir defeitos editando apenas a máscara.

Rota local incluída: `scripts/prepare_mask.py`, com Rembg/U2Net em modo somente máscara. Dependência opcional: `rembg[cpu]`; verificar a versão de Python suportada na documentação oficial https://github.com/danielgatis/rembg (consultada: Python >=3.11 e <3.14). Preparar um ambiente local compatível. O modelo pode precisar ser baixado no primeiro uso; as fotografias são processadas localmente, sem upload. Não usar backends de nuvem ou generativos dessa biblioteca.

```text
python scripts/prepare_mask.py --image /caminho/frontal.jpg --out /sessao/front-mask.png --protect L T R B
python scripts/prepare_mask.py --image /caminho/perfil.jpg --out /sessao/profile-mask.png --protect L T R B
```

Substituir L T R B pelos valores reais de protected_face_box de cada foto. Inspecionar a máscara e uma prévia sobre cinza: cabelo preservado, nada apagado do rosto/orelhas, sem cenário retangular ou buracos. Se a segmentação falhar, ajustar só a máscara com ferramenta local ou pedir foto adequada. Não retornar à foto inteira silenciosamente.

Também pode fornecer máscaras feitas por outra ferramenta NÃO generativa: PNG monocromático L com o tamanho da foto após orientação EXIF. O compositor rejeita formato/tamanho incorretos, máscaras totalmente brancas e transparência na região facial protegida. Guardar originais e máscaras juntos para reversibilidade. A mudança visual autorizada é a ocultação do cenário; o PNG composto não é idêntico byte a byte à foto de entrada.

## 3. Compor e inspecionar

```text
python scripts/compose.py --front /caminho/frontal.jpg --profile /caminho/perfil.jpg --body /sessao/centro.png --framing /sessao/framing.json --front-mask /sessao/front-mask.png --profile-mask /sessao/profile-mask.png --out /saidas/board-novo
python scripts/compose.py --verify /saidas/board-novo
```

Todos os scripts partem da raiz da skill. `--background cutout` é padrão e exige as duas máscaras. `--background original` só quando a pessoa pedir manter o cenário: ainda exige enquadramento dos rostos. O script não descobre rostos automaticamente; o agente deve medir/inspecionar, sem transferir essa tarefa técnica ao usuário.

Abrir HTML e PNG. Conferir retratos grandes, cabelo e face completos, perfil verdadeiro, sem faixas enormes vazias, sem cenário sobrevivente, máscaras naturais, quatro vistas, corpos inteiros e roupa-alvo correta. Os corpos terminam na gola/base do pescoço, sem toco alto de pele; devem ocupar cerca de 88–94% da altura central. Não aprovar automaticamente apenas porque hashes e dimensões passaram. Se as fotos não tiverem resolução para close-up, avisar e pedir melhores; não fazer upscale generativo.

HTML usa a foto original com máscara CSS de luminância; precisa de navegador com suporte a CSS masks. PNG usa a mesma máscara na composição local. Verificador comprova bytes, máscaras, transformações e recomposição, não qualidade do cabelo nem identificação de rosto. Alterar uma máscara ou enquadramento exige recompor e verificar novamente.
