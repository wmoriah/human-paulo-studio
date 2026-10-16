---
description: 🔴 CHAT-OFF - Encerra a sessão, cria a Cápsula do Tempo em .memoria/ e sincroniza o repositório Git.
---

# 🔴 CHAT-OFF: O Protocolo da Cápsula do Tempo WM360

Aliases de invocação: `chat-off`, `/chat-off` e `@chatoff`. A definição canônica e a compatibilidade entre interfaces estão em `AI-OPERATING-SYSTEM.md`.

Ao receber qualquer alias de encerramento de sessão ou encerrar o trabalho:

1. **Revisão da Sessão:** Faça um balanço das conquistas, entregas validadas, arquivos modificados e testes realizados.
2. **Criação da Pasta de Sessão:**
   - Crie a pasta `.memoria/ChatOff/YYYY-MM-DD__<nome-da-sessao>/` contendo:
     - `summary.md`: Data, Contexto, O que foi feito, Arquivos modificados e Status.
     - `decisions.md`: Lista das decisões tomadas.
     - `tasklist.md`: Tarefas finalizadas `[x]` e pendentes `[ ]`.
3. **Cápsula Imutável & Estado Atual:**
   - Gere o arquivo de sessão consolidado em `.memoria/ChatOff/capsules/capsule_YYYY-MM-DD_HH-MM.md`.
   - Atualize `.memoria/ChatOff/LATEST_STATE.md`.
4. **Atualização do Grafo de Conhecimento:**
   - Se o projeto usar `.agents/shared/tools/memory_graph.py` ou `tools/memory_graph.py`, registre a sessão e nós correspondentes.
5. **Sincronização Git Automática:**
   - Verifique `git status`.
   - Adicione os arquivos: `git add .`
   - Faça o commit semântico: `git commit -m "docs(chat-off): capsule YYYY-MM-DD_HH-MM - <resumo das conquistas>"`
   - Envie para o remoto: `git push origin main` (se configurado).
   - Confirme o hash do commit e status para o usuário.
