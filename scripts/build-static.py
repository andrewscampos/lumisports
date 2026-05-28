#!/usr/bin/env python3
"""Gera o site estático do LumiSports a partir de data/posts.json."""

from __future__ import annotations

import html
import json
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_JSON = ROOT / "data" / "posts.json"
BLOG_DIR = ROOT / "blog"
CATEGORY_DIR = ROOT / "categoria"
TAG_DIR = ROOT / "tag"
SITE_URL = "https://lumisports.com.br"
ADSENSE_CLIENT = "ca-pub-6974524299465436"
ADSENSE_SLOT = "6752427405"
LOGO_FILE = "images/logo.png"
FAVICON_FILE = "images/logo.png"
DEFAULT_POST_IMAGE = "images/default-post.svg"
LOGO_ALT = "LumiSports"
TWITTER_SITE = "@lumisports"

CATEGORY_LABELS = {
    "futebol": "Futebol",
    "brasileirao": "Brasileirão",
    "libertadores": "Libertadores",
    "santos": "Santos",
    "brasil": "Seleção Brasileira",
    "palmeiras": "Palmeiras",
    "selecao-brasileira": "Seleção Brasileira",
    "neymar": "Neymar",
    "cartola-feminino": "Cartola Feminino",
    "formula1": "Fórmula 1",
    "futebol-internacional": "Futebol Internacional",
    "estrategia": "Estratégia",
    "analise": "Análise",
    "tecnologia": "Tecnologia",
    "scouting": "Scouting",
    "gestao": "Gestão",
    "preparacao": "Preparação",
    "relatorios": "Relatórios",
    "tatica": "Tática",
    "treinamento": "Treinamento",
    "mercado-da-bola": "Mercado da Bola",
}

HOME_TOPICS = [
    ("brasileirao", "Brasileirão"),
    ("libertadores", "Libertadores"),
    ("selecao-brasileira", "Seleção Brasileira"),
    ("neymar", "Neymar"),
    ("futebol-internacional", "Futebol Internacional"),
    ("formula1", "Fórmula 1"),
    ("estrategia", "Estratégia"),
    ("analise", "Análise"),
    ("gestao", "Gestão"),
    ("treinamento", "Treinamento"),
]


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().strip()
    result = []
    prev_dash = False
    for ch in text:
        if ch.isalnum():
            result.append(ch)
            prev_dash = False
        else:
            if not prev_dash:
                result.append("-")
                prev_dash = True
    slug = "".join(result).strip("-")
    return slug or "item"


def post_image_url(post: dict) -> str:
    url = (post.get("imageUrl") or "").strip()
    return url if url else DEFAULT_POST_IMAGE


def is_default_image(post: dict) -> bool:
    return not (post.get("imageUrl") or "").strip()


def absolute_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{SITE_URL}/{path.lstrip('/')}"


def format_date(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except Exception:
        return iso[:10]
    months = {
        1: "janeiro",
        2: "fevereiro",
        3: "março",
        4: "abril",
        5: "maio",
        6: "junho",
        7: "julho",
        8: "agosto",
        9: "setembro",
        10: "outubro",
        11: "novembro",
        12: "dezembro",
    }
    return f"{dt.day:02d} de {months[dt.month]} de {dt.year}"


def to_rfc2822(iso: str) -> str:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return format_datetime(dt)


def category_key(post: dict) -> str:
    return post.get("subitem") or post.get("subcategory") or post.get("category") or "futebol"


def category_label(key: str) -> str:
    return CATEGORY_LABELS.get(key, key.replace("-", " ").title())


def category_slug(key: str) -> str:
    return slugify(key)


def post_title(post: dict) -> str:
    return post["title"]


def render_post_content(content: str) -> str:
    text = (content or "").strip()
    if not text:
        return ""
    # Support rich HTML posts while keeping the original plain-text format working.
    if "<" in text and ">" in text:
        return text
    return "".join(f"<p>{esc(p)}</p>" for p in text.split("\n\n") if p.strip())


def page_image_src(post: dict, assets_prefix: str = "") -> str:
    url = (post.get("imageUrl") or "").strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"{assets_prefix}{url.lstrip('/')}"


def page_image_src_abs(post: dict) -> str:
    return absolute_url(post_image_url(post))


def adsense_block() -> str:
    return f'''<div class="adsense-block" data-adsense>
<span class="adsense-label">Publicidade</span>
<ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_CLIENT}"
    data-ad-slot="{ADSENSE_SLOT}" data-ad-format="auto" data-full-width-responsive="true"></ins>
</div>'''


def render_card(post: dict, prefix: str, item_kind: str = "post") -> str:
    slug = post["slug"]
    title = post["title"]
    excerpt = post.get("excerpt", "")
    date = format_date(post["publishDate"])
    cat_key = category_key(post)
    cat_label = category_label(cat_key)
    img_src = page_image_src(post, prefix)
    img_class = "post-card-media post-card-media--default" if is_default_image(post) else "post-card-media"
    cat_path = f"{prefix}categoria/{category_slug(cat_key)}.html"
    post_path = f"{prefix}blog/{slug}.html"
    return f'''
            <article class="post-card">
                <a href="{esc(post_path)}" class="post-card-link">
                    <div class="{img_class}">
                        <img src="{esc(img_src)}" alt="{esc(title)}" loading="lazy" decoding="async" width="1200" height="675" onerror="this.onerror=null;this.src='{esc(prefix + DEFAULT_POST_IMAGE)}';this.closest('.post-card-media').classList.add('post-card-media--default');">
                        <span class="category-badge">{esc(cat_label)}</span>
                    </div>
                    <div class="post-card-body">
                        <h2>{esc(title)}</h2>
                        <div class="post-meta">
                            <span><i class="far fa-calendar"></i> {esc(date)}</span>
                            <span><i class="far fa-clock"></i> {esc(post.get("readTime", 5))} min</span>
                        </div>
                        <p class="post-excerpt">{esc(excerpt)}</p>
                        <span class="read-more">Ler notícia completa →</span>
                    </div>
                </a>
            </article>'''


def render_chip(label: str, href: str, count: int) -> str:
    return f'<a class="topic-chip" href="{esc(href)}">{esc(label)} <span>({count})</span></a>'


def json_ld_article(post: dict, page_url: str, image_abs: str, logo_abs: str, breadcrumb_url: str) -> str:
    category = category_label(category_key(post))
    data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": post_title(post),
        "description": post.get("metaDescription") or post.get("excerpt", ""),
        "image": [image_abs],
        "datePublished": post["publishDate"],
        "dateModified": post["publishDate"],
        "author": {"@type": "Organization", "name": post.get("author", "LumiSports")},
        "publisher": {
            "@type": "Organization",
            "name": "LumiSports",
            "logo": {"@type": "ImageObject", "url": logo_abs},
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": page_url},
        "keywords": ", ".join(post.get("tags", [])),
        "articleSection": category,
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Início", "item": SITE_URL + "/"},
                {"@type": "ListItem", "position": 2, "name": category, "item": breadcrumb_url},
                {"@type": "ListItem", "position": 3, "name": post_title(post), "item": page_url},
            ],
        },
    }
    return json.dumps(data, ensure_ascii=False)


def json_ld_archive(title: str, page_url: str, description: str, items: list[dict], label: str) -> str:
    itemlist = []
    for idx, post in enumerate(items, start=1):
        itemlist.append(
            {
                "@type": "ListItem",
                "position": idx,
                "url": f"{SITE_URL}/blog/{post['slug']}.html",
                "name": post_title(post),
            }
        )
    data = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "description": description,
        "url": page_url,
        "mainEntity": {"@type": "ItemList", "name": label, "itemListElement": itemlist},
    }
    return json.dumps(data, ensure_ascii=False)


def render_head(title: str, description: str, canonical: str, og_type: str, og_image: str, prefix: str, extra_meta: str = "", extra_jsonld: str = "") -> str:
    return f'''<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <link rel="canonical" href="{esc(canonical)}">
    <meta property="og:type" content="{esc(og_type)}">
    <meta property="og:site_name" content="LumiSports">
    <meta property="og:locale" content="pt_BR">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(description)}">
    <meta property="og:url" content="{esc(canonical)}">
    <meta property="og:image" content="{esc(og_image)}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="675">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="{TWITTER_SITE}">
    <meta name="twitter:title" content="{esc(title)}">
    <meta name="twitter:description" content="{esc(description)}">
    <meta name="twitter:image" content="{esc(og_image)}">
    <link rel="alternate" type="application/rss+xml" title="LumiSports RSS" href="{esc(prefix)}feed.xml">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="{esc(prefix)}css/site.css">
    <link rel="icon" href="{esc(prefix)}{FAVICON_FILE}" type="image/png">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
    {extra_meta}
    {extra_jsonld}
</head>'''


def render_layout(title: str, description: str, canonical: str, og_type: str, og_image: str, prefix: str, body: str, extra_meta: str = "", extra_jsonld: str = "") -> str:
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
{render_head(title, description, canonical, og_type, og_image, prefix, extra_meta, extra_jsonld)}
<body>
    <header>
        <div class="top-bar"><div class="top-bar-content"><i class="fas fa-calendar-alt"></i> <span id="current-date"></span></div></div>
        <nav>
            <a href="{esc(prefix)}index.html" class="logo"><img src="{esc(prefix)}{LOGO_FILE}" alt="{LOGO_ALT}" width="240" height="72"></a>
            <ul class="nav-links">
                <li><a href="{esc(prefix)}index.html"><i class="fas fa-home"></i> Início</a></li>
                <li><a href="{esc(prefix)}index.html#noticias">Notícias</a></li>
                <li><a href="{esc(prefix)}index.html#categorias">Categorias</a></li>
            </ul>
            <button type="button" id="theme-toggle" class="theme-toggle" aria-label="Alternar tema"><i class="fas fa-moon"></i></button>
        </nav>
    </header>
    {body}
    <footer>
        <div class="footer-content">
            <p>&copy; 2026 LumiSports. Notícias de futebol.</p>
            <div class="footer-links">
                <a href="{esc(prefix)}index.html">Início</a>
                <a href="{esc(prefix)}sitemap.xml">Sitemap</a>
                <a href="{esc(prefix)}robots.txt">Robots</a>
                <a href="{esc(prefix)}feed.xml">RSS</a>
            </div>
        </div>
    </footer>
    <script src="{esc(prefix)}js/site.js"></script>
</body>
</html>
'''


def article_page(post: dict, all_posts: list[dict]) -> str:
    slug = post["slug"]
    page_url = f"{SITE_URL}/blog/{slug}.html"
    canonical = page_url
    desc = post.get("metaDescription") or post.get("excerpt", "")
    keywords = post.get("metaKeywords", "")
    cat_key = category_key(post)
    cat_label = category_label(cat_key)
    cat_url = f"{SITE_URL}/categoria/{category_slug(cat_key)}.html"
    image_abs = page_image_src_abs(post)
    img_src = page_image_src(post, "../")
    logo_abs = absolute_url(LOGO_FILE)
    img_class = "post-featured-image post-featured-image--default" if is_default_image(post) else "post-featured-image"

    paragraphs = render_post_content(post["content"])
    tags_html = "".join(
        f'<a class="post-tag" href="../tag/{slugify(t)}.html">{esc(t)}</a>' for t in post.get("tags", [])
    )

    related_posts = [p for p in all_posts if p["slug"] != slug][:3]
    related_html = "".join(
        f'<li><a href="../blog/{esc(p["slug"])}.html">{esc(p["title"])}</a></li>' for p in related_posts
    )

    breadcrumbs = f'''
            <nav class="breadcrumbs" aria-label="Breadcrumb">
                <a href="../index.html">Início</a>
                <span>/</span>
                <a href="../categoria/{esc(category_slug(cat_key))}.html">{esc(cat_label)}</a>
                <span>/</span>
                <span>{esc(post_title(post))}</span>
            </nav>'''

    extra_jsonld = f'<script type="application/ld+json">{json_ld_article(post, page_url, image_abs, logo_abs, cat_url)}</script>'

    body = f'''
    <div class="main-container">
        <main>
            <a href="../index.html" class="back-link"><i class="fas fa-arrow-left"></i> Voltar para notícias</a>
            {adsense_block()}
            <article class="post-single" itemscope itemtype="https://schema.org/NewsArticle">
                {breadcrumbs}
                <img src="{esc(img_src)}" alt="{esc(post_title(post))}" class="{img_class}" width="1200" height="675" itemprop="image" loading="eager" decoding="async" onerror="this.onerror=null;this.src='../{DEFAULT_POST_IMAGE}';this.classList.add('post-featured-image--default');">
                <div class="post-single-header">
                    <span class="category-badge category-badge-inline" style="position:static;display:inline-block;margin-bottom:1rem;"><a href="../categoria/{esc(category_slug(cat_key))}.html">{esc(cat_label)}</a></span>
                    <h1 itemprop="headline">{esc(post_title(post))}</h1>
                    <div class="post-meta">
                        <span><i class="far fa-calendar"></i> <time datetime="{esc(post['publishDate'])}">{esc(format_date(post['publishDate']))}</time></span>
                        <span><i class="far fa-clock"></i> {esc(post.get('readTime', 5))} min de leitura</span>
                    </div>
                    <p class="post-author"><i class="fas fa-pen-nib"></i> {esc(post.get('author', 'Redação LumiSports'))}</p>
                </div>
                <div class="post-content" itemprop="articleBody">{paragraphs}</div>
                <div class="post-tags">{tags_html}</div>
            </article>
            {adsense_block()}
            <section class="related-posts">
                <h2>Leia também</h2>
                <ul class="related-list">{related_html}</ul>
            </section>
        </main>
        <aside class="ad-sidebar">
            <h3><i class="fas fa-bullhorn"></i> Publicidade</h3>
            {adsense_block()}
            {adsense_block()}
        </aside>
    </div>
    '''
    return render_layout(post_title(post) + " | LumiSports", desc, canonical, "article", image_abs, "../", body, extra_meta=f'<meta name="keywords" content="{esc(keywords)}">', extra_jsonld=extra_jsonld)


def archive_page(title: str, description: str, page_url: str, items: list[dict], prefix: str, page_kind: str, archive_slug: str) -> str:
    og_image = absolute_url(DEFAULT_POST_IMAGE)
    cards = "\n".join(render_card(post, prefix) for post in items)
    breadcrumbs = f'''
            <nav class="breadcrumbs" aria-label="Breadcrumb">
                <a href="{esc(prefix)}index.html">Início</a>
                <span>/</span>
                <span>{esc(title)}</span>
            </nav>'''
    extra_jsonld = f'<script type="application/ld+json">{json_ld_archive(title, page_url, description, items, title)}</script>'
    body = f'''
    <div class="main-container">
        <main>
            <section class="archive-hero">
                {breadcrumbs}
                <span class="archive-kicker">{esc(page_kind)}</span>
                <h1>{esc(title)}</h1>
                <p>{esc(description)}</p>
            </section>
            {adsense_block()}
            <section id="noticias">
                <div class="posts-grid">{cards}</div>
            </section>
            {adsense_block()}
        </main>
        <aside class="ad-sidebar">
            <h3><i class="fas fa-bullhorn"></i> Publicidade</h3>
            {adsense_block()}
            {adsense_block()}
        </aside>
    </div>
    '''
    return render_layout(title + " | LumiSports", description, page_url, "website", og_image, prefix, body, extra_jsonld=extra_jsonld)


def home_page(posts: list[dict], category_counts: Counter, tag_counts: Counter) -> str:
    cards = "\n".join(render_card(post, "") for post in posts)
    category_chips = "".join(
        render_chip(category_label(key), f"categoria/{category_slug(key)}.html", category_counts[key])
        for key, _label in HOME_TOPICS
        if category_counts.get(key)
    )
    top_tags = tag_counts.most_common(10)
    tag_chips = "".join(
        render_chip(tag, f"tag/{slugify(tag)}.html", count)
        for tag, count in top_tags
    )
    hero = f"""
            <section class="hero-section">
                <div class="hero-kicker">Cobertura esportiva diária</div>
                <h1>Últimas notícias do futebol</h1>
                <p>Brasileirão, Libertadores, Seleção Brasileira, Neymar e os principais bastidores do esporte.</p>
                <div class="topic-chips">{category_chips}</div>
            </section>
            {adsense_block()}
            <section class="archive-strip" id="categorias">
                <div class="section-heading">
                    <h2>Categorias em destaque</h2>
                    <p>Veja os principais temas que organizam a cobertura do LumiSports.</p>
                </div>
                <div class="topic-chips">{category_chips}</div>
            </section>
            <section class="archive-strip" id="tags">
                <div class="section-heading">
                    <h2>Tags mais buscadas</h2>
                    <p>Termos que conectam os assuntos mais quentes do site.</p>
                </div>
                <div class="topic-chips">{tag_chips}</div>
            </section>
            <section id="noticias">
                <div class="section-heading">
                    <h2>Notícias recentes</h2>
                    <p>Os artigos mais novos já com cobertura e leitura rápida.</p>
                </div>
                <div class="posts-grid">{cards}</div>
            </section>
            {adsense_block()}
    """

    body = f'''
    <div class="main-container main-container--home">
        <main>
            {hero}
        </main>
        <aside class="ad-sidebar">
            <h3><i class="fas fa-bullhorn"></i> Publicidade</h3>
            {adsense_block()}
            {adsense_block()}
        </aside>
    </div>
    '''
    og_image = absolute_url(DEFAULT_POST_IMAGE)
    description = "Notícias de futebol: Flamengo, Palmeiras, Santos, Libertadores, Seleção Brasileira e Copa do Mundo 2026. Análises e cobertura esportiva no LumiSports."
    return render_layout("LumiSports | Notícias de Futebol, Brasileirão e Copa do Mundo 2026", description, SITE_URL + "/", "website", og_image, "", body, extra_jsonld='<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","name":"LumiSports","url":"https://lumisports.com.br","description":"Notícias de futebol brasileiro"}</script>')


def rss_feed(posts: list[dict]) -> str:
    items = []
    for post in posts:
        link = f"{SITE_URL}/blog/{post['slug']}.html"
        items.append(
            f"""    <item>
      <title>{esc(post['title'])}</title>
      <link>{esc(link)}</link>
      <guid isPermaLink=\"true\">{esc(link)}</guid>
      <description>{esc(post.get('metaDescription') or post.get('excerpt', ''))}</description>
      <pubDate>{esc(to_rfc2822(post['publishDate']))}</pubDate>
      <category>{esc(category_label(category_key(post)))}</category>
    </item>"""
        )
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>LumiSports</title>
    <link>{SITE_URL}/</link>
    <description>Notícias de futebol, análises e bastidores do esporte.</description>
    <language>pt-BR</language>
    <lastBuildDate>{esc(to_rfc2822(posts[0]['publishDate']))}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
'''


def sitemap(posts: list[dict], category_pages: list[dict], tag_pages: list[dict]) -> str:
    urls = [f"  <url><loc>{SITE_URL}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>"]
    urls.append(f"  <url><loc>{SITE_URL}/feed.xml</loc><changefreq>daily</changefreq><priority>0.4</priority></url>")
    for page in category_pages:
        urls.append(
            f'  <url><loc>{SITE_URL}/categoria/{page["slug"]}.html</loc>'
            f'<lastmod>{page["lastmod"]}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>'
        )
    for page in tag_pages:
        urls.append(
            f'  <url><loc>{SITE_URL}/tag/{page["slug"]}.html</loc>'
            f'<lastmod>{page["lastmod"]}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>'
        )
    for p in posts:
        urls.append(
            f'  <url><loc>{SITE_URL}/blog/{p["slug"]}.html</loc>'
            f'<lastmod>{p["publishDate"][:10]}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>'
        )
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    posts = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    posts.sort(key=lambda p: p["publishDate"], reverse=True)

    BLOG_DIR.mkdir(exist_ok=True)
    CATEGORY_DIR.mkdir(exist_ok=True)
    TAG_DIR.mkdir(exist_ok=True)

    category_map: dict[str, list[dict]] = defaultdict(list)
    tag_map: dict[str, list[dict]] = defaultdict(list)
    category_counts: Counter = Counter()
    tag_counts: Counter = Counter()

    for post in posts:
        category_counts[category_key(post)] += 1
        category_map[category_key(post)].append(post)
        for tag in post.get("tags", []):
            tag_map[tag].append(post)
            tag_counts[tag] += 1

    for post in posts:
        path = BLOG_DIR / f"{post['slug']}.html"
        write_text(path, article_page(post, posts))
        print("OK", path.name)

    category_pages = []
    for key, items in category_map.items():
        slug = category_slug(key)
        label = category_label(key)
        page_url = f"{SITE_URL}/categoria/{slug}.html"
        description = f"Últimas matérias de {label} no LumiSports."
        path = CATEGORY_DIR / f"{slug}.html"
        write_text(path, archive_page(label, description, page_url, items, "../", "Categoria", slug))
        category_pages.append({"slug": slug, "lastmod": max(p["publishDate"][:10] for p in items)})
        print("OK", path.as_posix())

    tag_pages = []
    for tag, items in tag_map.items():
        slug = slugify(tag)
        page_url = f"{SITE_URL}/tag/{slug}.html"
        description = f"Conteúdos e análises sobre {tag} no LumiSports."
        path = TAG_DIR / f"{slug}.html"
        write_text(path, archive_page(tag, description, page_url, items, "../", "Tag", slug))
        tag_pages.append({"slug": slug, "lastmod": max(p["publishDate"][:10] for p in items)})
        print("OK", path.as_posix())

    write_text(ROOT / "index.html", home_page(posts, category_counts, tag_counts))
    write_text(ROOT / "feed.xml", rss_feed(posts))
    write_text(ROOT / "sitemap.xml", sitemap(posts, category_pages, tag_pages))
    write_text(ROOT / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    print("OK index.html, feed.xml, sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
