---
description: 🔍 AUDITORIA DE PADRÕES - Varrer a raiz, identificar desvios da taxonomia e propor limpeza (Garbage Collection).
---

# 🔍 Workflow de Auditoria de Padrões e Taxonomia

Ao ser invocado para auditar padrões:

1. **Varredura da Raiz:** Liste todos os arquivos e pastas na raiz do projeto.
2. **Conformidade com a Taxonomia:**
   - Diretórios permitidos: `.agents/`, `.memoria/`, `docs/`, `playbooks/`, `pipelines/`, `tools/`, arquivos de código do projeto (`src/`, etc.), e arquivos de configuração padrão (`.gitignore`, etc.).
   - Qualquer pasta ou arquivo avulso (como notas temporárias, zips, prints ou rascunhos) deve ser catalogado.
3. **Detecção de Riscos:**
   - Chaves de API, senhas ou tokens expostos fora do `.env`.
   - Arquivos pesados que não deveriam estar no Git (vídeos, backups brutos).
4. **Plano de Expurgo (Garbage Collection):**
   - Apresente um relatório com as anomalias encontradas e um plano seguro de remoção ou realocação para aprovação do usuário.
   - **NUNCA** remova arquivos sem a autorização explícita do usuário.
