"""SiYuan component mappings. Palette identity stays in targets/semantics.

Selectors were checked against SiYuan 3.8.9 desktop assets. No JavaScript,
font/layout overrides or plugin-specific selectors are shipped in the theme.
"""
import html
from .colors import contrast

DARK = "html[data-theme-mode='dark']"
EDITOR = '.protyle-wysiwyg'

# Semantic aliases consume existing target tokens rather than inflating budgets.
ROLES = {
    'document': 'background', 'panel': 'panel', 'raised': 'elevated',
    'body': 'foreground', 'heading': 'foreground', 'subheading': 'secondary',
    'minor_heading': 'type', 'metadata': 'muted', 'link': 'primary',
    'reference': 'secondary', 'code': 'constant', 'border': 'border',
    'selected': 'selection', 'selected_text': 'selection_text',
    'hover': 'primary_hover', 'pressed': 'primary_pressed',
    'warning': 'warning', 'error': 'error', 'success': 'success', 'info': 'info',
}
SYNTAX = {
    'keyword': 'keyword', 'selector-tag': 'keyword', 'meta': 'keyword',
    'string': 'string', 'regexp': 'string', 'addition': 'success',
    'number': 'number', 'literal': 'constant', 'symbol': 'constant',
    'built_in': 'type', 'type': 'type', 'title.class_': 'type',
    'title.function_': 'function', 'title': 'function',
    'attr': 'type', 'attribute': 'type', 'params': 'foreground',
    'variable': 'foreground', 'operator': 'operator', 'punctuation': 'muted',
    'comment': 'comment', 'quote': 'comment', 'doctag': 'info',
    'deletion': 'error', 'section': 'function', 'bullet': 'operator',
}


def refine_status(tokens, add):
    """Separate colliding states locally, without changing canonical hue families."""
    if tokens['warning']['hex'] == tokens['error']['hex']:
        add('error', 'error', 'SiYuan error distinguished from warning',
            lightness=min(.96, tokens['error']['oklch'][0] + .08), chroma=.65,
            minimum=4.5)


def role_tokens(tokens):
    aliases = {role: token if token in tokens else token.rsplit('_', 1)[0]
               for role, token in ROLES.items()}
    aliases['on_primary'] = max(('background', 'foreground'),
                               key=lambda key: contrast(tokens[key], tokens['primary']))
    return aliases


def component_rules():
    """Each colored component names its real surface for contrast validation."""
    return [
        ('.protyle-wysiwyg', 'body', 'document', ''),
        ('.layout__dockl, .layout__dockr, .layout__dockb', 'body', 'panel', ''),
        ('.b3-dialog__container, .b3-menu', 'body', 'raised', ''),
        (f'{EDITOR} [data-type="NodeHeading"].h1', 'heading', None, ''),
        (f'{EDITOR} [data-type="NodeHeading"].h2', 'subheading', None, ''),
        (f'{EDITOR} [data-type="NodeHeading"].h3', 'minor_heading', None, ''),
        (f'{EDITOR} [data-type="NodeHeading"].h4, {EDITOR} [data-type="NodeHeading"].h5, {EDITOR} [data-type="NodeHeading"].h6', 'metadata', None, ''),
        (f'{EDITOR} a, {EDITOR} [data-type~="a"]', 'link', None, ''),
        (f'{EDITOR} [data-type~="block-ref"], {EDITOR} [data-type~="file-annotation-ref"]', 'reference', None, ''),
        (f'{EDITOR} .protyle-attr, .protyle-background__tags, .protyle-breadcrumb', 'metadata', None, ''),
        ('.file-tree .b3-list-item', 'body', 'panel', ''),
        ('.file-tree [data-type="navigation-root"] > .b3-list-item__text', 'subheading', None, 'font-weight:600;'),
        ('.file-tree .b3-list-item__toggle, .file-tree .b3-list-item__meta', 'metadata', None, ''),
        ('.sy__file [data-type="navigation-file"]:not([data-count="0"]) > .b3-list-item__toggle', 'reference', None, ''),
        ('.file-tree .b3-list-item:hover', 'body', 'raised', ''),
        ('.file-tree .b3-list-item--focus, .file-tree .b3-list-item--focus:hover', 'selected_text', 'selected', 'box-shadow:inset 2px 0 var(--apt-siyuan-link);'),
        ('.file-tree .b3-list-item--focus > .b3-list-item__text, .file-tree .b3-list-item--focus > .b3-list-item__meta, .file-tree .b3-list-item--focus > .b3-list-item__toggle, .sy__file [data-type="navigation-file"].b3-list-item--focus > .b3-list-item__toggle', 'selected_text', None, ''),
        ('.layout-tab-bar .item', 'metadata', 'panel', ''),
        ('.layout-tab-bar .item:hover', 'body', 'raised', ''),
        ('.layout__wnd--active .layout-tab-bar .item--focus', 'selected_text', 'selected', 'box-shadow:inset 0 -2px var(--apt-siyuan-link);'),
        ('.toolbar, .dock', 'metadata', 'document', ''),
        ('.toolbar__item:hover, .dock__item:hover, .b3-menu__item:hover', 'hover', 'raised', ''),
        ('.toolbar__item:active, .dock__item:active, .b3-menu__item:active', 'pressed', 'raised', ''),
        ('.dock__item--active', 'link', 'raised', ''),
        ('.b3-text-field, .b3-select, .b3-button--outline', 'body', 'panel', 'border-color:var(--apt-siyuan-border);'),
        ('.b3-button:not(.b3-button--outline):not(.b3-button--cancel):not(.b3-button--text)', 'selected_text', 'selected', ''),
        ('.b3-button--outline:hover, .b3-button--cancel:hover, .b3-button--text:hover', 'hover', 'raised', ''),
        (f'{EDITOR} [data-type="NodeTable"] table', 'body', 'document', 'border-collapse:collapse;'),
        (f'{EDITOR} [data-type="NodeTable"] :is(td, th)', 'body', None, 'border-color:var(--apt-siyuan-border);padding:.5em .65em;overflow-wrap:anywhere;'),
        (f'{EDITOR} [data-type="NodeTable"] tbody tr:nth-child(even)', 'body', 'panel', ''),
        (f'{EDITOR} [data-type="NodeTable"] tbody tr:nth-child(odd)', 'body', 'document', ''),
        (f'{EDITOR} [data-type="NodeTable"] th', 'subheading', 'raised', 'font-weight:600;'),
        (f'{EDITOR} span[data-type~="code"], {EDITOR} code:not(.hljs)', 'code', 'panel', ''),
        (f'{EDITOR} [data-type="NodeCodeBlock"], {EDITOR} .hljs', 'body', 'panel', ''),
        (f'{EDITOR} .bq, {EDITOR} blockquote', 'body', 'panel', 'border-inline-start:3px solid var(--apt-siyuan-reference);'),
        (f'{EDITOR} .callout', 'body', 'raised', 'border-inline-start:3px solid var(--apt-siyuan-info);'),
        (f'{EDITOR} [data-type="NodeBlockQueryEmbed"]', 'body', 'panel', 'border-color:var(--apt-siyuan-border);'),
        (f'{EDITOR} .av', 'body', 'document', ''),
        (f'{EDITOR} .av__row--header', 'metadata', 'raised', ''),
        (f'{EDITOR} .av__gallery-item', 'body', 'panel', 'border-color:var(--apt-siyuan-border);'),
    ]


def mapping(tokens):
    aliases = role_tokens(tokens)
    records = []
    for selector, fg, bg, _ in component_rules():
        records.append({'selector': selector, 'foreground': aliases[fg],
                        'background': aliases[bg] if bg else 'inherited'})
    for cls, token in SYNTAX.items():
        records.append({'selector': f'{EDITOR} .hljs-{cls}',
                        'foreground': token + '_on_panel' if token + '_on_panel' in tokens else token,
                        'background': 'panel'})
    return {'schema': 'aptlantis.siyuan-mapping.v1', 'tested_selector_version': '3.8.9',
            'aliases': aliases, 'components': records,
            'status_collision': tokens['warning']['hex'] == tokens['error']['hex'],
            'native_application_acceptance': 'pending'}


def validate(result):
    """Check all declared foregrounds, including nested and selected surfaces."""
    tokens = result['tokens']
    on_primary = role_tokens(tokens)['on_primary']
    ratio = contrast(tokens[on_primary], tokens['primary'])
    result['checks'].append({'foreground': on_primary, 'background': 'primary',
        'selector': '--b3-theme-on-primary', 'ratio': ratio, 'required': 4.5,
        'pass': ratio + 1e-9 >= 4.5})
    # Inherited text may occur inside tables, quotes, cards, or raised dialogs.
    for record in mapping(tokens)['components']:
        surfaces = ('background', 'panel', 'elevated', 'selection') if 'item--focus' in record['selector'] or 'list-item--focus' in record['selector'] else ('background', 'panel', 'elevated')
        if record['background'] != 'inherited':
            surfaces = (record['background'],)
        for bg in surfaces:
            fg = record['foreground']
            ratio = contrast(tokens[fg], tokens[bg])
            result['checks'].append({'foreground': fg, 'background': bg,
                'selector': record['selector'], 'ratio': ratio, 'required': 4.5,
                'pass': ratio + 1e-9 >= 4.5})
    for fg in ('primary', 'border'):
        for bg in ('background', 'panel', 'elevated'):
            ratio = contrast(tokens[fg], tokens[bg])
            result['checks'].append({'foreground': fg, 'background': bg,
                'selector': 'focus indicator / component boundary', 'ratio': ratio,
                'required': 3, 'pass': ratio + 1e-9 >= 3})
    result['contrast_failures'] = sum(not c['pass'] for c in result['checks'])


def theme_css(tokens):
    aliases = role_tokens(tokens)
    css = DARK + ' {\n' + ''.join(f' --apt-siyuan-{role.replace("_", "-")}:var(--apt-{key.replace("_", "-")});\n' for role, key in aliases.items())
    native = {
        'theme-background': 'document', 'body-background': 'document', 'theme-surface': 'panel',
        'theme-surface-light': 'raised', 'theme-on-background': 'body',
        'theme-on-surface': 'metadata', 'theme-on-surface-light': 'metadata',
        'theme-on-surface-lighter': 'metadata', 'theme-primary': 'link',
        'theme-on-primary': 'on_primary', 'theme-primary-light': 'selected',
        'theme-primary-lighter': 'selected', 'theme-primary-lightest': 'selected',
        'theme-secondary': 'reference', 'theme-error': 'error', 'theme-success': 'success',
        'border-color': 'border', 'protyle-code-background': 'panel',
        'protyle-inline-code-color': 'code', 'protyle-inline-blockref-color': 'reference',
        'protyle-inline-link-color': 'link', 'protyle-inline-tag-color': 'metadata',
        'list-hover': 'raised', 'list-background': 'selected',
        'toolbar-color': 'metadata', 'toolbar-hover': 'raised',
        'menu-background': 'raised', 'menu-icon-color': 'metadata',
        'table-even-background': 'panel', 'protyle-code-linenumber-hl': 'metadata',
    }
    for status in ('warning', 'error', 'success', 'info'):
        native['card-' + status + '-color'] = status
        native['card-' + status + '-background'] = 'panel'
    css += ''.join(f' --b3-{key}:var(--apt-siyuan-{role.replace("_", "-")});\n' for key, role in native.items()) + '}\n'
    for selector, fg, bg, extra in component_rules():
        selectors = DARK + ' :is(' + selector + ')'
        css += selectors + ' { color:var(--apt-siyuan-' + fg.replace('_', '-') + ');'
        if bg:
            css += 'background-color:var(--apt-siyuan-' + bg.replace('_', '-') + ');'
        css += extra + '}\n'
    for record in mapping(tokens)['components'][len(component_rules()):]:
        css += DARK + ' ' + record['selector'] + ' { color:var(--apt-' + record['foreground'].replace('_', '-') + '); }\n'
    css += f'''{DARK} :is(.b3-text-field, .b3-select, .b3-button, .b3-menu__item, .toolbar__item, .dock__item):focus-visible,
{DARK} {EDITOR} :is(a, [data-type~="a"], [data-type~="block-ref"]):focus-visible {{ outline:2px solid var(--apt-siyuan-link);outline-offset:2px; }}
{DARK} {EDITOR} ::selection {{ background:var(--apt-siyuan-selected);color:var(--apt-siyuan-selected-text); }}
{DARK} {EDITOR} :is(a, [data-type~="a"]):hover {{ color:var(--apt-siyuan-hover); }}
{DARK} {EDITOR} :is(a, [data-type~="a"]):active {{ color:var(--apt-siyuan-pressed); }}
'''
    return css


def specimen(css, name):
    """Authored native-shaped fixtures, explicitly not a SiYuan screenshot."""
    geometry = '''
body { margin:0; font:14px/1.5 system-ui,sans-serif;background:var(--b3-theme-background,#fff);color:var(--b3-theme-on-background,#000); }
.specimen-note { padding:12px 20px;background:#18212a;color:#f0f0f0; }
.specimen { display:grid;grid-template-columns:210px minmax(0,1fr);min-height:900px; }
.specimen aside { padding:14px; } .specimen main { min-width:0;padding:20px; }
.b3-list-item { padding:7px 10px;list-style:none;display:flex;gap:8px;border-radius:4px; }
.b3-list-item__text { flex:1; } .layout-tab-bar { display:flex;gap:6px;margin-bottom:20px; }
.layout-tab-bar .item,.toolbar__item,.dock__item,.b3-menu__item { padding:7px 12px;border-radius:4px; }
.protyle-wysiwyg [data-type="NodeHeading"] { margin:16px 0 8px;font-weight:600; }
.h1 { font-size:28px; } .h2 { font-size:23px; } .h3 { font-size:19px; }
.protyle-wysiwyg p { margin:12px 0; }
.protyle-wysiwyg table { width:100%; } .protyle-wysiwyg td,.protyle-wysiwyg th { border:1px solid;padding:6px;text-align:left; }
.protyle-wysiwyg .bq,.callout,[data-type="NodeBlockQueryEmbed"],.av__gallery-item { margin:14px 0;padding:12px;border:1px solid; }
.protyle-wysiwyg pre { padding:14px;white-space:pre-wrap;overflow-wrap:anywhere; }
.b3-text-field,.b3-button { padding:8px;margin:6px 6px 6px 0; }
.av__row { display:flex;gap:20px;padding:8px; } .av__gallery-item { max-width:340px; }
.b3-dialog__container,.b3-menu { padding:12px;margin-top:14px; }
.specimen-unrelated { color:rgb(1,2,3);background:rgb(244,245,246);padding:10px; }
@media(max-width:700px) { .specimen { grid-template-columns:140px minmax(0,1fr); } .specimen main { padding:10px; } }
'''
    body = '''<div class="specimen"><aside class="layout__dockl file-tree sy__file">
<strong>Documents</strong><ul class="b3-list b3-list--background">
<li class="b3-list-item" data-type="navigation-root"><span class="b3-list-item__text">City Hall</span></li>
<li class="b3-list-item" data-type="navigation-file" data-count="3"><span class="b3-list-item__toggle">›</span><span class="b3-list-item__text">Standards</span></li>
<li class="b3-list-item" id="tree-hover" data-type="navigation-file" data-count="0"><span class="b3-list-item__text">Adoption guide</span></li>
<li class="b3-list-item b3-list-item--focus" id="tree-selected" data-type="navigation-file" data-count="3"><span class="b3-list-item__toggle">›</span><span class="b3-list-item__text">Overview</span><span class="b3-list-item__meta">3</span></li></ul>
<div class="dock"><button class="dock__item dock__item--active">Files</button></div>
<div class="b3-menu"><div class="b3-menu__item" tabindex="0">Open reference</div></div></aside>
<main class="layout__wnd--active"><div class="layout-tab-bar"><div class="item">Schema reference</div><div class="item item--focus">Overview</div></div>
<div class="toolbar"><button class="toolbar__item" id="toolbar-hover">Document actions</button></div>
<article class="protyle-wysiwyg">
<div class="h1" data-type="NodeHeading">Workspace Governance</div>
<p>The governance standard defines how projects, standards, and shared services relate to the workspace.</p>
<div class="protyle-attr">Candidate v0.2.7 · implementation metadata</div>
<div class="h2" data-type="NodeHeading">Document suite</div>
<p><a id="reference-link" href="#details">Read the adoption guide</a> · <span data-type="block-ref">Governance reference</span> · <span data-type="code">WGS.manifest.toml</span></p>
<div data-type="NodeTable"><table><thead><tr><th>File</th><th>Purpose</th></tr></thead><tbody>
<tr><td><span data-type="code">Workspace-Governance-Standard.md</span></td><td>Primary specification</td></tr>
<tr><td>Manifest conventions</td><td>Machine-readable records</td></tr>
<tr><td style="text-align:right">32</td><td>Preserved canonical colors</td></tr>
<tr><td>Source identity and provenance</td><td>Verified recovery evidence</td></tr></tbody></table></div>
<div class="h3" data-type="NodeHeading">Implementation note</div>
<div class="bq">Agent orientation begins with inherited instructions and workspace manifests.</div>
<div class="callout">Information: repository Markdown remains authoritative.</div>
<div data-type="NodeCodeBlock"><pre class="hljs"><span class="hljs-comment">// Preserve canonical identity</span>
<span class="hljs-keyword">const</span> <span class="hljs-title function_">validate</span> = (<span class="hljs-params">palette</span>) =&gt; <span class="hljs-number">32</span>;
<span class="hljs-attr">name</span>: <span class="hljs-string">"Aptlantis"</span>, <span class="hljs-literal">true</span>, <span class="hljs-type">Theme</span>
<span class="hljs-addition">+ preserved</span> <span class="hljs-deletion">- invalid</span></pre></div>
<div data-type="NodeBlockQueryEmbed">Embedded reference · document preview</div>
<div class="av"><div class="av__row av__row--header">Standard　 Version　 Lifecycle</div><div class="av__row">WGS　 v0.2.7　 Active Core</div>
<div class="av__gallery-item"><strong>Workspace Governance</strong><p>Active Core</p><span class="protyle-attr">Version v0.2.7</span></div></div>
<div class="h4" data-type="NodeHeading" id="details">Supporting details</div>
<p><span style="color:#AABBCC" id="explicit-color">User-selected text color</span></p></article>
<div class="b3-dialog__container"><label>Find document <input class="b3-text-field" id="focus-input" value="Governance"></label><button class="b3-button b3-button--outline">Search</button><button class="b3-button">Apply</button></div>
<section class="specimen-unrelated"><button id="unrelated-button">Unrelated plugin control</button><input id="unrelated-input" value="Unrelated input"><table><tr><th id="unrelated-heading">Unrelated table</th></tr></table></section>
</main></div>'''
    return '<!doctype html><html data-theme-mode="dark"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + html.escape(name) + '</title><style>' + geometry + '</style><style id="theme">' + css + '</style><body><div class="specimen-note">' + html.escape(name) + ' · Authored browser specimen; native SiYuan acceptance pending.</div>' + body + '</body></html>'
