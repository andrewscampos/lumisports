# Publicar matérias estáticas (LumiSports)

O blog é **100% estático** — sem API, sem Vue. Ideal para Google AdSense e SEO.

## Fluxo

1. Coloque ou edite o rascunho em `txts/nome-do-arquivo.txt`
2. Atualize o post correspondente em `data/posts.json` (título, excerpt, content, metaKeywords, tags)
3. Gere as páginas HTML:

```bash
python3 scripts/build-static.py
```

Isso recria:
- `index.html` (home com cards)
- `blog/*.html` (uma página por matéria)
- `sitemap.xml`

## Estrutura

| Arquivo txt | Página gerada |
|-------------|---------------|
| `analise-flamengo-...` | `blog/flamengo-vence-estudiantes-libertadores-moral-palmeiras.html` |
| `abel-faz-alerta-...` | `blog/abel-ferreira-arbitragem-corajosa-flamengo-palmeiras.html` |
| `cuca-evita-previsao-...` | `blog/cuca-neymar-santos-panturrilha-sul-americana-copa-2026.html` |
| `selecao-10-03-2026.txt` | `blog/convocacao-selecao-brasileira-ancelotti-copa-2026.html` |

## Deploy

Envie para o servidor: `index.html`, `blog/`, `css/`, `js/`, `logo.svg`, `ads.txt`, `robots.txt`, `sitemap.xml`.

Altere `SITE_URL` em `scripts/build-static.py` se o domínio for diferente de `https://lumisports.com.br`.

A versão antiga com Vue/API está em `index.spa.bak.html` (backup).
