# Human Paulo Studio — Sistema Operacional de Agentes

Este documento é a fonte canônica de entrada para qualquer inteligência artificial ou agente conectado ao workspace **Human Paulo Studio**.

## 1. Hierarquia de Decisão
1. Regras de segurança e permissões do CLI em execução.
2. Este documento (`AI-OPERATING-SYSTEM.md`).
3. O estatuto existente em `.agents/AGENTS.md`.
4. O mapa de taxonomia em `.agents/shared/rules/taxonomy.md`.
5. A skill ou workflow selecionado em `.agents/`.
6. O pedido atual do usuário.

As regras de negócio e segurança existentes em `.agents/AGENTS.md` têm precedência sobre instruções operacionais genéricas.

## 2. Interoperabilidade entre IAs (Zero Fricção)
- **Codex CLI e Pi:** carregam `AGENTS.md`.
- **Claude Code:** carrega `CLAUDE.md`.
- **Antigravity CLI / Gemini:** carrega `GEMINI.md`.
- **OpenCode:** carrega `AGENTS.md` via `opencode.json`.
- **Todos os motores** compartilham este mesmo documento, as mesmas regras, os mesmos workflows em `.agents/` e a mesma memória em `.memoria/`.

## 3. Aliases Universais de Sessão

Todos os agentes devem interpretar os aliases abaixo como a mesma intenção operacional, mesmo que a interface em uso não ofereça comandos nativos.

| Intenção | Aliases aceitos | Workflow canônico |
| --- | --- | --- |
| Iniciar ou retomar sessão | `chat-on`, `/chat-on`, `@chaton` | `.agents/workflows/chat-on.md` |
| Encerrar sessão e registrar memória | `chat-off`, `/chat-off`, `@chatoff` | `.agents/workflows/chat-off.md` |

Algumas interfaces reservam `@` para menção de arquivos ou agentes. Quando `@chaton` ou `@chatoff` chegar ao modelo como texto, ele deve ser interpretado pelos aliases acima; se a interface o interceptar, use `chat-on` ou `chat-off`.

<!-- wm-scaffold:shared-methods -->
## 4. Métodos e Skills Compartilhadas

### BMAD — método padrão para construir

Quando o usuário trouxer uma ideia, pedir um sistema, uma funcionalidade, produto ou melhoria, use o BMAD como método padrão. Selecione e leia a skill adequada em `.agents/skills/bmad-*/SKILL.md` para conduzir descoberta, briefing, PRD, arquitetura, UX, épicos, stories, implementação, testes e revisão. Não pule diretamente para código quando uma etapa de definição for necessária.

### Caveman — comunicação econômica obrigatória

Leia `.agents/skills/caveman/SKILL.md`. Em respostas operacionais normais, aplique Caveman no nível padrão `full` para economizar tokens sem perder conteúdo técnico. Siga as exceções da própria skill: use linguagem explícita quando a clareza, uma decisão complexa, um aviso de segurança ou uma confirmação irreversível exigir.

### Security Audit — auditoria autorizada

Para pedidos de auditoria de segurança, revisão de vulnerabilidades ou avaliação de segurança, leia `.agents/skills/security-audit/SKILL.md` e depois seu `SECURITY-AUDIT.md`. Defina o escopo e siga o padrão de evidência. Não acesse rede, credenciais, produção ou sistemas externos sem autorização explícita. Esta skill complementa o BMAD; não é executada automaticamente.

### Headroom — compressão de contexto para dados pesados

Leia `.agents/skills/headroom/SKILL.md`. É proibido carregar arquivos JSON brutos, dumps de API, caches volumosos ou logs maiores que 10KB diretamente na janela de contexto via `view_file` ou `cat`. Sempre utilize a ferramenta do Headroom (`headroom-compress arquivo.json --stats` ou via pipe) para aplicar a compressão SmartCrusher antes de carregar dados volumosos para inspeção ou raciocínio.

## 5. Inicialização de Sessão (`chat-on`)
Ao iniciar qualquer expedição ou receber qualquer alias de início de sessão:
1. Siga `.agents/workflows/chat-on.md`.
2. Execute `python3 tools/session_preflight.py --json` (ou `.agents/shared/tools/session_preflight.py --json`) para resolver cadência, drop zone e redundâncias sem gasto excessivo de tokens.
3. Se existirem arquivos não classificados em `@inbox/`, execute o protocolo do `agent-admin`.
4. Aprofunde apenas as referências necessárias (não carregue o histórico bruto ou governança redundante no contexto).
5. Apresente ao usuário o status da última sessão, pendências e a próxima ação imediata adaptada à cadência do projeto.

## 6. Encerramento de Sessão (`chat-off`)
Ao receber qualquer alias de encerramento de sessão ou encerrar o trabalho:
1. Siga `.agents/workflows/chat-off.md`.
2. Registre entregas validadas, decisões, arquivos modificados e validações.
3. Crie a pasta de sessão `.memoria/ChatOff/YYYY-MM-DD__nome-da-sessao/` com `summary.md`, `decisions.md` e `tasklist.md`.
4. Publique a cápsula e sincronize o grafo com `python3 .agents/shared/tools/memory_graph.py close --file CAMINHO_JSON --expected-revision REV`.
5. Atualize `.memoria/ChatOff/LATEST_STATE.md`.
6. Sincronize com o Git (`git add`, `git commit` semântico e `git push`).
7. **NUNCA** grave credenciais, tokens, senhas ou dados sensíveis na memória ou no Git.

## 7. Taxonomia Sagrada de Pastas (Quatro Diretórios Mestres + Sistema)
Nenhum agente tem autorização para criar diretórios arbitrários na raiz. A taxonomia canônica da WM360 é mantida pelo `agent-admin` (`.agents/shared/rules/taxonomy.md`):

- **SISTEMA (Oculto):**
  - `.agents/`: Motor da IA (personas, skills, workflows, tools, pipelines, regras).
  - `.memoria/`: Estado durável entre sessões, cápsulas e grafo semântico.

- **ENTRADA BRUTA (@input/):**
  - `@inbox/`: Drop zone universal para novos arquivos recebidos do cliente.
  - `@input/`: Dados brutos, briefings, orçamentos, contratos, finanças, mídias brutas e referências (estritamente não-versionado).

- **PROCESSO / ELABORAÇÃO (process/):**
  - `process/`: Inteligência aplicada em elaboração (PRD, arquitetura, estratégia, persona, cronograma).

- **PRODUTO / ENTREGÁVEL (output/):**
  - `output/`: O que foi executado e entregue ao cliente (marca, site, sistema, criativos, copy, conteúdo, campanhas, entregáveis finais).

- **SUPORTE LOCAL (@):**
  - `@scratch/`: Rascunhos e ideias temporárias locais.
  - `@quarentena/`: Arquivos movidos pelo `agent-admin` para análise de segurança ou classificação.
