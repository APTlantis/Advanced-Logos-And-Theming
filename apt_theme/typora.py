"""Typora native CSS and paired offline Markdown/browser specimens.

No Markdown parser or browser framework is used: the paired specimens are
authored together, and the HTML is a simulation, not Typora's live renderer.
"""
import html


def theme_css(tokens):
    css = """:root {
 --bg-color:var(--apt-background); --text-color:var(--apt-foreground);
 --side-bar-bg-color:var(--apt-panel); --control-text-color:var(--apt-foreground);
 --md-char-color:var(--apt-muted); --meta-content-color:var(--apt-muted);
 --monospace: Consolas, 'Liberation Mono', monospace;
}
html, body { background:var(--apt-background); color:var(--apt-foreground); }
#write { box-sizing:border-box; max-width:900px; margin:auto; padding:2rem;
 line-height:1.65; overflow-wrap:anywhere; }
#typora-sidebar { background:var(--apt-panel); color:var(--apt-foreground); }
.modal-content, .dropdown-menu { background:var(--apt-elevated); color:var(--apt-foreground); }
#write h1, #write h2, #write h3, #write h4, #write h5, #write h6 {
 color:var(--apt-primary); line-height:1.3; margin:1.6em 0 .65em; font-weight:600; }
#write h1 { font-size:2rem; } #write h2 { font-size:1.65rem; }
#write h3 { font-size:1.35rem; } #write h4 { font-size:1.15rem; }
#write h5 { font-size:1rem; } #write h6 { font-size:.95rem; }
#write p { margin:.8em 0; }
#write ul, #write ol { padding-left:1.8em; margin:.8em 0; }
#write li > ul, #write li > ol { margin:.25em 0; }
#write li > p { margin:.35em 0; }
#write .task-list-item { list-style:none; }
#write .task-list-item input { accent-color:var(--apt-primary); margin-right:.5em; }
#write blockquote { margin:1em 0; padding:.25em 1em; background:var(--apt-panel);
 border-left:3px solid var(--apt-primary); color:var(--apt-foreground); }
#write hr { border:0; border-top:1px solid var(--apt-border); margin:1.8em 0; }
#write table { border-collapse:collapse; width:100%; margin:1.2em 0;
 background:var(--apt-background); color:var(--apt-foreground); }
#write th, #write td { border:1px solid var(--apt-border); padding:.55em .7em;
 vertical-align:top; overflow-wrap:anywhere; }
#write thead th { background:var(--apt-elevated); font-weight:600; }
#write tbody tr:nth-child(even) { background:var(--apt-panel); }
#write tbody tr:nth-child(odd) { background:var(--apt-background); }
#write code { font-family:var(--monospace); font-size:.92em;
 background:var(--apt-panel); color:var(--apt-foreground); padding:.12em .3em; border-radius:.2em; }
#write pre, #write .md-fences { background:var(--apt-panel); color:var(--apt-foreground);
 padding:1em; border-radius:.3em; overflow-x:auto; }
#write pre code { padding:0; border-radius:0; }
#write .CodeMirror { background:var(--apt-panel); color:var(--apt-foreground); }
#write a { color:var(--apt-primary); text-decoration:underline; text-underline-offset:.15em; }
#write a:focus-visible { outline:2px solid var(--apt-primary); outline-offset:2px; }
#write strong { font-weight:700; } #write em { font-style:italic; }
#write mark { background:var(--apt-selection); color:var(--apt-selection-text); padding:.1em .2em; }
#write .md-def-footnote, #write .footnotes { font-size:.9em; color:var(--apt-muted); }
#write .md-toc { padding:.7em 1em; background:var(--apt-panel); }
#write img { max-width:100%; height:auto; }
#write ::selection { background:var(--apt-selection); color:var(--apt-selection-text); }
@media screen and (max-width:600px) { #write { padding:1rem; }
 #write th, #write td { padding:.35em .2em; } }
"""
    mapping = {'keyword': 'keyword', 'string': 'string', 'number': 'number',
               'comment': 'comment', 'def': 'function', 'operator': 'operator',
               'variable-2': 'type', 'atom': 'constant'}
    for cls, role in mapping.items():
        css += f"#write .cm-s-inner .cm-{cls} {{ color:var(--apt-{role}); }}\n"
    for role in ('keyword', 'string', 'number', 'function', 'type', 'operator', 'constant', 'comment'):
        css += f"#write .hljs-{role} {{ color:var(--apt-{role}); }}\n"
    for state, pseudo in (('hover', ':hover'), ('pressed', ':active')):
        key = 'primary_' + state
        if key in tokens:
            css += f"#write a{pseudo} {{ color:var(--apt-{key.replace('_', '-')}); }}\n"
    return css


def specimens(name):
    md, body = [], []
    def add(markdown, markup):
        md.append(markdown)
        body.append(markup)
    add('# Markdown stress test', '<h1>Markdown stress test</h1>')
    add(f'{name}: illustrative fixtures. Native Typora review remains pending.',
        f'<p>{html.escape(name)}: browser simulation using exported CSS. Native Typora review remains pending.</p>')
    add('[TOC]', '<nav class="md-toc" aria-label="Table of contents"><a href="#tables">Tables</a> · <a href="#structures">Structures</a></nav>')
    add('## Tables', '<h2 id="tables">Tables</h2>')
    def table(label, headers, rows, align=None, table_id=''):
        align = align or ['left'] * len(headers)
        separator = {'left': ':---', 'center': ':---:', 'right': '---:'}
        source = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(separator[a] for a in align) + ' |']
        source += ['| ' + ' | '.join(row) + ' |' for row in rows]
        def cells(row, tag):
            return ''.join(f'<{tag} style="text-align:{a}">{value}</{tag}>' for a, value in zip(align, row))
        rendered = f'<h3>{label}</h3><table id="{table_id}"><thead><tr>{cells(headers, "th")}</tr></thead><tbody>'
        rendered += ''.join('<tr>' + cells(row, 'td') + '</tr>' for row in rows) + '</tbody></table>'
        add('### ' + label + '\n\n' + '\n'.join(source), rendered)
    table('Alignment', ['Left', 'Center', 'Right'], [['Alpha', 'Beta', '123'], ['Gamma', 'Delta', '456']],
          ['left', 'center', 'right'], 'alignment')
    long_url = 'https://example.invalid/' + 'long-reference-' * 12
    table('Long content', ['Item', 'Description'], [['URL', long_url], ['Formatting', '**Bold**, *italic*, `code`']], table_id='long-content')
    # HTML inline formatting corresponds to the authored Markdown fixture.
    body[-1] = body[-1].replace('**Bold**, *italic*, `code`', '<strong>Bold</strong>, <em>italic</em>, <code>code</code>')
    table('Tall table: 100 rows', ['Row', 'Name', 'Value'],
          [[str(i), f'Sample {i:03}', str(i * 7)] for i in range(1, 101)], table_id='tall')
    table('Wide table: 12 columns', [f'C{i}' for i in range(1, 13)],
          [[str(i * j) for j in range(1, 13)] for i in range(1, 9)], table_id='wide')
    add('## Structures', '<h2 id="structures">Structures</h2>')
    for level in range(3, 7):
        add('#' * level + f' Heading level {level}', f'<h{level}>Heading level {level}</h{level}>')
    add('Paragraph with **strong**, *emphasis*, ~~deleted~~, ==highlight== and `inline code`.\n\nA second paragraph with a [local link](#tables) and footnote.[^1]',
        '<p>Paragraph with <strong>strong</strong>, <em>emphasis</em>, <del>deleted</del>, <mark>highlight</mark> and <code>inline code</code>.</p><p>A second paragraph with a <a href="#tables">local link</a> and footnote.<sup><a href="#footnote-1">1</a></sup></p>')
    add('- First item\n  - Nested item\n    1. Ordered child\n- Second item\n\n1. Ordered item\n2. Another item',
        '<ul><li>First item<ul><li>Nested item<ol><li>Ordered child</li></ol></li></ul></li><li>Second item</li></ul><ol><li>Ordered item</li><li>Another item</li></ol>')
    add('- [ ] Pending task\n- [x] Completed task', '<ul class="task-list"><li class="task-list-item"><label><input type="checkbox">Pending task</label></li><li class="task-list-item"><label><input type="checkbox" checked>Completed task</label></li></ul>')
    add('> A quotation with a [link](#tables).\n>\n> > A nested quotation.', '<blockquote><p>A quotation with a <a href="#tables">link</a>.</p><blockquote><p>A nested quotation.</p></blockquote></blockquote>')
    add('---', '<hr>')
    add('```python\n# Example only\ndef answer():\n    return "gold", 32\n```', '<pre class="md-fences cm-s-inner"><code><span class="cm-comment"># Example only</span>\n<span class="cm-keyword">def</span> <span class="cm-def">answer</span>():\n    <span class="cm-keyword">return</span> <span class="cm-string">"gold"</span>, <span class="cm-number">32</span></code></pre>')
    add('![Local palette swatch](example-image.png)', '<p><img src="example-image.png" alt="Local palette swatch"></p>')
    add('[^1]: Footnote text with a [return link](#structures).', '<div class="md-def-footnote" id="footnote-1"><p>1: Footnote text with a <a href="#structures">return link</a>.</p></div>')
    return '\n\n'.join(md) + '\n', '\n'.join(body)


def export_examples(result, directory, name, css_filename):
    from .report import swatch
    markdown, markup = specimens(name)
    (directory / 'examples.md').write_text(markdown, encoding='utf-8')
    document = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>{html.escape(name)} — Typora browser simulation</title>'
                f'<link rel="stylesheet" href="{html.escape(css_filename, quote=True)}">'
                '</head><body><main id="write">' + markup + '</main></body></html>')
    (directory / 'examples.html').write_text(document, encoding='utf-8')
    swatch({k: result['tokens'][k] for k in ('background', 'panel', 'elevated', 'primary')},
           directory / 'example-image.png', 'Local theme surfaces and accent')
    result['examples'] = ['examples.html', 'examples.md']
