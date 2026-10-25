"""Portable document and native CodeMirror 5/6 exports, with real offline previews."""
import hashlib
import html
import json
import shutil
from pathlib import Path

VENDOR = Path(__file__).parent / 'vendor/browser-themes'
TARGETS = ('markdown', 'codemirror5', 'codemirror6')
SYNTAX = {'keyword':'keyword','string':'string','number':'number','comment':'comment',
          'def':'function','type':'type','operator':'operator','atom':'constant',
          'tag':'tag','attribute':'attribute','property':'property','variable':'variable',
          'meta':'meta','link':'link','header':'heading','em':'emphasis','strong':'strong',
          'error':'invalid','positive':'inserted','negative':'deleted'}
SAMPLES = {'markdown':'# Markdown source\n\n**Strong**, *emphasis* and [a link](https://example.org).\n\n- [x] Checked task\n- [ ] Open task\n\n```python\ndef answer():\n    return 42\n```',
           'javascript':'// Search for answer; try Ctrl-Space and Ctrl-F\nfunction answer(value = 42) {\n  return "answer: " + value;\n}\nconsole.log(answer());\n',
           'python':'# Search for answer; try Ctrl-Space and Ctrl-F\ndef answer(value=42):\n    return "answer: " + str(value)\n\nprint(answer())\n'}
def markdown_specimen(artifact):
    return f'''# Portable Markdown theme

A real GFM rendering with **strong**, *emphasis*, ~~deleted text~~, `inline code`,
a [keyboard-focusable link](https://example.org), and https://example.org/autolink.

## Lists and tasks

- Parent
  - Nested child
    1. Ordered grandchild
- [x] Completed task
- [ ] Open task

> A quotation with **emphasis**.
>
> > A nested quotation.

### Tables

| Left | Center | Right |
| :--- | :---: | ---: |
| Alpha | Beta | 123 |
| Second | Stripe | 456 |

```javascript
// Actual offline Prism highlighting
function answer(value = 42) {{
  return "answer: " + value;
}}
```

```python
def answer():
    return "gold", 32
```

#### Heading four
##### Heading five
###### Heading six

---

![Local example]({artifact('example-image.svg')})

<details><summary>Disclosure</summary>Keyboard: <kbd>Ctrl</kbd> + <kbd>F</kbd>.
Subscript H<sub>2</sub>O and superscript x<sup>2</sup>.</details>

<script>window.unsafeMarkdownExecuted = true</script>
<img src="{artifact('example-image.svg')}" onerror="window.unsafeMarkdownExecuted = true">
<a href="javascript:alert(1)">Unsafe URL becomes harmless text</a>
'''


def verify_vendor():
    manifest = json.loads((VENDOR / 'manifest.json').read_text(encoding='utf-8'))
    for record in manifest['files']:
        if hashlib.sha256((VENDOR / record['file']).read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Browser theme asset hash mismatch: ' + record['file'])
    return manifest


def extend(tokens, checks, add):
    """Consumed document/editor roles; 40 is a ceiling, not a filler quota."""
    add('selection','selection','selected editor/document surface',lightness=.24,chroma=.55)
    add('cursor','primary','editor caret',minimum=3)
    add('active_line','background','active editor line',lightness=tokens['panel']['oklch'][0],chroma=.7)
    add('search_match','selection','search match surface',lightness=.24,chroma=.55)
    add('search_text','foreground','search match text',minimum=4.5,bg='search_match')
    mapping = {'matching_bracket':'primary','invalid':'error','link':'primary','tag':'keyword',
               'attribute':'type','property':'foreground','variable':'foreground','meta':'muted',
               'heading':'primary','emphasis':'foreground','strong':'foreground',
               'inserted':'success','deleted':'error'}
    for key, role in mapping.items():
        add(key,role,key.replace('_',' ')+' text',minimum=4.5)
    from .colors import contrast
    for fg in ('foreground','muted',*dict.fromkeys(SYNTAX.values())):
        for bg in ('panel','elevated','active_line','selection','search_match'):
            ratio = contrast(tokens[fg],tokens[bg])
            checks.append(dict(foreground=fg,background=bg,ratio=ratio,required=4.5,pass_=ratio>=4.5))
            checks[-1]['pass'] = checks[-1].pop('pass_')
    for check in checks:
        ratio = contrast(tokens[check['foreground']],tokens[check['background']])
        check.update(ratio=ratio, **{'pass':ratio>=check['required']})
    for bg in ('panel','elevated'):
        ratio = contrast(tokens['cursor'],tokens[bg])
        checks.append(dict(foreground='cursor',background=bg,ratio=ratio,required=3,**{'pass':ratio>=3}))


def variables(tokens, scope):
    return scope+' {\n'+''.join(f' --apt-{k.replace("_","-")}: {v["hex"]};\n' for k,v in tokens.items())+'}\n'


def page(title, body, head='', scripts=''):
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>body{margin:0;padding:24px;background:#181a1d;color:#eceef0;font:16px/1.6 system-ui}main{max-width:1100px;margin:auto;min-width:0}a{color:#b8dcff}a:focus-visible,button:focus-visible,select:focus-visible{outline:3px solid #b8dcff;outline-offset:3px}nav{display:flex;gap:16px;flex-wrap:wrap}section{margin:24px 0}.editor{margin:12px 0;border:1px solid #777}button,select{padding:8px;margin:4px}pre{overflow:auto}.CodeMirror,.cm-editor{height:280px}.cm-scroller{overflow:auto}</style>'+head+'</head><body><main>'+body+'</main>'+scripts+'</body></html>'


CORE = '''.markdown-body {box-sizing:border-box;background:var(--apt-background);color:var(--apt-foreground);font:17px/1.65 system-ui;max-width:100%;padding:clamp(16px,3vw,32px);overflow-wrap:anywhere}
.markdown-body h1,.markdown-body h2,.markdown-body h3,.markdown-body h4,.markdown-body h5,.markdown-body h6 {color:var(--apt-heading);line-height:1.3;margin:1.6em 0 .65em}
.markdown-body h1{font-size:2em}.markdown-body h2{font-size:1.65em}.markdown-body h3{font-size:1.35em}.markdown-body h4{font-size:1.15em}.markdown-body h5{font-size:1em}.markdown-body h6{font-size:.95em}
.markdown-body p{margin:.8em 0}.markdown-body ul,.markdown-body ol{padding-left:1.8em}.markdown-body li>ul,.markdown-body li>ol{margin:.25em 0}
.markdown-body a{color:var(--apt-link);text-decoration:underline;text-underline-offset:.15em}.markdown-body a:hover{color:var(--apt-primary)}
.markdown-body :focus-visible{outline:2px solid var(--apt-primary);outline-offset:3px}
.markdown-body blockquote{margin:1em 0;padding:.3em 1em;background:var(--apt-panel);border-left:3px solid var(--apt-primary)}
.markdown-body hr{border:0;border-top:1px solid var(--apt-border)}
.markdown-body .table-scroll{overflow:auto;max-width:100%}.markdown-body table{border-collapse:collapse;width:100%;margin:1em 0}
.markdown-body th,.markdown-body td{border:1px solid var(--apt-border);padding:.55em .7em}.markdown-body th{background:var(--apt-elevated)}.markdown-body tbody tr:nth-child(even){background:var(--apt-panel)}
.markdown-body code{background:var(--apt-panel);font: .92em/1.6 Consolas,monospace;padding:.12em .3em;border-radius:3px}.markdown-body pre{background:var(--apt-panel);padding:1em;overflow:auto}.markdown-body pre code{padding:0;white-space:pre;overflow-wrap:normal}
.markdown-body img{max-width:100%;height:auto}.markdown-body input[type=checkbox]{accent-color:var(--apt-primary)}.markdown-body .task-list-item,.markdown-body li:has(> input[type=checkbox]){list-style:none}
.markdown-body strong{color:var(--apt-strong);font-weight:700}.markdown-body em{color:var(--apt-emphasis);font-style:italic}
.markdown-body ::selection{background:var(--apt-selection);color:var(--apt-selection-text)}
'''
EXTRAS = '''.markdown-body details{border:1px solid var(--apt-border);padding:.7em;margin:1em 0}.markdown-body summary{cursor:pointer;color:var(--apt-primary)}
.markdown-body kbd{background:var(--apt-elevated);border:1px solid var(--apt-border);border-radius:3px;padding:.1em .35em;font-family:monospace}
.markdown-body .footnotes{color:var(--apt-muted);font-size:.9em}.markdown-body .markdown-alert{border-left:4px solid var(--alert-color);background:var(--apt-panel);padding:.7em 1em;margin:1em 0}.markdown-body .markdown-alert-title{color:var(--alert-color);font-weight:700}
.markdown-body .markdown-alert-note{--alert-color:var(--apt-info)}.markdown-body .markdown-alert-tip{--alert-color:var(--apt-success)}.markdown-body .markdown-alert-important{--alert-color:var(--apt-secondary)}.markdown-body .markdown-alert-warning{--alert-color:var(--apt-warning)}.markdown-body .markdown-alert-caution{--alert-color:var(--apt-error)}
'''


def export_markdown(result, directory, name):
    from .output_names import artifact_names
    artifact = artifact_names(result)
    from .syntax_examples import VENDOR as PRISM_VENDOR, verify_vendor as verify_prism
    from .visual_targets import PRISM
    manifest = verify_prism()
    shutil.copytree(PRISM_VENDOR, directory/'vendor/prism')
    (directory/artifact('tokens.css')).write_text(variables(result['tokens'],'.markdown-body'),encoding='utf-8')
    (directory/artifact('markdown.css')).write_text(CORE,encoding='utf-8')
    (directory/artifact('markdown-extras.css')).write_text(EXTRAS,encoding='utf-8')
    css = ''
    for classes, role in PRISM.items():
        role = {'diff_added':'inserted','diff_deleted':'deleted'}.get(role,role)
        css += ','.join('.markdown-body .token.'+c for c in classes.split())+'{color:var(--apt-'+role.replace('_','-')+')}\n'
    (directory/artifact('syntax-prism.css')).write_text(css,encoding='utf-8')
    wide = '\n| '+' | '.join('Column '+str(i) for i in range(1,13))+' |\n| '+' | '.join('---' for _ in range(12))+' |\n| '+' | '.join('Wide table value '+str(i) for i in range(12))+' |\n'
    specimen = markdown_specimen(artifact)+wide
    (directory/artifact('examples.md')).write_text(specimen,encoding='utf-8')
    (directory/artifact('example-image.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="640" height="160"><rect width="640" height="160" fill="'+result['tokens']['panel']['hex']+'"/><text x="24" y="90" font-size="24" fill="'+result['tokens']['foreground']['hex']+'">Local image / source palette</text></svg>',encoding='utf-8')
    alerts=''.join('<div class="markdown-alert markdown-alert-'+kind+'"><p class="markdown-alert-title">'+kind.title()+'</p><p>Optional renderer-provided alert structure.</p></div>' for kind in ('note','tip','important','warning','caution'))
    extras=alerts+'<p>Footnote reference<a href="#footnote-1" id="ref-1" role="doc-noteref">[1]</a>.</p><section class="footnotes"><ol><li id="footnote-1">Renderer-provided footnote <a href="#ref-1">Back to reference</a></li></ol></section>'
    scripts='<script src="vendor/browser-themes/markdown.js"></script>'+''.join('<script src="vendor/prism/'+f+'"></script>' for f in manifest['load_order'])
    data=json.dumps(specimen).replace('<','\\u003c')
    scripts+='<script id="source" type="application/json">'+data+'</script><script>const source=JSON.parse(document.getElementById("source").textContent);document.getElementById("document").innerHTML=AptMarkdown.DOMPurify.sanitize(AptMarkdown.marked.parse(source,{gfm:true}),{USE_PROFILES:{html:true}});document.querySelectorAll("#document table").forEach(table=>{const wrap=document.createElement("div");wrap.className="table-scroll";wrap.tabIndex=0;wrap.setAttribute("role","region");wrap.setAttribute("aria-label","Scrollable table");table.before(wrap);wrap.append(table)});document.querySelectorAll("#document pre").forEach(p=>p.tabIndex=0);Prism.highlightAll();document.documentElement.dataset.ready="true";</script>'
    body=f'<nav><a href="{artifact('examples.md')}" download>Download Markdown</a><a href="{artifact('README.md')}">Integration</a></nav><h1>'+html.escape(name)+' / Markdown</h1><p>Actual GFM parser, sanitization and offline Prism. Extras below use documented HTML contracts.</p><p id="outside-sentinel">Host content outside the document scope.</p><article class="markdown-body" id="document"></article><section class="markdown-body" id="extras">'+extras+'</section>'
    head=''.join('<link rel="stylesheet" href="'+f+'">' for f in (artifact('tokens.css'),artifact('markdown.css'),artifact('markdown-extras.css'),artifact('syntax-prism.css')))
    (directory/artifact('examples.html')).write_text(page(name+' Markdown',body,head,scripts),encoding='utf-8')
    coverage={'baseline':{'supported':['headings','paragraphs','emphasis','links','autolinks','lists','tasks','tables','strikethrough','quotes','images','code','dividers'],'rendering':'Bundled marked with gfm:true plus DOMPurify; no full GitHub renderer equivalence claimed.'},'conditional':{'alerts':'Expected .markdown-alert and .markdown-alert-<type> DOM; no alert parser installed.','footnotes':'Expected .footnotes and linked references; no footnote parser installed.','html':'Safe details, summary, kbd, sub and sup depend on host sanitization.','syntax':'Bundled Prism grammars; unknown languages remain plain text.'},'deferred':['math','Mermaid','application-specific adapters']}
    (directory/artifact('coverage.json')).write_text(json.dumps(coverage,indent=2)+'\n',encoding='utf-8')
    (directory/artifact('README.md')).write_text('# '+name+f" Markdown theme\n\nLoad {artifact('tokens.css')}, {artifact('markdown.css')} and optionally {artifact('markdown-extras.css')} and syntax-prism.css. Put `markdown-body` on each document container. Wrap wide tables in `.table-scroll` for local scrolling without changing table layout. Supply a sanitized GFM renderer and a syntax engine; CSS does not parse Markdown. This stylesheet cannot theme GitHub.com READMEs.\n\nAlerts use `.markdown-alert.markdown-alert-note|tip|important|warning|caution` with `.markdown-alert-title`; footnotes use `.footnotes` with accessible links. These are conditional HTML contracts, not formal GFM syntax support. The preview authors these extras separately from the parsed baseline.\n\nServe the output locally with a static HTTP server for browser previews. All assets are local. See {artifact('coverage.json')} and vendor/browser-themes/manifest.json for coverage and pinned dependencies. No installation, activation or publication is performed.\n",encoding='utf-8')
    result['examples']=[artifact('examples.html'),artifact('examples.md')]


def cm5_css(tokens, slug):
    scope='.cm-s-'+slug
    css=variables(tokens,scope)+f'''{scope}.CodeMirror{{background:var(--apt-background);color:var(--apt-foreground)}}
{scope} .CodeMirror-gutters{{background:var(--apt-panel);color:var(--apt-muted);border-color:var(--apt-border)}}
{scope} .CodeMirror-linenumber{{color:var(--apt-muted)}}{scope} .CodeMirror-cursor{{border-left-color:var(--apt-cursor)}}
{scope} .CodeMirror-selected{{background:var(--apt-selection)}}{scope} .CodeMirror-line .CodeMirror-selectedtext{{color:var(--apt-selection-text)}}
{scope} .CodeMirror-activeline-background{{background:var(--apt-active-line)}}{scope} .CodeMirror-activeline-gutter{{background:var(--apt-active-line)}}
{scope} .CodeMirror-line .cm-searching{{background:var(--apt-search-match);color:var(--apt-search-text)}}
{scope} .CodeMirror-matchingbracket{{color:var(--apt-matching-bracket);outline:1px solid var(--apt-border)}}
{scope} .CodeMirror-dialog{{background:var(--apt-elevated);color:var(--apt-foreground);border-color:var(--apt-border)}}
{scope} .CodeMirror-dialog input{{background:var(--apt-panel);color:var(--apt-foreground);border:1px solid var(--apt-border)}}
{scope} .CodeMirror-hints{{background:{tokens['elevated']['hex']};color:{tokens['foreground']['hex']};border-color:{tokens['border']['hex']}}}
{scope} .CodeMirror-hints .CodeMirror-hint{{color:var(--apt-foreground)}}
{scope} .CodeMirror-hints .CodeMirror-hint-active{{background:{tokens['selection']['hex']};color:{tokens['selection_text']['hex']}}}
{scope} ::selection{{background:var(--apt-selection);color:var(--apt-selection-text)}}
'''
    css+=''.join(scope+' .cm-'+cls+'{color:var(--apt-'+role.replace('_','-')+')}\n' for cls,role in SYNTAX.items())
    return css


def cm6_module(tokens):
    h=lambda key:tokens[key]['hex']
    styles={'&':{'color':h('foreground'),'backgroundColor':h('background')},'.cm-content':{'caretColor':h('cursor')},'.cm-cursor, .cm-dropCursor':{'borderLeftColor':h('cursor')},'&.cm-focused .cm-selectionBackground, .cm-selectionBackground':{'backgroundColor':h('selection')},'& .cm-content ::selection':{'backgroundColor':h('selection'),'color':h('selection_text')},'.cm-gutters':{'backgroundColor':h('panel'),'color':h('muted'),'borderColor':h('border')},'.cm-activeLine, .cm-activeLineGutter':{'backgroundColor':h('active_line')},'.cm-searchMatch, .cm-searchMatch.cm-searchMatch-selected':{'backgroundColor':h('search_match'),'color':h('search_text')},'&.cm-focused .cm-matchingBracket':{'color':h('matching_bracket'),'outline':'1px solid '+h('border')},'.cm-panels, .cm-tooltip':{'backgroundColor':h('elevated'),'color':h('foreground'),'borderColor':h('border')},'.cm-panels input, .cm-panels button':{'backgroundColor':h('panel'),'color':h('foreground'),'border':'1px solid '+h('border')},'.cm-tooltip-autocomplete > ul > li[aria-selected]':{'backgroundColor':h('selection'),'color':h('selection_text')}}
    mapping={'keyword':'keyword','string':'string','number':'number','comment':'comment','function(tags.variableName)':'function','typeName':'type','operator':'operator','bool':'constant','atom':'constant','tagName':'tag','attributeName':'attribute','propertyName':'property','variableName':'variable','meta':'meta','link':'link','url':'link','heading':'heading','emphasis':'emphasis','strong':'strong','invalid':'invalid','inserted':'inserted','deleted':'deleted'}
    definitions=','.join('{tag:tags.'+tag+',color:'+json.dumps(h(role))+'}' for tag,role in mapping.items())
    return 'import {EditorView} from "@codemirror/view";\nimport {HighlightStyle,syntaxHighlighting} from "@codemirror/language";\nimport {tags} from "@lezer/highlight";\nexport const theme=EditorView.theme('+json.dumps(styles)+',{dark:true});\nexport const highlightStyle=HighlightStyle.define(['+definitions+']);\nexport const extension=[theme,syntaxHighlighting(highlightStyle)];\nexport default extension;\n'


def export_codemirror(result, directory, name):
    from .output_names import artifact_names
    artifact = artifact_names(result)
    from .targets import slug
    version=5 if result['target']=='codemirror5' else 6
    ident=artifact.identity.key
    filename=artifact('theme.css') if version==5 else artifact('theme.mjs')
    (directory/filename).write_text(cm5_css(result['tokens'],ident) if version==5 else cm6_module(result['tokens']),encoding='utf-8')
    body='<h1>'+html.escape(name)+' / CodeMirror '+str(version)+'</h1><nav><a href="'+filename+f'" download>Download theme</a><a href="{artifact('README.md')}">Integration</a></nav><p>Real local editors. Try typing, selection, Ctrl-F and Ctrl-Space. Sample code is never executed.</p>'
    for language in SAMPLES:
        body+='<section><h2>'+language.title()+'</h2><div class="editor" id="'+language+'"></div></section>'
    body+='<section><h2>Unrelated editor / isolation control</h2><div class="editor" id="unrelated"></div></section>'
    samples=json.dumps(SAMPLES).replace('<','\\u003c')
    if version==5:
        vendor='vendor/browser-themes/'
        files=['lib-codemirror','mode-markdown-markdown','mode-javascript-javascript','mode-python-python','addon-dialog-dialog','addon-search-searchcursor','addon-search-search','addon-search-match-highlighter','addon-edit-matchbrackets','addon-selection-active-line','addon-selection-mark-selection','addon-hint-show-hint']
        head=''.join('<link rel="stylesheet" href="'+vendor+'cm5-'+f+'.css">' for f in ('lib-codemirror','addon-dialog-dialog','addon-hint-show-hint'))+'<link rel="stylesheet" href="'+filename+'">'
        scripts=''.join('<script src="'+vendor+'cm5-'+f+'.js"></script>' for f in files)
        scripts+='<script>window.editors={};for(const [lang,doc] of Object.entries('+samples+')){editors[lang]=CodeMirror(document.getElementById(lang),{value:doc,mode:lang,theme:"'+ident+'",lineNumbers:true,styleActiveLine:true,styleSelectedText:true,matchBrackets:true,extraKeys:{"Ctrl-Space":cm=>cm.showHint({hint:()=>({list:["answer","value","print"],from:cm.getCursor(),to:cm.getCursor()}),completeSingle:false})}});editors[lang].setOption("hintOptions",{container:editors[lang].getWrapperElement()})}editors.unrelated=CodeMirror(document.getElementById("unrelated"),{value:"const unrelated = 1;",mode:"javascript",lineNumbers:true});document.documentElement.dataset.ready="true";</script>'
    else:
        imports={package:'./vendor/browser-themes/cm6-runtime.mjs' for package in ('@codemirror/view','@codemirror/language','@lezer/highlight')}
        head='<script type="importmap">'+json.dumps({'imports':imports})+'</script>'
        scripts='<script type="module">import * as CM from "./vendor/browser-themes/cm6-runtime.mjs";import {extension} from "./'+artifact("theme.mjs")+'";window.CM=CM;window.editors={};const samples='+samples+';for(const [lang,doc] of Object.entries({...samples,unrelated:"const unrelated = 1;"})){const language=lang==="unrelated"?CM.javascript():CM[lang]();editors[lang]=new CM.EditorView({parent:document.getElementById(lang),state:CM.EditorState.create({doc,extensions:[CM.lineNumbers(),CM.history(),CM.drawSelection(),CM.highlightActiveLine(),CM.highlightActiveLineGutter(),CM.bracketMatching(),CM.search(),CM.autocompletion({override:[ctx=>({from:ctx.pos,options:[{label:"answer",type:"function"},{label:"value",type:"variable"}]})]}),CM.keymap.of([...CM.defaultKeymap,...CM.historyKeymap,...CM.searchKeymap,...CM.completionKeymap]),language,...(lang==="unrelated"?[CM.syntaxHighlighting(CM.defaultHighlightStyle)]:extension)]})})}document.documentElement.dataset.ready="true";</script>'
    (directory/artifact('examples.html')).write_text(page(name+' CodeMirror '+str(version),body,head,scripts),encoding='utf-8')
    contract='Load the CSS and CodeMirror 5 core CSS, then set `theme: "'+ident+'"`. Preview compatibility is pinned to CodeMirror 5.65.16. Keep completion popups inside the themed wrapper with `hintOptions: {container: editor.getWrapperElement()}` as in the preview. Load the relevant editor addons for their UI styles.' if version==5 else 'Import `{theme, highlightStyle, extension}` from `./'+artifact("theme.mjs")+'`; add `extension` to your EditorState extensions. Peer dependencies: @codemirror/view 6.x, @codemirror/language 6.x, @lezer/highlight 1.x. The combined extension includes syntaxHighlighting(highlightStyle). Use one shared dependency instance in your application.'
    (directory/artifact('README.md')).write_text('# '+name+' CodeMirror '+str(version)+'\n\n'+contract+f"\n\nServe {artifact('examples.html')} over local HTTP (ES modules need HTTP). All preview dependencies are bundled; see vendor/browser-themes/manifest.json for exact versions, hashes and licenses. Node is needed only to rebuild vendor assets, never for Python theme generation. Browser evidence does not establish acceptance in downstream applications. No installation, activation or publication is performed.\n",encoding='utf-8')
    result['examples']=[artifact('examples.html')]


def export_browser_theme(result, directory, name):
    from .output_names import artifact_names
    artifact = artifact_names(result)
    manifest=verify_vendor()
    shutil.copytree(VENDOR,directory/'vendor/browser-themes')
    if result['target']=='markdown':
        export_markdown(result,directory,name)
    else:
        export_codemirror(result,directory,name)
    result['dependency_manifest']='vendor/browser-themes/manifest.json'
    result['acceptance_limits']='Real offline browser preview; downstream application integration and native visual acceptance remain pending.'
    (directory/artifact('dependencies.json')).write_text(json.dumps(manifest['packages'],indent=2)+'\n',encoding='utf-8')
