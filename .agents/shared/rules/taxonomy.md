# Taxonomia Canônica WM360 — Mapa Completo de Diretórios

Este documento define a taxonomia oficial para todos os workspaces da WM360.
Toda inteligência artificial conectada ao projeto deve seguir rigorosamente estes 4 diretórios mestres + sistema.

---

## 1. SISTEMA E INFRAESTRUTURA (Oculto)
- **`.agents/`**: O cérebro da IA. Contém personas dos agentes, skills, workflows, tools e pipelines operacionais do workspace.
- **`.memoria/`**: A memória viva do projeto. Contém o grafo semântico em `.memoria/graph/knowledge_graph.json`, a ponte de retomada em `.memoria/ChatOff/LATEST_STATE.md` e as cápsulas imutáveis de sessão em `.memoria/ChatOff/capsules/`.

---

## 2. ENTRADA BRUTA (`@input/` & `@inbox/` - Não-versionado)
Tudo o que veio de fora (cliente, mercado, dados brutos). É estritamente local e nunca é enviado para o Git.

- **`@inbox/`**: ZONA DE ENTRADA UNIVERSAL (Drop Zone). Qualquer novo arquivo recebido do cliente deve ser colocado aqui. O `agent-admin` lê, classifica e move para a subpasta correta.
- **`@input/briefing/`**: Respostas do SuperBriefing, transcrições de áudio/WhatsApp, questionários.
- **`@input/orcamento/`**: Planilhas de horas, propostas enviadas, orçamento técnico e comercial.
- **`@input/contrato/`**: Contratos assinados, NDAs, termos de uso, documentos jurídicos.
- **`@input/aditivos/`**: Mudanças de escopo acordadas e termos aditivos.
- **`@input/financeiro/`**: NFs, recibos, comprovantes e controle de pagamentos.
- **`@input/atas/`**: Atas de reunião, gravações e decisões formais com cliente.
- **`@input/marca/`**: Logos originais do cliente, brand books, fontes e guia de cores original.
- **`@input/midias/`**: Fotos brutas, vídeos originais, áudios e arquivos pesados.
- **`@input/referencias/`**: Moodboards, inspirações visuais, URLs e benchmarks.

---

## 3. PROCESSO / ELABORAÇÃO (`process/` - Versionado)
Inteligência aplicada. O dado bruto foi processado e está sendo trabalhado e estruturado.

- **`process/prd/`**: Product Requirements Document (PRD), especificações técnicas e funcionais.
- **`process/arquitetura/`**: Decisões de arquitetura (ADRs), diagramas, sitemaps e jornadas.
- **`process/estrategia/`**: Playbooks de campanha, funis de vendas, plano editorial.
- **`process/persona/`**: Estudo de ICP, persona do cliente e posicionamento.
- **`process/cronograma/`**: Planejamento de fases, cronograma Notion/n8n e sprints.
- **`process/pipelines/`**: Automações em desenvolvimento e scripts de processo.

---

## 4. PRODUTO / ENTREGÁVEL (`output/` - Versionado)
O que foi executado, produzido e entregue ao cliente.

- **`output/marca/`**: Identidade visual final, design system e logos produzidos.
- **`output/site/`**: Código-fonte de sites, landing pages e temas.
- **`output/sistema/`**: Aplicações, plugins, dashboards, SaaS e ferramentas desenvolvidas.
- **`output/criativos/`**: Peças visuais aprovadas para anúncios e redes sociais.
- **`output/copy/`**: Textos de anúncio, roteiros finais e copies.
- **`output/conteudo/`**: Aulas, e-books, artigos e posts produzidos.
- **`output/campanhas/`**: Estrutura de campanhas de tráfego e relatórios de performance.
- **`output/entregaveis/`**: Entregas formais (`em-revisao/` e `aprovados/`).

---

## 5. SUPORTE LOCAL (`@`)
- **`@scratch/`**: Rascunhos, esboços e testes sem destino final.
- **`@quarentena/`**: Arquivos movidos pelo `agent-admin` para análise de segurança ou classificação.
