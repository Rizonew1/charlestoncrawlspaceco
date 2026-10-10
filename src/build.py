#!/usr/bin/env python3
"""Static site builder for Charleston Crawlspace Co.
Usage:  python build.py        -> writes ../public (deploy) and ../preview (open offline)
Edit config.json (phone, socials, pricing) and the Markdown files in content/ then re-run.
"""
import json, re, shutil, html, datetime
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent
CFG = json.loads((ROOT / "config.json").read_text())
BRAND, DOMAIN = CFG["brand"], CFG["domain"].rstrip("/")
PHONE, TEL = CFG["phone_display"], CFG["phone_tel"]
A = CFG["address"]
ADDR_LINE = f'{A["street"]}, {A["city"]}, {A["state"]} {A["zip"]}'
PLACEHOLDER = "555-01" in PHONE
MODE = {"v": "public"}
TODAY = datetime.date.today().isoformat()

IMG = {
 "enc":   ("encapsulated-crawl-space-charleston-sc", "Completed crawl space encapsulation in Charleston, SC with sealed liner and dehumidifier"),
 "ins":   ("crawl-space-insulation-charleston-sc", "Spray foam insulation and sealed liner in a Charleston, SC crawl space"),
 "clean": ("crawl-space-cleaning-preparation-charleston-sc", "Technicians cleaning and preparing a Charleston, SC crawl space"),
 "before":("before-crawl-space-encapsulation-charleston-sc", "Damp crawl space with exposed soil before encapsulation in Charleston, SC"),
 "dehu":  ("crawl-space-dehumidifier-charleston-sc", "Crawl space dehumidifier installed on a sealed liner in Charleston, SC"),
}
PHONE_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>'
SOC_ICON = {
 "facebook": ("Facebook", '<path d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 3.78-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.44 2.89h-2.34v6.99A10 10 0 0 0 22 12z"/>'),
 "instagram": ("Instagram", '<g fill="none" stroke="#fff" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/></g><circle cx="17.5" cy="6.5" r="1.2"/>'),
 "youtube": ("YouTube", '<path d="M21.6 7.2a2.5 2.5 0 0 0-1.76-1.77C18.3 5 12 5 12 5s-6.3 0-7.84.43A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.76 1.77C5.7 19 12 19 12 19s6.3 0 7.84-.43a2.5 2.5 0 0 0 1.76-1.77A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8zM10 15V9l5.2 3z"/>'),
 "google_business": ("Google Business Profile", '<path d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/>'),
 "x": ("X", '<path d="M18.9 2H22l-7.2 8.2L23 22h-6.6l-5.2-6.8L5.3 22H2.2l7.7-8.8L1.7 2h6.8l4.7 6.2L18.9 2zm-1.2 18h1.8L7.4 3.9H5.5L17.7 20z"/>'),
}

# ------------------------------------------------------------------ content
def parse(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    meta, body = {}, raw
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = m.group(2)
    meta["body"] = body.strip()
    meta["file"] = path.name
    return meta

def load(folder):
    items = [parse(p) for p in sorted((ROOT / "content" / folder).glob("*.md"))]
    return sorted(items, key=lambda x: int(x.get("order", 99)))

SERVICES = load("services")
LOCATIONS = load("locations")
PAGES = {p.name[:-3]: parse(p) for p in (ROOT / "content" / "pages").glob("*.md")}
for s in SERVICES: s["url"] = f'/{s["slug"]}/'
for l in LOCATIONS: l["url"] = f'/locations/{l["slug"]}/'
SVC_BY_SLUG = {s["slug"]: s for s in SERVICES}
LOC_BY_SLUG = {l["slug"]: l for l in LOCATIONS}
AREAS = []
for l in LOCATIONS:
    if l["area"] not in AREAS: AREAS.append(l["area"])

# ------------------------------------------------------------------ helpers
def esc(s): return html.escape(s, quote=True)
def slugify(t): return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", t).lower()).strip("-")
def money(n): return "${:,.0f}".format(n)

def img(key, alt=None, sizes="(max-width:900px) 100vw, 720px", eager=False, cls=""):
    f, default_alt = IMG[key]
    alt = alt or default_alt
    return (f'<img{(" class=%s" % chr(34)+cls+chr(34)) if cls else ""} src="/assets/img/{f}-720.webp" '
            f'srcset="/assets/img/{f}-400.webp 400w, /assets/img/{f}-720.webp 720w, /assets/img/{f}-1200.webp 1200w" '
            f'sizes="{sizes}" width="1200" height="697" alt="{esc(alt)}" '
            f'{"fetchpriority=%shigh%s" % (chr(34),chr(34)) if eager else "loading=%slazy%s" % (chr(34),chr(34))} decoding="async">')

def gauge_arc(p1, p2, color):
    import math
    def pt(p):
        th = math.pi * (1 - p / 100)
        return 100 + 80 * math.cos(th), 100 - 80 * math.sin(th)
    x1, y1 = pt(p1); x2, y2 = pt(p2)
    return f'<path d="M{x1:.1f} {y1:.1f} A80 80 0 0 1 {x2:.1f} {y2:.1f}" fill="none" stroke="{color}" stroke-width="16"/>'

def gauge():
    return ('<div class="gauge" role="img" aria-label="Example crawl space humidity reading dropping from 88 percent to 48 percent after sealing">'
        '<svg viewBox="0 0 200 112" aria-hidden="true">'
        + gauge_arc(0, 55, "#4F7A62") + gauge_arc(55.5, 65, "#C98A1B") + gauge_arc(65.5, 100, "#B3402F") +
        '<g id="needle" class="needle" style="transform:rotate(-3.6deg)"><line x1="100" y1="100" x2="100" y2="30" stroke="#102632" stroke-width="4" stroke-linecap="round"/></g>'
        '<circle cx="100" cy="100" r="9" fill="#102632"/></svg>'
        '<div class="g-read" id="g-read" aria-hidden="true">48%</div>'
        '<p class="g-cap">Example crawl space humidity before and after sealing. A sealed, conditioned crawl space targets about 45–55% relative humidity.</p></div>')

def call_btn(cls="", label=None):
    label = label or f"Call {PHONE}"
    return f'<a class="call-btn {cls}" href="tel:{TEL}" data-call>{PHONE_ICON}<span>{esc(label)}</span></a>'

# ------------------------------------------------------------------ markdown → html
MD = markdown.Markdown(extensions=["extra", "sane_lists"])
def subst(t):
    return (t.replace("{{phone}}", PHONE).replace("{{tel}}", TEL).replace("{{address}}", ADDR_LINE)
             .replace("{{brand}}", BRAND))

def diagram(name):
    svg = (ROOT / "diagrams" / f"{name}.svg").read_text()
    return f'<figure class="diagram">{svg}<figcaption>How a sealed crawl space is built: liner, insulated walls, sealed vents, dehumidifier and drainage working as one system.</figcaption></figure>'

def price_table():
    P = CFG["pricing"]
    rows = "".join(f'<tr><td>{esc(c["label"])}</td><td>{money(c["lo"])}–{money(c["hi"])} per sq ft</td></tr>' for c in P["conditions"])
    rows2 = "".join(f'<tr><td>{esc(a["label"])}</td><td>{money(a["lo"])}–{money(a["hi"])}</td></tr>' for a in P["addons"])
    return (f'<div class="table-scroll"><table><thead><tr><th>Crawl space condition (encapsulation)</th><th>Typical range</th></tr></thead><tbody>{rows}</tbody></table></div>'
            f'<div class="table-scroll"><table><thead><tr><th>Common add-on</th><th>Typical range</th></tr></thead><tbody>{rows2}</tbody></table></div>')

def estimator():
    P = CFG["pricing"]
    opts = "".join(f'<option data-lo="{c["lo"]}" data-hi="{c["hi"]}">{esc(c["label"])}</option>' for c in P["conditions"])
    chk = "".join(f'<label><input type="checkbox" data-lo="{a["lo"]}" data-hi="{a["hi"]}"> {esc(a["label"])}</label>' for a in P["addons"])
    return ('<div class="est" id="estimator"><div class="row"><label for="sqft">Crawl space size: <span class="sqval" id="sqval">1,200</span> sq ft</label>'
            '<input id="sqft" type="range" min="400" max="3500" step="50" value="1200"></div>'
            f'<div class="row"><label for="cond">What does it look like under there?</label><select id="cond">{opts}</select></div>'
            f'<div class="row checks"><label style="margin-bottom:.4rem">Add-ons you may need</label>{chk}</div>'
            '<div class="out"><p class="range" id="est-range">—</p><p>Planning range only. The real number depends on what the crew finds under your house.</p></div></div>')

def svc_grid(limit=None, exclude=None):
    items = [s for s in SERVICES if s["slug"] != exclude][:limit]
    cards = "".join(f'<a class="svc" href="{s["url"]}">{img(s.get("image","enc"), sizes="(max-width:620px) 100vw, 360px")}<div class="t"><h3>{esc(s["nav"])}</h3><p>{esc(s["summary"])}</p></div></a>' for s in items)
    return f'<div class="cards">{cards}</div>'

def loc_chips():
    out = '<div class="areas">'
    for ar in AREAS:
        out += f'<h3>{esc(ar)}</h3><ul>' + "".join(f'<li><a href="{l["url"]}">{esc(l["nav"])}</a></li>' for l in LOCATIONS if l["area"] == ar) + "</ul>"
    return out + "</div>"

def loc_cards():
    out = ""
    for ar in AREAS:
        out += f'<h2 id="{slugify(ar)}">{esc(ar)}</h2><div class="nb-cards">'
        out += "".join(f'<a href="{l["url"]}"><strong>{esc(l["nav"])}</strong><span>{esc(l["summary"])}</span></a>' for l in LOCATIONS if l["area"] == ar)
        out += "</div>"
    return out

def callout(text=None):
    text = text or "Hear what is actually going on under your house. Call and talk to the crew."
    return f'<div class="callout"><p>{esc(text)}</p>{call_btn()}</div>'

def render_body(md_text):
    h = MD.reset().convert(subst(md_text))
    def fig(m):
        alt, key = m.group(1), m.group(2)
        return f'<figure>{img(key, alt)}<figcaption>{esc(alt)}</figcaption></figure>'
    h = re.sub(r'<p><img alt="([^"]*)" src="img:([a-z]+)"\s*/?></p>', fig, h)
    def tok(m):
        t = m.group(1)
        if t.startswith("diagram:"): return diagram(t[8:])
        if t.startswith("call"): return callout(t[5:] if t.startswith("call:") else None)
        return {"price-table": price_table, "estimator": estimator, "services-grid": svc_grid,
                "locations-chips": loc_chips, "locations-cards": loc_cards}[t]()
    h = re.sub(r"<p>\[\[([^\]]+)\]\]</p>", tok, h)
    # h2 ids
    h = re.sub(r"<h2>(.*?)</h2>", lambda m: f'<h2 id="{slugify(m.group(1))}">{m.group(1)}</h2>', h)
    return h

def split_faq(h):
    """Convert the FAQ section (h3 = question) to <details>. Returns html, [(q,a)]."""
    m = re.search(r'<h2 id="frequently-asked[^"]*">.*?</h2>', h)
    if not m: return h, []
    head, rest = h[:m.end()], h[m.end():]
    nxt = re.search(r"<h2[ >]", rest)
    faq_html, tail = (rest[:nxt.start()], rest[nxt.start():]) if nxt else (rest, "")
    parts = re.split(r"<h3[^>]*>(.*?)</h3>", faq_html)
    qa, out = [], '<div class="faq">'
    for i in range(1, len(parts), 2):
        q, a = parts[i], parts[i + 1].strip()
        qa.append((re.sub(r"<[^>]+>", "", q), re.sub(r"<[^>]+>", " ", a).strip()))
        out += f'<details><summary>{q}</summary><div class="ans">{a}</div></details>'
    return head + out + "</div>" + tail, qa

def words(md_text):
    t = re.sub(r"\[\[.*?\]\]|!\[.*?\]\(.*?\)|[#*>|_`\[\]\(\)-]", " ", subst(md_text))
    return len(t.split())

# ------------------------------------------------------------------ layout
def nav_html():
    sv = "".join(f'<a href="{s["url"]}">{esc(s["nav"])}</a>' for s in SERVICES)
    lc = "".join(f'<a href="{l["url"]}">{esc(l["nav"])}</a>' for l in LOCATIONS)
    return (f'<nav class="nav" id="nav" aria-label="Main"><ul>'
        f'<li class="has-drop"><button class="nl" aria-expanded="false">Services <span class="chev"></span></button><div class="drop cols"><a class="all" href="/services/">All crawl space services</a>{sv}<a href="/crawl-space-encapsulation-charleston-sc-cost/">Encapsulation cost guide</a></div></li>'
        f'<li class="has-drop"><button class="nl" aria-expanded="false">Neighborhoods <span class="chev"></span></button><div class="drop cols"><a class="all" href="/locations/">All Charleston neighborhoods</a>{lc}</div></li>'
        f'<li><a class="nl" href="/crawl-space-encapsulation-charleston-sc-cost/">Cost</a></li>'
        f'<li><a class="nl" href="/about-us/">About</a></li></ul>'
        f'{call_btn("in-menu")}</nav>')

def header():
    return (f'<a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap hdr">'
        f'<a class="brand" href="/" aria-label="{esc(BRAND)} home"><img src="/assets/logo-60.png" srcset="/assets/logo-60.png 1x, /assets/logo.png 2x" width="255" height="60" alt="{esc(BRAND)}"></a>'
        f'<button class="menu-btn" aria-expanded="false" aria-controls="nav">Menu</button>'
        f'{nav_html()}{call_btn()}</div></header>')

def footer():
    soc = ""
    for k, url in CFG["socials"].items():
        if url and (MODE["v"] == "preview" or "REPLACE" not in url):
            name, path = SOC_ICON[k]
            soc += f'<a href="{esc(url)}" rel="noopener me" target="_blank" aria-label="{name}"><svg viewBox="0 0 24 24" aria-hidden="true">{path}</svg></a>'
    sv = "".join(f'<li><a href="{s["url"]}">{esc(s["nav"])}</a></li>' for s in SERVICES)
    lc = "".join(f'<li><a href="{l["url"]}">{esc(l["nav"])}</a></li>' for l in LOCATIONS)
    return (f'<footer class="site-footer"><div class="wrap"><div class="ft"><div>'
        f'<p class="wm">Charleston Crawlspace Co</p><p class="wm-sub">Crawl space encapsulation in Charleston, SC</p>'
        f'<address>{esc(A["street"])}<br>{esc(A["city"])}, {A["state"]} {A["zip"]}<br><a href="tel:{TEL}" data-call>{PHONE}</a></address>'
        f'<p style="margin:.9rem 0 0">Locally owned &amp; operated. Licensed &amp; insured.</p><div class="social">{soc}</div></div>'
        f'<div><h2>Services</h2><ul>{sv}<li><a href="/crawl-space-encapsulation-charleston-sc-cost/">Encapsulation cost guide</a></li></ul></div>'
        f'<div><h2>Charleston neighborhoods</h2><ul class="two-col">{lc}<li><a href="/locations/">All neighborhoods</a></li></ul>'
        f'<h2 style="margin-top:1.4rem">Company</h2><ul><li><a href="/about-us/">About us</a></li><li><a href="/services/">All services</a></li></ul></div></div>'
        f'<div class="legal"><span>&copy; {datetime.date.today().year} {esc(BRAND)}. All rights reserved.</span><span>{esc(ADDR_LINE)}</span></div></div></footer>'
        f'<a class="callbar" href="tel:{TEL}" data-call>{PHONE_ICON}<span>Call {PHONE}</span></a>')

def endcta(title=None):
    title = title or "Find out what is happening under your Charleston home"
    return (f'<section class="endcta"><div class="wrap"><div><h2>{esc(title)}</h2>'
        f'<p>Call and you reach the crew that does the work, not a call center. Tell us your street or neighborhood and what you are seeing, and we will tell you what to expect.</p></div>'
        f'<div class="num"><a class="big" href="tel:{TEL}" data-call>{PHONE}</a>{call_btn("lg", "Call now")}</div></div></section>')

def proof_band():
    S = CFG["stats"]
    cards = (f'<div class="stat"><strong>{S["jobs"]}</strong><span>crawl space jobs completed</span></div>'
             f'<div class="stat"><strong>{S["rating"]}<small>/5</small></strong><span>average homeowner rating</span></div>'
             '<div class="stat"><strong>Licensed</strong><span>and insured</span></div>')
    tl = ""
    for q in CFG.get("testimonials", []):
        tl += f'<figure class="quote"><blockquote>{esc(q["quote"])}</blockquote><figcaption>{esc(q["name"])}{", " + esc(q["area"]) if q.get("area") else ""}</figcaption></figure>'
    return (f'<section class="proof" aria-label="Customer proof"><div class="wrap"><h2>Trusted by Charleston homeowners</h2>'
            f'<div class="stats">{cards}</div>{"<div class=%squotes%s>%s</div>" % (chr(34),chr(34),tl) if tl else ""}'
            f'<p class="proof-call">Join them. Call <a href="tel:{TEL}" data-call>{PHONE}</a> and talk to the crew.</p></div></section>')

def side_call(extra=""):
    return (f'<div class="card call"><h2>Talk to a Charleston crawl space pro</h2><p>The phone is the fastest way to get an inspection on the schedule. {extra}</p>{call_btn()}</div>')

def side_list(title, items, cur):
    li = "".join(f'<li><a href="{u}"{" aria-current=%spage%s" % (chr(34),chr(34)) if u == cur else ""}>{esc(n)}</a></li>' for u, n in items)
    return f'<div class="card"><h3>{esc(title)}</h3><ul>{li}</ul></div>'

def toc(h):
    hs = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', h)
    if len(hs) < 3: return ""
    li = "".join(f'<li><a href="#{i}">{re.sub("<[^>]+>","",t)}</a></li>' for i, t in hs)
    return f'<div class="card toc"><h3>On this page</h3><ul>{li}</ul></div>'

def schema(page, qa, crumbs):
    biz = {"@type": ["HomeAndConstructionBusiness", "LocalBusiness"], "@id": f"{DOMAIN}/#business", "name": BRAND,
        "url": DOMAIN + "/", "telephone": TEL, "image": f"{DOMAIN}/assets/img/{IMG['enc'][0]}-1200.webp",
        "logo": f"{DOMAIN}/assets/logo.png",
        "address": {"@type": "PostalAddress", "streetAddress": A["street"], "addressLocality": A["city"], "addressRegion": A["state"], "postalCode": A["zip"], "addressCountry": "US"},
        "areaServed": [{"@type": "City", "name": "Charleston, SC"}] + [{"@type": "Place", "name": f'{l["nav"]}, Charleston, SC'} for l in LOCATIONS],
        "sameAs": [u for u in CFG["socials"].values() if u and "REPLACE" not in u]}
    g = [biz, {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + u} for i, (u, n) in enumerate(crumbs)]}]
    k = page.get("kind")
    if k == "service":
        g.append({"@type": "Service", "name": page["title"], "serviceType": page["nav"], "provider": {"@id": biz["@id"]},
                  "areaServed": {"@type": "City", "name": "Charleston, SC"}, "url": DOMAIN + page["url"], "description": page["description"]})
    if k == "location":
        g.append({"@type": "Service", "name": f'Crawl space encapsulation in {page["nav"]}', "serviceType": "Crawl space encapsulation",
                  "provider": {"@id": biz["@id"]}, "areaServed": {"@type": "Place", "name": f'{page["nav"]}, Charleston, SC'}, "url": DOMAIN + page["url"]})
    if qa:
        g.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]})
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False) + "</script>"

def desc_with_phone(d):
    d = subst(d)
    return d if PHONE in d else (d.rstrip(". ") + f". Call {PHONE}.")

def ga_snippet():
    g = CFG.get("ga_id")
    if not g or MODE["v"] != "public": return ""
    return (f'<!-- Google tag (gtag.js) -->\n<script async src="https://www.googletagmanager.com/gtag/js?id={g}"></script>\n'
            f'<script>\n  window.dataLayer = window.dataLayer || [];\n  function gtag(){{dataLayer.push(arguments);}}\n  gtag(\'js\', new Date());\n\n  gtag(\'config\', \'{g}\');\n</script>\n')

def document(page, body, qa, crumbs):
    page = dict(page, description=desc_with_phone(page["description"]))
    title = page.get("meta_title") or f'{page["title"]} | {BRAND}'
    robots = '<meta name="robots" content="noindex,nofollow">' if PLACEHOLDER else '<meta name="robots" content="index,follow,max-image-preview:large">'
    ogimg = f'{DOMAIN}/assets/img/{IMG[page.get("image","enc")][0]}-1200.webp'
    return f'''<!doctype html>
<html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(page["description"])}">
{robots}<link rel="canonical" href="{DOMAIN}{page["url"]}">
{ga_snippet()}<meta name="theme-color" content="#1B3B4B"><meta name="format-detection" content="telephone=yes">
<link rel="icon" href="/assets/icon-32.png" sizes="32x32"><link rel="apple-touch-icon" href="/assets/icon-180.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="{esc(BRAND)}"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(page["description"])}"><meta property="og:url" content="{DOMAIN}{page["url"]}"><meta property="og:image" content="{ogimg}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Public+Sans:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="/assets/css/style.css">
{schema(page, qa, crumbs)}
</head><body>
{header()}
<main id="main">{body}</main>
{footer()}
<script src="/assets/js/site.js" defer></script>
</body></html>'''

def crumbs_html(crumbs):
    parts = []
    for i, (u, n) in enumerate(crumbs):
        parts.append(esc(n) if i == len(crumbs) - 1 else f'<a href="{u}">{esc(n)}</a>')
    return '<p class="crumbs">' + "<span>/</span>".join(parts) + "</p>"

def page_head(page, crumbs):
    lede = f'<p class="lede">{esc(subst(page["lede"]))}</p>'
    media = f'<div class="head-img">{img(page.get("image","enc"), sizes="(max-width:900px) 0px, 420px", eager=True)}</div>'
    return (f'<section class="page-head"><div class="wrap split"><div>{crumbs_html(crumbs)}<h1>{esc(page["title"])}</h1>{lede}{call_btn("lg")}</div>{media}</div></section>')

def content_page(page, crumbs, sidebar_fn):
    h = render_body(page["body"])
    h, qa = split_faq(h)
    side = sidebar_fn(h)
    body = (page_head(page, crumbs) +
        f'<section class="content"><div class="wrap"><article class="prose">{h}</article><aside class="side">{side}</aside></div></section>' + proof_band() + endcta())
    return body, qa

def home_page(page):
    h = render_body(page["body"])
    h, qa = split_faq(h)
    secs = re.split(r'(?=<h2 id=)', h)
    bands = ""
    for i, s in enumerate(s for s in secs if s.strip()):
        m = re.match(r'(<h2 id="[^"]+">.*?</h2>)(.*)', s, re.S)
        head, rest = (m.group(1), m.group(2)) if m else ("", s)
        wide = " wide" if ('class="cards' in rest or 'class="areas' in rest or 'class="faq' in rest or 'class="diagram' in rest) else ""
        bands += f'<section class="band{" alt" if i % 2 else ""}"><div class="wrap band-grid">{head}<div class="band-body prose{wide}">{rest}</div></div></section>'
    hero = (f'<section class="hero"><div class="wrap"><div><h1>{esc(page["title"])}</h1><p class="lede">{esc(subst(page["lede"]))}</p>{call_btn("lg")}'
        f'<p class="small">{esc(ADDR_LINE)}</p></div><div class="hero-media">{img("enc", sizes="(max-width:900px) 100vw, 560px", eager=True)}{gauge()}</div></div></section>'
        f'<div class="trust"><ul><li>{CFG["stats"]["jobs"]} crawl space jobs completed</li><li>{CFG["stats"]["rating"]} average homeowner rating</li><li>Licensed and insured</li><li>Locally owned. No call center. You reach the crew.</li></ul></div>')
    return hero + bands + proof_band() + endcta(), qa

# ------------------------------------------------------------------ build
def to_relative(doc, url):
    depth = url.strip("/").count("/") + 1 if url != "/" else 0
    pre = "../" * depth if depth else "./"
    def fix(p):
        if p.startswith("//"): return p
        p = p.split("#")[0] if False else p
        if p == "/": return pre + "index.html"
        if p.endswith("/"): return pre + p[1:] + "index.html"
        return pre + p[1:]
    def attr(m):
        name, val = m.group(1), m.group(2)
        if name == "srcset":
            val = ", ".join(" ".join([fix(x.split()[0])] + x.split()[1:]) for x in val.split(","))
        else:
            if name == "href" and (val.startswith("/") and not val.startswith("//")):
                anchor = ""
                if "#" in val: val, anchor = val.split("#", 1); anchor = "#" + anchor
                val = fix(val) + anchor
            elif val.startswith("/") and not val.startswith("//"): val = fix(val)
        return f'{name}="{val}"'
    # leave canonical/og absolute (they start with https)
    return re.sub(r'\b(href|src|srcset)="([^"]*)"', attr, doc)

def write(out_dir, url, doc, relative):
    if relative: doc = to_relative(doc, url)
    p = out_dir / url.strip("/") / "index.html" if url != "/" else out_dir / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(doc, encoding="utf-8")

def main():
    pages, report = [], []
    home = PAGES["home"]; home.update(url="/", kind="home", description=home["description"]); 
    body, qa = home_page(home); pages.append((home, body, qa, [("/", "Home")])); report.append(("Home", words(home["body"])))

    all_svc = [(s["url"], s["nav"]) for s in SERVICES]
    for s in SERVICES:
        s.update(kind="service")
        crumbs = [("/", "Home"), ("/services/", "Services"), (s["url"], s["nav"])]
        def side(h, s=s):
            return side_call() + toc(h) + side_list("Crawl space services", all_svc, s["url"])
        body, qa = content_page(s, crumbs, side); pages.append((s, body, qa, crumbs)); report.append((s["nav"], words(s["body"])))

    for l in LOCATIONS:
        l.update(kind="location", description=l["description"])
        crumbs = [("/", "Home"), ("/locations/", "Neighborhoods"), (l["url"], l["nav"])]
        near = [(LOC_BY_SLUG[n]["url"], LOC_BY_SLUG[n]["nav"]) for n in l.get("nearby", "").replace(" ", "").split(",") if n in LOC_BY_SLUG]
        def side(h, l=l, near=near):
            return side_call(f'We work across {l["nav"]} regularly.') + toc(h) + (side_list("Nearby neighborhoods", near, "") if near else "") + side_list("Services", all_svc[:6], "")
        body, qa = content_page(l, crumbs, side); pages.append((l, body, qa, crumbs)); report.append((l["nav"], words(l["body"])))

    for key, url, crumbs, kind in [("services-hub", "/services/", [("/", "Home"), ("/services/", "Services")], "hub"),
                                   ("locations-hub", "/locations/", [("/", "Home"), ("/locations/", "Neighborhoods")], "hub"),
                                   ("cost", "/crawl-space-encapsulation-charleston-sc-cost/", [("/", "Home"), ("/services/", "Services"), ("/crawl-space-encapsulation-charleston-sc-cost/", "Cost guide")], "cost"),
                                   ("about", "/about-us/", [("/", "Home"), ("/about-us/", "About us")], "about")]:
        p = PAGES[key]; p.update(url=url, kind=kind)
        def side(h): return side_call() + toc(h) + side_list("Crawl space services", all_svc, "")
        body, qa = content_page(p, crumbs, side); pages.append((p, body, qa, crumbs)); report.append((p["title"][:34], words(p["body"])))

    nf = {"title": "Page not found", "lede": "That page moved or never existed. The services and neighborhood lists below will get you back on track, or call us and we will point you to the right place.",
          "description": "Page not found.", "url": "/404.html", "image": "enc", "body": "## Where to go next\n\n[[services-grid]]\n\n[[locations-chips]]", "kind": "hub"}
    body, qa = content_page(nf, [("/", "Home"), ("/404.html", "Not found")], lambda h: side_call()); pages.append((nf, body, qa, [("/", "Home")]))

    for name, relative in (("public", False), ("preview", True)):
        MODE["v"] = name
        out = OUT / name
        if out.exists(): shutil.rmtree(out)
        out.mkdir(parents=True)
        shutil.copytree(ROOT / "assets", out / "assets")
        for pg, body, qa, crumbs in pages:
            doc = document(pg, body, qa, crumbs)
            if pg["url"] == "/404.html":
                p = out / "404.html"; p.write_text(to_relative(doc, "/") if relative else doc, encoding="utf-8")
            else: write(out, pg["url"], doc, relative)

    pub = OUT / "public"
    urls = [p[0]["url"] for p in pages if p[0]["url"] != "/404.html"]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f'<url><loc>{DOMAIN}{u}</loc><lastmod>{TODAY}</lastmod><priority>{"1.0" if u=="/" else "0.8"}</priority></url>\n' for u in urls) + "</urlset>\n"
    (pub / "sitemap.xml").write_text(sm)
    (pub / "robots.txt").write_text(("User-agent: *\nDisallow: /\n# Placeholder phone/social values detected in config.json - site blocked from indexing until you replace them.\n" if PLACEHOLDER
        else "User-agent: *\nAllow: /\n") + f"Sitemap: {DOMAIN}/sitemap.xml\n")
    old = ["crawl-space-encapsulation-goose-creek", "crawl-space-encapsulation-in-johns-island-sc", "crawl-space-encapsulation-north-charleston-sc",
           "crawl-space-encapsulation-in-summerville", "crawl-space-encapsulation-in-mount-pleasant"]
    (pub / "_redirects").write_text("# Old WordPress city pages -> neighborhoods hub\n" + "".join(f"/locations/{o}  /locations/  301\n/locations/{o}/  /locations/  301\n" for o in old))
    (pub / "_headers").write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: SAMEORIGIN\n\n/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n")
    (pub / "CNAME").unlink(missing_ok=True)
    print(f"{len(urls)} pages built. Placeholder values in config: {PLACEHOLDER}")
    for n, w in report: print(f"{w:6d}  {n}")

if __name__ == "__main__":
    main()
