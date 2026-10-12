"""Dark, scoped browser CSS contract and offline website review specimens."""
import html
from .colors import contrast

SURFACES = {'nav': .18, 'hero': .22, 'card': .24, 'input': .16,
            'dialog': .28, 'table': .20, 'footer': .14}
ACTIONS = ('primary', 'secondary')
STATES = {'rest': .27, 'hover': .32, 'pressed': .22, 'disabled': .20}
STATUSES = ('success', 'warning', 'error', 'info')
LIMITS = ('Scoped .apt-site CSS custom properties and opt-in .apt-* components; '
          'opaque dark surfaces. Preview interactions are illustrative. Existing framework '
          'integration, screen-reader review, CVD/category separation and production acceptance '
          'require separate review. Status labels remain necessary when source hues alias.')


def extend(tokens, checks, add):
    for surface, lightness in SURFACES.items():
        bg = surface + '_bg'
        add(bg, 'background', surface + ' surface', lightness=lightness, chroma=.45)
        for suffix, role, minimum in (('text', 'foreground', 4.5), ('muted', 'muted', 4.5),
                                      ('border', 'muted', 3)):
            add(surface + '_' + suffix, role, surface + ' ' + suffix, minimum=minimum, bg=bg)
    for action in ACTIONS:
        for state, lightness in STATES.items():
            key = action + '_' + state
            add(key + '_bg', action, key + ' fill', lightness=lightness, chroma=.8)
            add(key + '_text', 'foreground', key + ' label', minimum=4.5, bg=key + '_bg')
            add(key + '_border', action, key + ' boundary', minimum=3, bg=key + '_bg')
    for status in STATUSES:
        add(status + '_bg', status, status + ' message fill', lightness=.20, chroma=.4)
        add(status + '_text', status, status + ' message text', minimum=4.5, bg=status + '_bg')
        add(status + '_border', status, status + ' message boundary', minimum=3, bg=status + '_bg')
    # Links/focus may appear on any of the contract's surfaces, including actions.
    backgrounds = ['background', 'panel', 'elevated'] + [k for k in tokens if k.endswith('_bg')]
    brightest = max(backgrounds, key=lambda key: contrast(tokens[key], {'hex': '#000000'}))
    add('primary', 'primary', 'link text across website surfaces', minimum=4.5, bg=brightest)
    for name in [key for key in tokens if key.endswith('_border')]:
        family = name.split('_')[0]
        role = family if family in (*ACTIONS, *STATUSES) else 'muted'
        add(name, role, name.replace('_', ' '), minimum=3, bg=brightest)
    for name, role in (('link_hover', 'primary'), ('link_visited', 'secondary'), ('focus', 'primary')):
        add(name, role, name.replace('_', ' '), minimum=4.5 if name != 'focus' else 3, bg=brightest)
    for fg in ('primary', 'link_hover', 'link_visited', 'focus'):
        for bg in backgrounds:
            minimum = 3 if fg == 'focus' else 4.5
            ratio = contrast(tokens[fg], tokens[bg])
            checks.append({'foreground': fg, 'background': bg, 'ratio': ratio,
                           'required': minimum, 'pass': ratio >= minimum})
    # Visible control boundaries must separate from their surrounding surface too.
    for fg in [k for k in tokens if k.endswith('_border')]:
        for bg in ('background', 'panel', 'elevated'):
            ratio = contrast(tokens[fg], tokens[bg])
            checks.append({'foreground': fg, 'background': bg, 'ratio': ratio,
                           'required': 3, 'pass': ratio >= 3})
    # Updating a shared token above must also refresh its earlier recorded ratios.
    for check in checks:
        check['ratio'] = contrast(tokens[check['foreground']], tokens[check['background']])
        check['pass'] = check['ratio'] >= check['required']


def website_css(tokens):
    variables = '.apt-site {\n  color-scheme: dark;\n' + ''.join(
        f"  --apt-{key.replace('_', '-')}: {value['hex']};\n" for key, value in tokens.items()) + '}\n'
    css = variables + """
.apt-site{background:var(--apt-background);color:var(--apt-foreground);font:16px/1.65 system-ui,sans-serif;margin:0;overflow-wrap:anywhere}
.apt-site *{box-sizing:border-box}.apt-site .apt-wrap{max-width:1160px;margin:auto;padding:clamp(18px,4vw,48px)}
.apt-site h1,.apt-site h2,.apt-site h3{line-height:1.15;letter-spacing:-.025em}.apt-site h1{font-size:clamp(2.3rem,6vw,4.6rem);max-width:15ch;margin:.3em 0}
.apt-site .apt-eyebrow{text-transform:uppercase;letter-spacing:.18em;font-size:.75rem;color:var(--apt-secondary)}
.apt-site a{color:var(--apt-primary);text-underline-offset:4px}.apt-site a:visited{color:var(--apt-link-visited)}.apt-site a:hover{color:var(--apt-link-hover)}
.apt-site :focus-visible{outline:3px solid var(--apt-focus);outline-offset:4px}
.apt-site ::selection{background:var(--apt-selection);color:var(--apt-selection-text)}
.apt-site .apt-row{display:flex;gap:16px;flex-wrap:wrap;align-items:center;justify-content:space-between}
.apt-site .apt-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:22px}
.apt-site .apt-muted{color:var(--apt-muted)}.apt-site .apt-metric{font-size:2.4rem;font-weight:650;display:block}
.apt-site .apt-panel{background:var(--apt-panel);padding:24px}.apt-site .apt-elevated{background:var(--apt-elevated);padding:24px}
.apt-site .apt-button{display:inline-flex;align-items:center;justify-content:center;font:inherit;font-weight:650;padding:11px 20px;border:1px solid;border-radius:8px;cursor:pointer;text-decoration:none}
.apt-site .apt-button:disabled{cursor:not-allowed}.apt-site input,.apt-site textarea,.apt-site select{font:inherit;border:1px solid var(--apt-input-border);border-radius:6px;padding:10px 12px;width:100%;background:var(--apt-input-bg);color:var(--apt-input-text)}
.apt-site input::placeholder,.apt-site textarea::placeholder{color:var(--apt-input-muted)}.apt-site label{display:block;margin:16px 0 6px}.apt-site input[type=checkbox]{width:auto;accent-color:var(--apt-primary)}
.apt-site .apt-scroll{overflow:auto}.apt-site table{border-collapse:collapse;width:100%;min-width:500px}.apt-site td,.apt-site th{text-align:left;border-bottom:1px solid var(--apt-table-border);padding:12px}
.apt-site details{border:1px solid var(--apt-border);border-radius:8px;padding:16px;margin:14px 0}.apt-site summary{cursor:pointer;font-weight:650}
.apt-site pre{background:var(--apt-panel);color:var(--apt-foreground);padding:20px;overflow:auto}.apt-site code{font-family:ui-monospace,monospace}
.apt-site dialog{max-width:min(580px,90vw);border-radius:12px;padding:28px}.apt-site dialog::backdrop{background:var(--apt-background);opacity:.8}
.apt-site .apt-message{padding:16px 20px;border-left:4px solid;margin:14px 0;border-radius:4px}
.apt-site .apt-card{padding:24px;border:1px solid;border-radius:12px}.apt-site .apt-nav{border-bottom:1px solid;padding:20px clamp(18px,4vw,48px)}
.apt-site .apt-footer{padding:32px clamp(18px,4vw,48px);border-top:1px solid}.apt-site .apt-hero{border-bottom:1px solid}
"""
    for surface in SURFACES:
        css += f'.apt-site .apt-{surface}{{background:var(--apt-{surface}-bg);color:var(--apt-{surface}-text);border-color:var(--apt-{surface}-border)}}\n'
        css += f'.apt-site .apt-{surface} .apt-muted{{color:var(--apt-{surface}-muted)}}\n'
    for action in ACTIONS:
        for state, selector in (('rest', ''), ('hover', ':hover:not(:disabled)'),
                                ('pressed', ':active:not(:disabled)'), ('disabled', ':disabled')):
            prefix = action + '-' + state
            css += f'.apt-site .apt-button.apt-{action}{selector},.apt-site .apt-button.apt-{action}[data-state="{state}"]{{background:var(--apt-{prefix}-bg);color:var(--apt-{prefix}-text);border-color:var(--apt-{prefix}-border)}}\n'
    for status in STATUSES:
        css += f'.apt-site .apt-message.apt-{status}{{background:var(--apt-{status}-bg);color:var(--apt-{status}-text);border-color:var(--apt-{status}-border)}}\n'
        css += f'.apt-site .apt-text-{status}{{color:var(--apt-{status})}}\n'
    for role in ('keyword', 'string', 'number', 'function', 'type', 'operator', 'constant', 'comment'):
        css += f'.apt-site .apt-code-{role}{{color:var(--apt-{role})}}\n'
    return css


def export_website(result, directory, name):
    (directory / 'theme.css').write_text(website_css(result['tokens']), encoding='utf-8')
    result['examples'] = ['landing.html', 'components.html']
    result['acceptance_limits'] = LIMITS
    title = html.escape(name)
    head = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    nav = '<nav class="apt-nav apt-row" aria-label="Main"><strong>'+title+'</strong><div class="apt-row"><a href="landing.html">Overview</a><a href="components.html">Components</a><a href="examples.html">Theme review</a></div></nav>'
    script = '<script>document.querySelectorAll("[data-open-dialog]").forEach(b=>b.addEventListener("click",()=>document.querySelector("dialog").showModal()));document.querySelector("[data-close-dialog]")?.addEventListener("click",()=>document.querySelector("dialog").close());</script>'
    def save(file, content):
        (directory / file).write_text(head+'<title>'+title+' / '+file.split('.')[0]+'</title><link rel="stylesheet" href="theme.css"><body class="apt-site">'+nav+content+'<footer class="apt-footer">'+title+' · Illustrative local website theme specimen</footer>'+script+'</body></html>', encoding='utf-8')
    cards = ''.join('<article class="apt-card"><p class="apt-eyebrow">'+label+'</p><h3>'+heading+'</h3><p class="apt-muted">'+copy+'</p><a href="components.html">Explore components →</a></article>' for label, heading, copy in (
        ('01 / Discover', 'An identity worth exploring', 'Keep the source character across practical website surfaces.'),
        ('02 / Build', 'Make content readable', 'Cards, controls and text use shades with recorded source provenance.'),
        ('03 / Review', 'Choose where it belongs', 'A palette can suit one output and remain unsuitable for another.')))
    save('landing.html', '<header class="apt-hero"><div class="apt-wrap"><p class="apt-eyebrow">Artwork to interface</p><h1>A place for ideas to take shape.</h1><p class="apt-muted">A complete dark website specimen, built from '+title+'. Explore the visual identity across real content and controls.</p><div class="apt-row" style="justify-content:flex-start"><a class="apt-button apt-primary" href="components.html">Explore the theme</a><a class="apt-button apt-secondary" href="#collection">View collection</a></div></div></header><main class="apt-wrap"><section id="collection"><h2>From source to experience</h2><div class="apt-grid">'+cards+'</div></section><section style="margin-top:48px"><div class="apt-grid"><div class="apt-panel"><span class="apt-metric">32</span>Unchanged source colors</div><div class="apt-elevated"><span class="apt-metric">'+str(result['named_count'])+'</span>Website tokens</div><div class="apt-panel"><span class="apt-metric">'+str(result['contrast_failures'])+'</span>Declared contrast failures</div></div></section><section style="margin-top:48px"><h2>Questions worth asking</h2><details><summary>Does every image need to work here?</summary><p>No. Review the website separately from editor, presentation and chart outputs.</p></details><details><summary>What was extended?</summary><p>Target-specific lightness and chroma variants; the canonical palette is unchanged.</p></details></section></main>')
    buttons = ''.join('<div><h3>'+action.title()+'</h3><div class="apt-row" style="justify-content:flex-start">'+''.join('<button type="button" class="apt-button apt-'+action+'" data-state="'+state+'"'+(' disabled' if state == 'disabled' else '')+'>'+state.title()+'</button>' for state in STATES)+'</div></div>' for action in ACTIONS)
    messages = ''.join('<div class="apt-message apt-'+status+'"><strong>'+status.title()+': </strong>'+copy+'</div>' for status, copy in (
        ('success','Your draft is saved.'),('warning','Review the missing source hues before using status colors.'),
        ('error','This example needs your attention.'),('info','Labels carry meaning even when colors overlap.')))
    code = ' '.join('<span class="apt-code-'+role+'">'+html.escape(text)+'</span>' for role, text in (
        ('keyword','const'),('type','Palette'),('operator','='),('function','extend'),('string','"Source identity"'),('number','32'),('constant','DARK_ONLY'),('comment','// preserved canonical colors')))
    save('components.html', '<main class="apt-wrap"><p class="apt-eyebrow">Component review</p><h1>Test the everyday details.</h1><p>Hover, tab through controls, open the dialog and inspect the labeled states.</p><section><h2>Actions and states</h2>'+buttons+'</section><section><h2>Messages</h2>'+messages+'</section><section class="apt-grid"><div class="apt-card"><h2>Draft a collection</h2><form onsubmit="event.preventDefault()"><label for="name">Collection name</label><input id="name" placeholder="Give your collection a name"><label for="category">Category</label><select id="category"><option>Artwork</option><option>Documentation</option></select><label for="notes">Notes</label><textarea id="notes" rows="3" placeholder="What suits this palette?"></textarea><label><input type="checkbox"> Keep this draft local</label><button type="submit" class="apt-button apt-primary">Save draft (demo)</button></form></div><div class="apt-card"><h2>Reading and selection</h2><p>Primary body text stays legible on each surface. <a href="#table">Inspect the collection table</a>.</p><p class="apt-muted">Secondary text carries context without becoming decorative noise.</p><blockquote>Select this paragraph to check selected text.</blockquote><button type="button" class="apt-button apt-secondary" data-open-dialog>Open dialog</button><pre><code>'+code+'</code></pre></div></section><section id="table"><h2>Collection</h2><div class="apt-scroll apt-table"><table><thead><tr><th>Name</th><th>Use</th><th>Review</th></tr></thead><tbody><tr><td>Source artwork</td><td>Identity</td><td>Preserved</td></tr><tr><td>Website specimen</td><td>Browser CSS</td><td>Operator review</td></tr><tr><td>Original palette</td><td>Canonical 32</td><td>Unchanged</td></tr></tbody></table></div></section><dialog class="apt-dialog" aria-labelledby="dialog-title"><h2 id="dialog-title">Keep the source identity.</h2><p class="apt-muted">This native HTML dialog demonstrates the raised surface and keyboard focus. No data is saved.</p><button type="button" class="apt-button apt-primary" data-close-dialog>Close dialog</button></dialog></main>')
    gallery = head+'<title>'+title+' / website review</title><style>body{background:#181a1d;color:#eceef0;font:16px/1.6 system-ui;margin:32px auto;max-width:1000px;padding:20px}a{color:#dce1e6}li{margin:14px 0}</style><h1>'+title+' / website</h1><p>'+html.escape(LIMITS)+'</p><p>'+str(result['named_count'])+' named tokens / '+str(result['unique_count'])+' unique colors / '+str(result['contrast_failures'])+' declared contrast failures. Visual suitability remains your judgment.</p><ul><li><a href="landing.html">Landing page</a></li><li><a href="components.html">Component and interaction review</a></li><li><a href="theme.css" download>Download browser theme CSS</a></li><li><a href="tokens.json">Tokens and contrast findings</a></li></ul>'
    (directory / 'examples.html').write_text(gallery, encoding='utf-8')
    (directory / 'README.md').write_text('# '+name+' website theme\n\nLoad theme.css and place apt-site on the body or containing element. Components opt in with apt-* classes; landing.html and components.html document the DOM contract. The .apt-site namespace avoids styling an unrelated host page.\n\n'+LIMITS+'\n\nNo framework adapter, installation, activation or publication is performed. Generated previews are illustrative and forms save no data.\n', encoding='utf-8')
