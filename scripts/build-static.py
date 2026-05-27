#!/usr/bin/env python3
"""Gera páginas HTML estáticas a partir de data/posts.json (conteúdo baseado nos txts/)."""
import json
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_JSON = ROOT / "data" / "posts.json"
BLOG_DIR = ROOT / "blog"
SITE_URL = "https://lumisports.com.br"
ADSENSE_CLIENT = "ca-pub-6974524299465436"
ADSENSE_SLOT = "6752427405"
LOGO_FILE = "logo.svg"
DEFAULT_POST_IMAGE = "images/default-post.svg"

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
}


def esc(text):
    return html.escape(str(text), quote=True)


def post_image_url(post):
    """Retorna URL da imagem do post ou a imagem padrão local."""
    url = (post.get("imageUrl") or "").strip()
    return url if url else DEFAULT_POST_IMAGE


def page_image_src(post):
    """Retorna o src correto para a imagem dentro da página gerada."""
    url = post_image_url(post)
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"../{url.lstrip('/')}"


def is_default_image(post):
    return not (post.get("imageUrl") or "").strip()


def absolute_url(path):
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{SITE_URL}/{path.lstrip('/')}"


def adsense_block():
    return f'''<div class="adsense-block">
<ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_CLIENT}"
    data-ad-slot="{ADSENSE_SLOT}" data-ad-format="auto" data-full-width-responsive="true"></ins>
</div>'''


def json_ld_article(post, page_url, image_abs, logo_abs):
    data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": post["title"],
        "description": post.get("metaDescription") or post["excerpt"],
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
    }
    return json.dumps(data, ensure_ascii=False)


def format_date(iso):
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d de %B de %Y").replace(
            "January", "janeiro").replace("February", "fevereiro").replace(
            "March", "março").replace("April", "abril").replace(
            "May", "maio").replace("June", "junho").replace(
            "July", "julho").replace("August", "agosto").replace(
            "September", "setembro").replace("October", "outubro").replace(
            "November", "novembro").replace("December", "dezembro")
    except Exception:
        return iso[:10]


def article_page(post, all_posts):
    slug = post["slug"]
    page_url = f"{SITE_URL}/blog/{slug}.html"
    canonical = page_url
    desc = post.get("metaDescription") or post["excerpt"]
    keywords = post.get("metaKeywords", "")
    cat = CATEGORY_LABELS.get(post.get("subitem") or post.get("category"), "Futebol")
    img_abs = absolute_url(post_image_url(post))
    img_src = page_image_src(post)
    logo_abs = absolute_url(LOGO_FILE)
    img_default = is_default_image(post)
    img_class = "post-featured-image post-featured-image--default" if img_default else "post-featured-image"
    paragraphs = "".join(f"<p>{esc(p)}</p>" for p in post["content"].split("\n\n") if p.strip())
    tags_html = "".join(f'<span class="post-tag">{esc(t)}</span>' for t in post.get("tags", []))
    related = [p for p in all_posts if p["slug"] != slug][:3]
    related_html = "".join(
        f'<li><a href="{esc(p["slug"])}.html">{esc(p["title"])}</a></li>' for p in related
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(post["title"])} | LumiSports</title>
    <meta name="description" content="{esc(desc)}">
    <meta name="keywords" content="{esc(keywords)}">
    <meta name="author" content="{esc(post.get("author", "LumiSports"))}">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <link rel="canonical" href="{esc(canonical)}">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="LumiSports">
    <meta property="og:locale" content="pt_BR">
    <meta property="og:title" content="{esc(post["title"])}">
    <meta property="og:description" content="{esc(desc)}">
    <meta property="og:url" content="{esc(page_url)}">
    <meta property="og:image" content="{esc(img_abs)}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{esc(post["title"])}">
    <meta name="twitter:description" content="{esc(desc)}">
    <meta name="twitter:image" content="{esc(img_abs)}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="../css/site.css">
    <link rel="icon" href="../images/logo-icon.svg" type="image/svg+xml">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
    <script type="application/ld+json">{json_ld_article(post, page_url, img_abs, logo_abs)}</script>
</head>
<body>
    <header>
        <div class="top-bar"><div class="top-bar-content"><i class="fas fa-calendar-alt"></i> <span id="current-date"></span></div></div>
        <nav>
            <a href="../index.html" class="logo"><img src="../{LOGO_FILE}" alt="LumiSports" width="200" height="48"></a>
            <ul class="nav-links">
                <li><a href="../index.html"><i class="fas fa-home"></i> Início</a></li>
                <li><a href="../index.html#noticias">Notícias</a></li>
            </ul>
            <button type="button" id="theme-toggle" class="theme-toggle" aria-label="Alternar tema"><i class="fas fa-moon"></i></button>
        </nav>
    </header>
    <div class="main-container">
        <main>
            <a href="../index.html" class="back-link"><i class="fas fa-arrow-left"></i> Voltar para notícias</a>
            {adsense_block()}
            <article class="post-single" itemscope itemtype="https://schema.org/NewsArticle">
                <img src="{esc(img_src)}" alt="{esc(post["title"])}" class="{img_class}" width="1200" height="630" itemprop="image" onerror="this.onerror=null;this.src='../{DEFAULT_POST_IMAGE}';this.classList.add('post-featured-image--default');">
                <div class="post-single-header">
                    <span class="category-badge" style="position:static;display:inline-block;margin-bottom:1rem;">{esc(cat)}</span>
                    <h1 itemprop="headline">{esc(post["title"])}</h1>
                    <div class="post-meta">
                        <span><i class="far fa-calendar"></i> <time datetime="{esc(post["publishDate"])}">{format_date(post["publishDate"])}</time></span>
                        <span><i class="far fa-clock"></i> {post.get("readTime", 5)} min de leitura</span>
                    </div>
                    <p class="post-author"><i class="fas fa-pen-nib"></i> {esc(post.get("author", "Redação LumiSports"))}</p>
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
    <footer>
        <div class="footer-content">
            <p>&copy; 2026 LumiSports. Notícias de futebol.</p>
            <div class="footer-links">
                <a href="../index.html">Início</a>
                <a href="../sitemap.xml">Sitemap</a>
            </div>
        </div>
    </footer>
    <script src="../js/site.js"></script>
</body>
</html>
"""


def index_page(posts):
    cards = []
    default_og = absolute_url(DEFAULT_POST_IMAGE)
    for post in posts:
        slug = post["slug"]
        cat = CATEGORY_LABELS.get(post.get("subitem") or post.get("category"), "Futebol")
        date = format_date(post["publishDate"])
        img = post_image_url(post)
        card_img_class = "post-card-image post-card-image--default" if is_default_image(post) else "post-card-image"
        cards.append(f"""
            <a href="blog/{esc(slug)}.html" class="post-card">
                <div class="{card_img_class}" style="background-image:url('{esc(img)}')">
                    <span class="category-badge">{esc(cat)}</span>
                </div>
                <div class="post-card-body">
                    <h2>{esc(post["title"])}</h2>
                    <div class="post-meta">
                        <span><i class="far fa-calendar"></i> {date}</span>
                        <span><i class="far fa-clock"></i> {post.get("readTime", 5)} min</span>
                    </div>
                    <p class="post-excerpt">{esc(post["excerpt"])}</p>
                    <span class="read-more">Ler notícia completa →</span>
                </div>
            </a>""")

    cards_html = "\n".join(cards)
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LumiSports | Notícias de Futebol, Brasileirão e Copa do Mundo 2026</title>
    <meta name="description" content="Notícias de futebol: Flamengo, Palmeiras, Santos, Libertadores, Seleção Brasileira e Copa do Mundo 2026. Análises e cobertura esportiva no LumiSports.">
    <meta name="keywords" content="notícias futebol, Brasileirão 2026, Libertadores, Flamengo, Palmeiras, Santos, Seleção Brasileira, Copa do Mundo 2026">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{SITE_URL}/">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="LumiSports">
    <meta property="og:title" content="LumiSports | Notícias de Futebol">
    <meta property="og:description" content="Flamengo, Palmeiras, Santos, Libertadores e Seleção Brasileira.">
    <meta property="og:url" content="{SITE_URL}/">
    <meta property="og:image" content="{default_og}">
    <link rel="icon" href="images/logo-icon.svg" type="image/svg+xml">
    <link rel="sitemap" type="application/xml" href="sitemap.xml">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="css/site.css">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
    <script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"LumiSports","url":"{SITE_URL}","description":"Notícias de futebol brasileiro"}}</script>
</head>
<body>
    <header>
        <div class="top-bar"><div class="top-bar-content"><i class="fas fa-calendar-alt"></i> <span id="current-date"></span></div></div>
        <nav>
            <a href="index.html" class="logo"><img src="{LOGO_FILE}" alt="LumiSports" width="200" height="48"></a>
            <ul class="nav-links">
                <li><a href="index.html"><i class="fas fa-home"></i> Início</a></li>
                <li><a href="#noticias">Notícias</a></li>
            </ul>
            <button type="button" id="theme-toggle" class="theme-toggle" aria-label="Alternar tema"><i class="fas fa-moon"></i></button>
        </nav>
    </header>
    <div class="main-container">
        <main>
            <section class="hero-section">
                <h1>Últimas notícias do futebol</h1>
                <p>Brasileirão, Libertadores, Seleção Brasileira e Copa do Mundo 2026</p>
            </section>
            {adsense_block()}
            <section id="noticias">
                <div class="posts-grid">{cards_html}</div>
            </section>
            {adsense_block()}
        </main>
        <aside class="ad-sidebar">
            <h3><i class="fas fa-bullhorn"></i> Publicidade</h3>
            {adsense_block()}
            {adsense_block()}
        </aside>
    </div>
    <footer>
        <div class="footer-content">
            <p>&copy; 2026 LumiSports. Sua fonte de notícias esportivas.</p>
            <div class="footer-links">
                <a href="index.html">Início</a>
                <a href="sitemap.xml">Sitemap</a>
                <a href="robots.txt">Robots</a>
            </div>
        </div>
    </footer>
    <script src="js/site.js"></script>
</body>
</html>
"""


def sitemap(posts):
    urls = [f"  <url><loc>{SITE_URL}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>"]
    for p in posts:
        urls.append(
            f'  <url><loc>{SITE_URL}/blog/{p["slug"]}.html</loc>'
            f'<lastmod>{p["publishDate"][:10]}</lastmod>'
            f'<changefreq>weekly</changefreq><priority>0.9</priority></url>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n"
    )


def main():
    posts = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    posts.sort(key=lambda p: p["publishDate"], reverse=True)
    BLOG_DIR.mkdir(exist_ok=True)
    for post in posts:
        path = BLOG_DIR / f"{post['slug']}.html"
        path.write_text(article_page(post, posts), encoding="utf-8")
        print("OK", path.name)
    (ROOT / "index.html").write_text(index_page(posts), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(sitemap(posts), encoding="utf-8")
    print("OK index.html, sitemap.xml")


if __name__ == "__main__":
    main()
