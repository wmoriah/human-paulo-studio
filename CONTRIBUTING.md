# Como contribuir

Obrigado por querer ajudar! Este repo devolve para a comunidade o que a Human Academy e o PAULO.IA ensinaram na Live #1, e queremos que cresça com as próximas lives e com o uso real de vocês.

## Formas de contribuir
- **Reportar o que quebra** ao testar uma skill (abra uma issue com o template de bug).
- **Sugerir dicas novas** de lives futuras (template "Dica nova").
- **Traduzir** skills e README para inglês e espanhol.
- **Adaptadores** para outros hubs (Flora, Freepik, Kling direto, etc.).

## Fluxo
1. Faça um **fork** e crie uma branch (`feat/nome-curto` ou `fix/nome-curto`).
2. Edite as skills em `output/sistema/skills/<skill>/` (a fonte). A pasta `.agents/skills/` é a cópia instalada e é regenerada pelo script abaixo.
3. Valide cada skill alterada:
   ```bash
   python3 <caminho-do-skill-creator>/scripts/quick_validate.py output/sistema/skills/<skill>
   ```
4. Regenere a cópia instalada e o pacote:
   ```bash
   python3 output/sistema/manage_suite.py --install-workspace --package
   ```
5. Atualize o [`CHANGELOG.md`](./CHANGELOG.md) e abra o Pull Request.

## Regras das skills
- Toda skill precisa de **portão de perguntas** antes de gerar o resultado final (é aí que entra a personalização).
- Skills que geram imagem/vídeo devem manter o aviso de **conectores** e apontar para `references/providers.md`.
- **Nunca** inclua senhas, tokens, caminhos locais, fotos ou dados pessoais de terceiros.
- Não use `<` ou `>` no campo `description` do frontmatter (o validador rejeita).

## Créditos
O conteúdo vindo da Live #1 é da **Human Academy**, **Paulo Aguiar (@paulo.ia)**, **Mário (@marioo____)** e **Nando Blum (@nandoblum)**. Ao adaptar ou ampliar, mantenha os créditos e a origem das dicas. Este projeto não é afiliado a eles nem às ferramentas citadas.

Ao contribuir, você concorda que sua contribuição será licenciada sob a [MIT](./LICENSE).
