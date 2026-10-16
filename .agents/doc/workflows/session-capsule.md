---
name: Session Capsule Workflow
description: Protocolo de geração de cápsula imutável de sessão e atualização da ponte de memória.
---

# Workflow de Cápsula de Sessão

1. **Construção do Resumo da Sessão:**
   - Coletar arquivos modificados, decisões tomadas, validações executadas e próximas ações.

2. **Geração do Diretório da Cápsula:**
   - Criar diretório `.memoria/ChatOff/YYYY-MM-DD__slug-da-sessao/`.
   - Gerar os arquivos:
     - `summary.md`: Resumo executivo da sessão.
     - `decisions.md`: Lista de decisões arquiteturais e operacionais.
     - `tasklist.md`: Status atualizado de tarefas e próximas pendências.

3. **Atualização da Ponte de Estado:**
   - Gravar o resumo de retomada rápida em `.memoria/ChatOff/LATEST_STATE.md`.
   - Executar atualização do grafo semântico via `python3 .agents/shared/tools/memory_graph.py close`.

4. **Atualização do README.md:**
   - Registrar a sessão na tabela de histórico de evolução em `README.md`.
