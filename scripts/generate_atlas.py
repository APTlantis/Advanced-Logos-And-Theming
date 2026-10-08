"""
APTlantis Palette Atlas Generator
Reads logos.json, detects available files, generates palette-atlas.html.
"""

import re
import os
import json

ROOT        = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
PALETTE_DIR = os.path.join(ROOT, 'palettes')
SVG_DIR     = os.path.join(ROOT, 'svg')
PNG_DIR     = os.path.join(ROOT, 'png')
ICO_DIR     = os.path.join(ROOT, 'ico')
LOGOS_JSON  = os.path.join(ROOT, 'logos.json')
OUT_FILE    = os.path.join(ROOT, 'palette-atlas.html')


def read_palette(path):
    with open(path, 'rb') as f:
        raw = f.read()
    try:
        text = raw.decode('utf-16')
    except Exception:
        text = raw.decode('utf-8', errors='replace')
    hexes = re.findall(r'#([0-9A-Fa-f]{6})', text)
    return ['#' + h.upper() for h in hexes]


def read_svg(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def hex_luminance(hex_color):
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def file_exists(*parts):
    return os.path.exists(os.path.join(*parts))


def build_cards(logos_data):
    cards = []
    palette_files = sorted([
        f for f in os.listdir(PALETTE_DIR)
        if f.endswith('-palette.txt') and f != 'Combined.Pallets.txt'
    ])

    for pf in palette_files:
        slug_full = pf.replace('apt-', '').replace('-palette.txt', '')   # e.g. "python-logo-v2"
        slug = slug_full.replace('-logo', '', 1)                          # e.g. "python-v2"

        meta = logos_data.get(slug, {})
        display = meta.get('label', slug.replace('-', ' ').title())
        site    = meta.get('site', '#')
        desc    = meta.get('description', '')

        # SVG
        svg_path = os.path.join(SVG_DIR, f'apt-{slug_full}.svg')
        svg_content = read_svg(svg_path) if os.path.exists(svg_path) else ''

        # Palette colors
        palette = read_palette(os.path.join(PALETTE_DIR, pf))

        # Available download files (relative to HTML output root)
        files = {}
        if os.path.exists(svg_path):
            files['svg'] = f'svg/apt-{slug_full}.svg'
        if file_exists(PNG_DIR, f'apt-{slug_full}.png'):
            files['png'] = f'png/apt-{slug_full}.png'
        if file_exists(ICO_DIR, f'apt-{slug_full}.ico'):
            files['ico'] = f'ico/apt-{slug_full}.ico'
        if file_exists(PNG_DIR, f'apt-{slug_full}.ico'):   # ico sometimes in png dir
            files.setdefault('ico', f'png/apt-{slug_full}.ico')
        palette_path = f'palettes/apt-{slug_full}-palette.txt'
        if file_exists(PALETTE_DIR, f'apt-{slug_full}-palette.txt'):
            files['palette'] = palette_path

        # Dominant dark bg color
        dark = '#0d0d0d'
        if palette:
            dark = sorted(palette, key=hex_luminance)[0]

        cards.append({
            'slug':    slug,
            'name':    display,
            'desc':    desc,
            'site':    site,
            'palette': palette,
            'files':   files,
            'svg':     svg_content,
            'dark':    dark,
        })

    return cards


def swatch_html(colors):
    if not colors:
        return '<div class="swatches empty">No palette data</div>'
    swatches = ''
    for color in colors:
        lum = hex_luminance(color)
        text_color = '#111' if lum > 0.55 else '#eee'
        swatches += (
            f'<div class="swatch" style="background:{color};color:{text_color}" '
            f'title="{color}">'
            f'<span class="swatch-label">{color}</span>'
            f'</div>'
        )
    return f'<div class="swatches">{swatches}</div>'


def card_html(card):
    # SVG block
    if card['svg']:
        svg = re.sub(r'<\?xml[^?]*\?>', '', card['svg']).strip()
        svg = re.sub(r'\s(width|height)="[^"]*"', '', svg, count=2)
        svg = svg.replace('ns1:href=', 'href=')
        svg_block = f'<div class="logo-wrap">{svg}</div>'
    else:
        svg_block = f'<div class="logo-wrap logo-missing"><span>{card["name"]}</span></div>'

    color_count = len(card['palette'])
    swatches    = swatch_html(card['palette'])
    slug        = card['slug']

    # Visit site button â€” disabled if no real URL
    site_disabled = ' disabled title="No external site"' if card['site'] == '#' else ''
    site_target   = '' if card['site'] == '#' else 'target="_blank" rel="noopener"'

    visit_btn = (
        f'<a class="btn btn-visit" href="{card["site"]}" {site_target}{site_disabled}>'
        f'<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">'
        f'<circle cx="8" cy="8" r="6.5"/>'
        f'<path d="M8 1.5c-1.5 2-2.5 4-2.5 6.5s1 4.5 2.5 6.5M8 1.5c1.5 2 2.5 4 2.5 6.5S9.5 12.5 8 14.5M1.5 8h13"/>'
        f'</svg>'
        f'Visit Site</a>'
    )

    dl_btn = (
        f'<button class="btn btn-dl" data-slug="{slug}" onclick="toggleDl(this)">'
        f'<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">'
        f'<path d="M8 2v8M5 7l3 3 3-3M2 12h12"/>'
        f'</svg>'
        f'Resources</button>'
    )

    return f'''
<article class="card" id="card-{slug}" style="--card-dark:{card["dark"]}">
  <header class="card-header">
    <span class="lang-name">{card["name"]}</span>
    <span class="color-count">{color_count} colors</span>
  </header>
  {svg_block}
  <div class="card-actions">
    {visit_btn}
    {dl_btn}
  </div>
  <div class="dl-panel" id="dl-{slug}" hidden></div>
  {swatches}
</article>'''


# â”€â”€ HTML Template â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

HTML_TEMPLATE = '''\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>APTlantis Â· Palette Atlas</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg:       #07080c;
    --surface:  #0f1117;
    --border:   #1e2030;
    --accent:   #4a9eff;
    --accent2:  #a78bfa;
    --green:    #34d399;
    --text:     #c8cdd8;
    --dim:      #555a6e;
    --radius:   10px;
    --card-w:   220px;
    --gap:      18px;
    font-size: 13px;
  }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Segoe UI', system-ui, sans-serif;
    min-height: 100vh;
    padding: 48px 32px 80px;
  }}

  /* â”€â”€ Header â”€â”€ */
  .atlas-header {{
    text-align: center;
    margin-bottom: 56px;
  }}
  .atlas-title {{
    font-size: clamp(2rem, 5vw, 3.6rem);
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(135deg, #4a9eff 0%, #a78bfa 50%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
  }}
  .atlas-sub {{
    margin-top: 10px;
    font-size: 1rem;
    color: var(--dim);
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }}
  .atlas-rule {{
    margin: 28px auto 0;
    width: 80px; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    border: none;
  }}
  .atlas-count {{
    margin-top: 20px;
    font-size: 0.85rem;
    color: var(--dim);
  }}

  /* â”€â”€ Grid â”€â”€ */
  .atlas-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(var(--card-w), 1fr));
    gap: var(--gap);
    max-width: 1600px;
    margin: 0 auto;
  }}

  /* â”€â”€ Card â”€â”€ */
  .card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    position: relative;
  }}
  .card:hover {{
    transform: translateY(-4px);
    border-color: #2e3350;
    box-shadow: 0 16px 48px rgba(0,0,0,0.6), 0 0 0 1px rgba(74,158,255,0.08);
  }}

  /* â”€â”€ Card header â”€â”€ */
  .card-header {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    padding: 10px 12px 8px;
    border-bottom: 1px solid var(--border);
  }}
  .lang-name {{
    font-weight: 700;
    font-size: 0.95rem;
    color: #e0e4f0;
  }}
  .color-count {{
    font-size: 0.72rem;
    color: var(--dim);
    font-variant-numeric: tabular-nums;
  }}

  /* â”€â”€ Logo â”€â”€ */
  .logo-wrap {{
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px 16px;
    background: color-mix(in srgb, var(--card-dark, #0d0d0d) 35%, var(--surface));
    min-height: 140px;
  }}
  .logo-wrap svg {{
    width: 100%;
    max-width: 140px;
    max-height: 120px;
    height: auto;
  }}
  .logo-missing {{
    color: var(--dim);
    font-size: 0.8rem;
    font-style: italic;
  }}

  /* â”€â”€ Action buttons â”€â”€ */
  .card-actions {{
    display: flex;
    gap: 6px;
    padding: 8px 10px;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    background: rgba(255,255,255,0.015);
  }}

  .btn {{
    flex: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    padding: 5px 8px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    cursor: pointer;
    border: 1px solid transparent;
    text-decoration: none;
    transition: background 0.14s, border-color 0.14s, color 0.14s, transform 0.1s;
    white-space: nowrap;
  }}
  .btn svg {{
    width: 13px; height: 13px;
    flex-shrink: 0;
  }}
  .btn:active {{ transform: scale(0.96); }}

  .btn-visit {{
    background: rgba(74,158,255,0.1);
    border-color: rgba(74,158,255,0.25);
    color: var(--accent);
  }}
  .btn-visit:hover {{
    background: rgba(74,158,255,0.2);
    border-color: rgba(74,158,255,0.5);
    color: #7dbfff;
  }}
  .btn-visit[disabled] {{
    opacity: 0.35;
    pointer-events: none;
  }}

  .btn-dl {{
    background: rgba(167,139,250,0.1);
    border-color: rgba(167,139,250,0.25);
    color: var(--accent2);
  }}
  .btn-dl:hover {{
    background: rgba(167,139,250,0.2);
    border-color: rgba(167,139,250,0.5);
    color: #c4b0fd;
  }}
  .btn-dl.active {{
    background: rgba(167,139,250,0.22);
    border-color: rgba(167,139,250,0.6);
    color: #c4b0fd;
  }}

  /* â”€â”€ Download panel â”€â”€ */
  .dl-panel {{
    padding: 10px 10px 8px;
    background: rgba(0,0,0,0.3);
    border-bottom: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    gap: 6px;
    animation: slideDown 0.15s ease;
  }}
  .dl-panel[hidden] {{ display: none !important; }}

  @keyframes slideDown {{
    from {{ opacity: 0; transform: translateY(-4px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}

  .dl-desc {{
    font-size: 0.72rem;
    color: var(--dim);
    line-height: 1.4;
    font-style: italic;
    padding-bottom: 4px;
    border-bottom: 1px solid var(--border);
  }}

  .dl-links {{
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }}

  .dl-link {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 9px;
    border-radius: 4px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    text-decoration: none;
    border: 1px solid transparent;
    transition: background 0.12s, border-color 0.12s;
    cursor: pointer;
  }}

  .dl-link-svg   {{ color: #34d399; background: rgba(52,211,153,0.08); border-color: rgba(52,211,153,0.2); }}
  .dl-link-png   {{ color: #f59e0b; background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.2); }}
  .dl-link-ico   {{ color: #f87171; background: rgba(248,113,113,0.08); border-color: rgba(248,113,113,0.2); }}
  .dl-link-palette {{ color: #a78bfa; background: rgba(167,139,250,0.08); border-color: rgba(167,139,250,0.2); }}

  .dl-link:hover {{ filter: brightness(1.25); }}

  /* â”€â”€ Swatches â”€â”€ */
  .swatches {{
    display: flex;
    height: 32px;
    flex-shrink: 0;
  }}
  .swatches.empty {{
    background: #1a1a20;
    color: var(--dim);
    font-size: 0.72rem;
    align-items: center;
    justify-content: center;
    height: 32px;
  }}
  .swatch {{
    flex: 1;
    position: relative;
    cursor: default;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    overflow: hidden;
    transition: flex 0.15s ease;
  }}
  .swatch:hover {{ flex: 2.5; }}
  .swatch-label {{
    font-size: 0.6rem;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    letter-spacing: 0.03em;
    padding: 3px 2px;
    opacity: 0;
    transition: opacity 0.15s ease;
    white-space: nowrap;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
  }}
  .swatch:hover .swatch-label {{ opacity: 1; }}

  /* â”€â”€ Footer â”€â”€ */
  .atlas-footer {{
    text-align: center;
    margin-top: 64px;
    color: var(--dim);
    font-size: 0.78rem;
    letter-spacing: 0.05em;
  }}
</style>
</head>
<body>

<header class="atlas-header">
  <h1 class="atlas-title">APTlantis<br>Palette Atlas</h1>
  <p class="atlas-sub">A visual map of language ecosystems</p>
  <hr class="atlas-rule">
  <p class="atlas-count">{total_logos} logos &nbsp;Â·&nbsp; {total_colors} extracted colors</p>
</header>

<main class="atlas-grid">
{cards_html}
</main>

<footer class="atlas-footer">
  <p>APTlantis &mdash; hover swatches to reveal hex &nbsp;|&nbsp; hover cards to lift &nbsp;|&nbsp; click Resources to see available downloads</p>
</footer>

<script>
const LOGOS_DATA = {logos_json};

function toggleDl(btn) {{
  const slug  = btn.dataset.slug;
  const panel = document.getElementById('dl-' + slug);
  const open  = !panel.hidden;

  // Close all others
  document.querySelectorAll('.dl-panel').forEach(p => p.hidden = true);
  document.querySelectorAll('.btn-dl').forEach(b => b.classList.remove('active'));

  if (!open) {{
    const data = LOGOS_DATA[slug] || {{}};
    panel.innerHTML = buildPanel(slug, data);
    panel.hidden = false;
    btn.classList.add('active');
  }}
}}

const FORMAT_ICONS = {{
  svg:     '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="12" height="10" rx="2"/><path d="M5 8h6M8 5v6"/></svg>',
  png:     '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="12" height="12" rx="2"/><path d="M2 11l3.5-4 2.5 3 2-2 4 4"/></svg>',
  ico:     '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="12" height="12" rx="2"/><path d="M8 5v6M6 7h4"/></svg>',
  palette: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="6"/><circle cx="5.5" cy="6.5" r="1"/><circle cx="10.5" cy="6.5" r="1"/><circle cx="8" cy="10.5" r="1"/></svg>',
}};

function buildPanel(slug, data) {{
  const files = data.files || {{}};
  const desc  = data.desc  || '';

  let links = '';
  for (const [fmt, path] of Object.entries(files)) {{
    const cls  = 'dl-link dl-link-' + fmt;
    const icon = FORMAT_ICONS[fmt] || '';
    links += `<a class="${{cls}}" href="${{path}}" download title="Download ${{path}}">${{icon}}${{fmt.toUpperCase()}}</a>`;
  }}

  return `
    ${{desc ? `<div class="dl-desc">${{desc}}</div>` : ''}}
    <div class="dl-links">${{links || '<span style="color:#555;font-size:.72rem">No files found</span>'}}</div>
  `;
}}

// Close panel when clicking outside a card
document.addEventListener('click', e => {{
  if (!e.target.closest('.card')) {{
    document.querySelectorAll('.dl-panel').forEach(p => p.hidden = true);
    document.querySelectorAll('.btn-dl').forEach(b => b.classList.remove('active'));
  }}
}});
</script>
</body>
</html>
'''


def main():
    with open(LOGOS_JSON, 'r', encoding='utf-8') as f:
        logos_data = json.load(f)

    cards = build_cards(logos_data)

    # Build JS-ready data object  {slug: {site, desc, files}}
    js_data = {}
    for c in cards:
        js_data[c['slug']] = {
            'site':  c['site'],
            'desc':  c['desc'],
            'files': c['files'],
        }

    total_logos  = len(cards)
    total_colors = sum(len(c['palette']) for c in cards)
    cards_html   = '\n'.join(card_html(c) for c in cards)
    logos_json   = json.dumps(js_data, indent=2)

    html = HTML_TEMPLATE.format(
        total_logos=total_logos,
        total_colors=total_colors,
        cards_html=cards_html,
        logos_json=logos_json,
    )

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Written: {OUT_FILE}")
    print(f"  {total_logos} logos, {total_colors} colors total")
    for c in cards:
        fmts = ', '.join(c['files'].keys())
        print(f"  [{c['slug']:20s}] site={c['site'][:40]}  files=[{fmts}]")


if __name__ == '__main__':
    main()
