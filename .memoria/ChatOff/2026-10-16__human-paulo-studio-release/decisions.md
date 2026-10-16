# Decisões
- Skills instaladas apenas no projeto (`.agents/skills/`), nunca globalmente.
- Licença MIT e repo público após auditoria de dados sensíveis.
- Só o PDF do tutorial e o zip da suíte são versionados; demais zips ficam ignorados.
- Symlinks de skills locais (bmad, caveman etc.) fora do Git; só as 6 skills do projeto são públicas.
- Histórico recriado com commit único (nada no scaffold depende do histórico).
- Scripts das skills e ferramentas do scaffold marcados no `.gitattributes` para não definirem a "linguagem" do repo.
- Branch `main` sem proteção por enquanto (mantenedor único).
- Export de grupo de WhatsApp usado só como referência de tom; fica em `@inbox/` (ignorado pelo Git).
