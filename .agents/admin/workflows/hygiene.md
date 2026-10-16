---
name: Workspace Hygiene Workflow
description: Protocolo de higienização de raiz e classificação automática do @inbox/ pelo Agente Admin.
---

# Workflow de Higienização de Workspace

1. **Varredura da Drop Zone (`@inbox/`):**
   - Inspecionar todos os arquivos presentes em `@inbox/`.
   - Para cada arquivo:
     - Documentos administrativos/financeiros → `@input/admin/` ou subpasta apropriada em `@input/`.
     - Mídias brutas do cliente (fotos, vídeos, áudios) → `@input/midias/` ou `@input/marca/`.
     - Briefings e formulários → `@input/briefing/`.
     - Materiais de pesquisa / benchmarks → `@input/referencias/`.

2. **Varredura da Raiz:**
   - Verificar se há arquivos soltos na raiz (exceto arquivos permitidos de configuração como `.env`, `README.md`, `AI-OPERATING-SYSTEM.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `opencode.json`, `agent-interop.json`).
   - Mover arquivos não identificados para `@quarentena/`.

3. **Validação de Permissões `@`:**
   - Garantir que `.gitignore` contenha as entradas `@*/` e `@*`.

4. **Registro de Log:**
   - Gravar as alterações de movimentação no estado da memória em `.memoria/ChatOff/LATEST_STATE.md`.
