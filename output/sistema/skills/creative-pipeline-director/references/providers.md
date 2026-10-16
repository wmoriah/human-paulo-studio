# Conexões e modelos

Consultar apenas a rota escolhida. Estes exemplos foram conferidos em 2026-10-14; catálogos e interfaces mudam. A ferramenta/CLI disponível na sessão e sua ajuda atual prevalecem sobre exemplos antigos. Não confundir o modelo de conversa do assistente com o modelo que gera imagens.

## Codex: geração no próprio chat

1. Verificar se há ferramenta nativa de geração de imagem exposta e ler seu esquema/instruções. Estar no Codex não comprova que exista essa ferramenta.
2. Verificar se a ferramenta identifica GPT Image 2.5 ou permite selecioná-lo. Se não houver seletor nem identificação confiável, informar a incerteza antes da escolha final; oferecer hub/API com ID explícito. Não enviar um campo `model` inexistente.
3. Usar somente referências corporais derivadas sem rostos. Se a ferramenta incorporar imagens recentes da conversa automaticamente e não permitir restringi-las, essa chamada não é compatível: usar outra rota. Nunca incluir os retratos no conjunto de imagens enviado.
4. Executar a geração do centro com o prompt da skill; salvar o arquivo retornado para compor localmente. Se a ferramenta exigir outra skill de imagem, seguir suas instruções sem perder o isolamento das fotos faciais.

A API oficial documenta GPT Image 2.5 Sunburst e Flare. O nome da família não comprova a disponibilidade na ferramenta nativa ou na conta. Para qualidade, recomendar Sunburst quando essa variante estiver disponível e nenhuma preferência específica a contradisser. Fonte: https://developers.openai.com/api/docs/guides/images-vision

## Higgsfield CLI — Codex ou Claude Code

Descoberta local: localizar o binário, executar `higgsfield --help`, `higgsfield version` e ajuda dos subcomandos antes de usá-los. Não instalar um pacote apenas pelo nome. Se ausente, consultar o repositório oficial https://github.com/higgsfield-ai/cli e o guia https://higgsfield.ai/creator-hub/help-center/integrations/how-do-i-access-higgsfield-via-cli; escolher instalação oficial compatível com o sistema e respeitar as permissões do ambiente.

Sequência verificada na CLI instalada durante a criação do pacote:

```text
higgsfield account status
higgsfield auth login             # somente se a conexão faltar/expirar
higgsfield account status         # confirma login; não mostrar dados privados desnecessários
higgsfield model list --image
higgsfield model get <ID_VERIFICADO>
higgsfield generate cost <ID_VERIFICADO> <PARAMETROS_VERIFICADOS>
higgsfield generate create <ID_VERIFICADO> <PARAMETROS_VERIFICADOS>
higgsfield generate get <JOB_ID>
higgsfield generate wait <JOB_ID> --timeout 30s --interval 5s
```

Os termos entre <...> são placeholders explicativos, nunca comandos literais. Usar uma lista de argumentos com `subprocess.run([...])`, não interpolar prompts/caminhos em shell. `--prompt` recebe o texto; flags de referência como `--image-references`/`--image` aceitam caminhos locais ou IDs conforme ajuda/modelo. Consultar `generate create --help` e `model get` para formato de listas, proporção e demais parâmetros. Os corpos derivados são os únicos arquivos permitidos nesse envio. A cotação também pode fazer upload: não passar fotos faciais nem originais de corpo com cabeça nessa etapa.

`auth login` abre autenticação oficial pelo navegador; orientar a pessoa a concluir e retornar. Nunca usar `auth token` para diagnosticar conexão (imprime segredo). Catálogo pode ser público: confirmação de conexão requer também operação autenticada. Depois do envio, guardar o ID e consultar o mesmo job em esperas curtas, sem reenviar por timeout. Extrair a URL final do retorno real e baixar conforme as instruções da integração.

Modelos observados em catálogo Higgsfield: Seedream 5.0 Lite (`seedream_v5_lite`), Flash (`seedream_5_0_flash`) e Pro (`seedream_v5_pro`). São exemplos, não garantia de acesso nem aliases intercambiáveis. Consultar GPT Image 2.5 e Nano Banana 2.1 pelo nome exato; não presumir ID.

## Higgsfield MCP

Se as ferramentas já estiverem disponíveis, verificar perfil/conexão, buscar modelos de imagem, ler parâmetros do modelo escolhido, cotar e gerar. No conector verificado, as operações incluem `get_profile`, `models_search`, `models_get`, `estimate_image_cost`, `generate_image`, `jobs_wait`. Prefixos e nomes podem mudar: descobrir a ferramenta real em vez de inventar chamada.

Se faltar conexão, orientar pelo fluxo oficial de conectores/plugins do aplicativo e pela página https://higgsfield.ai/cli. Não presumir endpoint MCP a partir do domínio do site. Após autenticação, recarregar ferramentas se necessário e fazer leitura autenticada. Não usar o preset de character sheet completo/AI Influencer, pois o centro é a única parte generativa.

## Magnific: MCP preferencial; CLI somente se verificada

Rota oficial confirmada: MCP em https://mcp.magnific.com, documentação https://www.magnific.com/ai/docs/magnific-mcp. Abrir o conector no aplicativo e concluir autenticação. Em Claude Code, conferir `claude mcp add --help`; com transporte HTTP suportado, o formato é:

```text
claude mcp add --transport http magnific https://mcp.magnific.com
```

Não sobrescrever um servidor existente chamado `magnific`. Verificar os servidores já configurados. Usar `/mcp` na sessão Claude Code para acompanhar/concluir autenticação quando solicitado. Validar com uma operação autenticada de leitura. Os scopes e disponibilidade são os da versão local; respeitar as configurações existentes. Referência do cliente: https://code.claude.com/docs/en/mcp.

No Codex, preferir adicionar o conector/plugin pelo mecanismo exposto. Se usar CLI de configuração MCP, conferir primeiro a ajuda instalada e a documentação oficial https://developers.openai.com/codex/mcp; não fabricar flags.

Após conexão, descobrir catálogo e operações de geração. No conector verificado, `images_models_list` consulta nomes/slugs e `images_models_settings` traz parâmetros extras quando necessários. Nano Banana 2.1 foi observado como `imagen-nano-banana-2-1`; verificar novamente antes de usar. Selecionar explicitamente o modelo, nunca Auto. Consultar ferramenta de geração/upload/status/download real, suas restrições e custo antes de chamar; usar só referências corporais sem rosto.

Este pacote não presume a existência de uma CLI oficial chamada `magnific`. Se houver uma CLI fornecida pelo usuário/ambiente, verificar origem oficial, `--help`, login, catálogo, geração e exportação. Se não puder verificar, oferecer o MCP confirmado ou API documentada. Não instalar pacotes homônimos desconhecidos, nem usar upscale/retouch do Magnific sobre as fotos faciais ou o board.

## API — alternativa escolhida pelo usuário

1. Confirmar provedor escolhido e abrir sua documentação oficial atual: OpenAI https://developers.openai.com/api/docs/guides/image-generation ; Higgsfield https://open.higgsfield.ai/quick-start ; Magnific https://docs.magnific.com/.
2. Orientar a criação de credencial no painel oficial e armazenamento pelo mecanismo seguro do ambiente/variável de ambiente local. Não pedir para colar segredo no chat, arquivo da skill ou comando registrado. Usar um script local que leia o segredo do ambiente sem imprimi-lo.
3. Conferir catálogo/ID, endpoint, formato de referências, autenticação, custo e resposta. Preparar requisição com SDK oficial ou cliente HTTP e argumentos estruturados. Não derivar endpoint de nomes de modelo.
4. Verificar autenticação de forma não gerativa quando possível. Enviar apenas o centro após escolha e referências prontas, registrar job/request ID e acompanhar/exportar conforme documentação. Acesso à conta do chat não implica acesso à API nem faturamento incluído.

Se a pessoa não tem conexão utilizável, pausar na instrução concreta de login/configuração, mantendo session.json; retomar quando disser “conectei”. Nunca declarar conexão ou geração concluída por ter apenas escrito instruções.
