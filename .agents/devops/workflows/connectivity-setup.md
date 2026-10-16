---
name: Connectivity Setup Workflow
description: Protocolo de inicialização de repositório privado no GitHub e configuração de credenciais.
---

# Workflow de Conectividade e Repositório Privado

1. **Verificação do GitHub CLI (`gh`):**
   - Executar `gh auth status` para verificar autenticação.
   - Se não estiver autenticado, orientar o usuário a rodar `gh auth login` via navegador.

2. **Criação do Repositório Privado:**
   - Se o projeto não possui remote origin configurado:
     - Executar `gh repo create wmoriah/human-paulo-studio --private --source . --remote origin --confirm`.

3. **Validação de Credenciais:**
   - Garantir que o `.env` contenha as variáveis do projeto e esteja listado no `.gitignore`.
   - Garantir que nenhuma chave privada ou token seja comitado.
