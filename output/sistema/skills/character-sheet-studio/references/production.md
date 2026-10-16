# Produção e aprovação visual

Resultado: quatro representações em 4800 × 1800 (8:3), fundo cinza #808080, sem títulos, molduras ou divisórias. Retrato frontal grande à esquerda (29%); corpo frente e costas no centro (39%); perfil grande à direita (32%). A escala é definida pela cabeça, nunca pelo tamanho da fotografia inteira.

## Fontes e aparência

As fotografias faciais permanecem arquivos imutáveis. Permitir máscaras separadas para esconder cenário, escala proporcional e posicionamento/crop de visualização. Não gerar, retocar, suavizar, reiluminar, reconstruir ou substituir pixels faciais; não alterar seu RGB nem enviar os retratos a geradores. EXIF só orienta a exibição. O HTML incorpora bytes originais, e as máscaras são recursos separados e reversíveis.

A referência de layout define composição, não identidade/roupa. Não vestir a pessoa com a roupa de outra pessoa na referência. Confirmar roupa-alvo nas referências fornecidas ou na escolha do usuário. Não prometer fidelidade anatômica exata a partir de retratos.

## Execução

1. Registrar os hashes iniciais e inspecionar todas as fontes. Conferir que frontal é frontal e perfil é perfil; uma foto de corpo com rosto distante não é um close-up pronto, mas pode ser enquadrada se tiver resolução suficiente.
2. Seguir [framing.md](framing.md): medir cabeça/face, salvar framing.json e produzir máscaras locais. Preparar prévia dos retratos sobre cinza. Corrigir enquadramento/máscaras antes de gastar com nova geração. Não pedir confirmação extra para ajustes já autorizados.
3. Após escolha de rota/modelo, seguir [providers.md](providers.md) e [body-prompt.md](body-prompt.md). Gerar somente o centro. Referências corporais devem ser cópias sem rosto; fontes originais ficam preservadas. Usar proporção 26:25 ou a mais próxima suportada, mantendo margens. Não gerar o board completo.
4. Inspecionar centro: dois corpos, frente à esquerda e costas à direita, mesma escala/roupa, mãos plausíveis, ombros a pés inteiros. Terminação discreta na gola/base do pescoço, sem cabeça ou toco alto de pele. Corpos ocupam 88–94% da altura. Se corrigir, limitar a duas tentativas, respeitando orçamento; nunca corrigir o board com IA. Se continuar incorreto, comunicar o defeito sem declarar aprovado.
5. Compor com framing.json e máscaras usando o comando de framing.md. O output deve ser novo. Verificar hashes contra os registrados na entrada, executar --verify e inspecionar HTML/PNG. Verificações numéricas não substituem aparência.
6. Entregar HTML, PNG, integrity.json, originals/ e masks/ juntos em ZIP. Registrar separadamente modelo real, referências usadas, inferências, resolução e eventuais limitações. Não chamar três quartos de perfil nem dizer que uma roupa inventada reproduz referência.

## Falta de material

- Sem frontal ou perfil real: pedir foto, nunca gerar a vista. Pode avançar na preparação independente. Não omitir o perfil para imitar uma referência de três vistas: este fluxo exige quatro.
- Sem costas: pedir referência se fidelidade for exigida; inferir detalhes traseiros somente com autorização explícita.
- Sem corpo inteiro: pedir fotos ou autorização para proporções aproximadas. Rosto não determina corpo exato.
- Fotos pequenas, cabelo cortado, rosto desfocado: pedir arquivos melhores quando o close-up não for viável. Não preencher por IA.
- Roupa diferente entre vistas: confirmar roupa-alvo. Não copiar jaqueta/calçados da referência de layout por padrão.
- Segmentação ruim: ajustar máscara, não fotografia. Se não for possível obter contorno aceitável, informar e pedir foto apropriada; não entregar cenário inteiro como fallback sem avisar.

## Integridade

Hashes comprovam igualdade dos arquivos recebidos, não autenticidade anterior. Máscaras ocultam fundo sem reescrever fotografias. PNG inclui composição e reamostragem convencional; não alegar identidade pixel a pixel com o original em resolução diferente. A região facial anotada é verificada como opaca e o RGB vem diretamente da fonte; a identificação correta dessa região e a revisão dos contornos dependem de inspeção visual.
