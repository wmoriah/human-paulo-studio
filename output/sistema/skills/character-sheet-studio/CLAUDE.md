# Character Sheet Studio — entrada Claude Code

Leia `SKILL.md` nesta pasta quando o usuário disser “começar”, “iniciar”, “leia a pasta”, “leia as instruções” ou pedir o character sheet. Execute o fluxo; não transforme a solicitação em uma tarefa de programação nem se limite a descrever o pacote. Solicite as fotos que faltam; depois pergunte como gerar os corpos e qual modelo usar. No Claude Code, use uma conexão real por CLI, MCP ou API, guiando o login quando necessário. Não suponha geração nativa de imagens. Retome da etapa pendente após cada resposta.
Se o pedido for instalar como skill, execute a instalação descrita em `SKILL.md`. Para uso pela pasta, instalação é dispensável. Pedidos apenas de auditoria/explicação não iniciam produção. Nunca gere/edite as fotos faciais; somente os corpos são gerados, e a composição final é local.

Versão 2: manter quatro vistas. Remover apenas cenário por máscara separada é permitido; não gerar/retocar o rosto nem modificar RGB original. Seguir references/framing.md: medir a cabeça, fazer close-up por viewport e inspecionar máscaras. Não encaixar as fotografias inteiras nas laterais.
