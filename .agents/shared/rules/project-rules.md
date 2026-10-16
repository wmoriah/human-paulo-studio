# Regras de Ouro do Projeto — Human Paulo Studio

## Protocolos Obrigatórios de Operação

1. **Idioma Oficial:** Comunicação em Português (pt-BR).
2. **Investigação Antes da Edição:** Ler arquivos e inspecionar o estado do código antes de propor mudanças.
3. **Plano de Implementação:** Sempre apresentar um plano claro antes de editar múltiplos arquivos.
4. **Convenção `@` (Não-Versionável):**
   - Qualquer diretório ou arquivo com o prefixo `@` é estritamente local e nunca é enviado ao Git.
   - O arquivo `.env` nunca deve ser comitado.
5. **Drop Zone `@inbox/`:**
   - Todo novo arquivo recebido do cliente entra por `@inbox/`.
   - O `agent-admin` classifica e move para a subpasta correta.
6. **Memória de Sessão:**
   - Sempre executar qualquer alias de início de sessão para restaurar a memória rápida (`.memoria/ChatOff/LATEST_STATE.md`).
   - Sempre executar qualquer alias de encerramento de sessão para criar a cápsula imutável de sessão e sincronizar o Git.
