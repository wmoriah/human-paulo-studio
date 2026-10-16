---
description: 🟢 CHAT-ON - Retomada adaptativa com pre-flight local e zero desperdício de tokens.
---

# 🟢 CHAT-ON: Protocolo de Retomada do Workspace WM360

Aliases de invocação: `chat-on`, `/chat-on` e `@chaton`. A definição canônica e a compatibilidade entre interfaces estão em `AI-OPERATING-SYSTEM.md`.

Ao iniciar uma nova sessão ou receber qualquer alias de início de sessão:

### 1. Pré-Flight Local (Otimização Máxima de Tokens)
Se existir `tools/session_preflight.py` ou `.agents/shared/tools/session_preflight.py`, execute:
```bash
python3 tools/session_preflight.py --json
```
*(ou `python3 .agents/shared/tools/session_preflight.py --json`)*

O script analisa localmente em 5ms: cadência do projeto, arquivos no `@inbox/`, estado do `LATEST_STATE.md`, densidade do `AGENTS.md` e maturidade do grafo de memória.

- **Diretrizes a seguir com base no pre-flight:**
  - **NÃO** leia `AI-OPERATING-SYSTEM.md` nem `taxonomy.md` (arquivos estáticos de governança).
  - **NÃO** leia `AGENTS.md` se `skip_agents_md` for `true` ou se o arquivo já estiver presente no seu system prompt / regras ativas. Releia apenas se `density` for `high` e o conteúdo não estiver visível no contexto atual.
  - **NÃO** execute `ls -la @inbox/` (o status da drop zone já veio no campo `inbox`). Se houver arquivos (`count > 0`), acione o protocolo de higienização (`.agents/admin/workflows/hygiene.md`).
  - Execute `python3 tools/memory_graph.py resume --max-bytes 12000 --max-nodes 30 --max-capsules 5` **apenas se** `memory_graph.resume_needed` for `true`. Caso contrário, pule.

### 2. Fallback de Segurança (Caso o pre-flight não exista)
Se o script não estiver disponível:
1. Leia `.memoria/ChatOff/LATEST_STATE.md` e verifique `@inbox/`.
2. Releia governança apenas se ela não estiver presente no contexto do seu motor.
3. Se existir `memory_graph.py`, execute o `resume` apenas se o projeto tiver histórico consolidado.

### 3. Apresentação ao Usuário
Apresente um sumário conciso adaptado ao `welcome_mode`:
- **Última sessão:** O que foi entregue e validado.
- **Arquivos na Drop Zone:** Status do `@inbox/`.
- **Pendências:** O que ficou em aberto.
- **Próxima Ação Imediata:** A sugestão de início para a sessão de hoje.
- Se `welcome_mode` for `menu` (projetos esporádicos/novos) ou se o Walter solicitar opções, apresente o Menu do Walter.
- Se `welcome_mode` for `pipeline` (projetos diários como CTM), liste as pipelines disponíveis e foque na próxima ação imediata.

Aguarde o comando ou direcionamento do usuário para iniciar.
