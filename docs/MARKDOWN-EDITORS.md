# Markdown and CodeMirror output contracts

Added 2026-10-16. These three independently selectable default targets extend the pipeline from twelve to fifteen. Each has a 40-color budget and currently consumes 39 meaningful named color tokens; typography/spacing are CSS values, not additional palette colors. All preserve the canonical 32 source colors and use existing hue-preserving dark adaptation. GFM defines syntax, not an official theme schema.

| Target | Native integration | Additional files |
| --- | --- | --- |
| `markdown` | Load `tokens.css`, `markdown.css`, optional `markdown-extras.css` and `syntax-prism.css`; wrap documents in `.markdown-body` | `examples.md`, `examples.html`, `example-image.svg`, `coverage.json` |
| `codemirror5` | Load `apt-<theme-slug>.css` and CodeMirror core CSS; configure `theme: "apt-<theme-slug>"` | `examples.html`; actual CodeMirror 5.65.16 preview |
| `codemirror6` | Import `{theme, highlightStyle, extension}` from `theme.mjs`; add `extension` to EditorState | `examples.html`; actual CodeMirror 6 preview |

Each target also supplies README.md, dependencies.json, tokens.json, validation.json, a provenance-bearing `apt-<theme>-<target>-palette.toml` and labeled `-swatch.png`. Version 6 peer contracts are @codemirror/view 6.x, @codemirror/language 6.x and @lezer/highlight 1.x; exact preview package versions, integrity and licenses live in `vendor/browser-themes/manifest.json`. The ES module uses the host's shared CodeMirror dependency instances. It does not bundle a competing runtime into the distributable theme module.

## Markdown rendering and optional structures

The preview runs bundled marked with `gfm: true`, sanitizes the result with bundled DOMPurify and highlights supported fences with existing local Prism 1.30.0 grammars. Unknown languages remain plain text. It covers CommonMark structures plus tables, tasks, strikethrough and extended autolinks. Sanitization handles unsafe raw HTML and URLs; CSS does not implement parser filtering. This is a GFM-capable preview, not a claim of complete GitHub renderer equivalence or a GitHub.com theme installation mechanism.

All document token declarations and styles are scoped to `.markdown-body`. Wrap wide tables in `.table-scroll` for accessible local horizontal scrolling, retaining table layout and renderer-provided alignment. Images resize within the document. Keyboard links, disclosures, code blocks and scroll regions expose focus treatment.

Optional extras style expected HTML, independently of parser support:

- Alerts: `.markdown-alert.markdown-alert-note|tip|important|warning|caution`, with `.markdown-alert-title` for the title. Alert parsing is not installed.
- Footnotes: `.footnotes` with linked, uniquely identified references and backlinks. Footnote parsing is not installed.
- Safe `details`, `summary`, `kbd`, `sub` and `sup` depend on the host's sanitizer policy.

The preview authors alert and footnote structures separately and labels them as conditional HTML contracts. `coverage.json` lists supported, conditional and deferred capabilities. Math, Mermaid, framework adapters and downstream application integrations are deferred. Host applications must sanitize untrusted content according to their own trust boundary; the preview sanitizer is not applied automatically by the CSS.

## CodeMirror behavior

Both versions map the existing syntax roles into native token systems and theme the editor, gutters, cursor, selection, active line, search results, matching brackets, panels and completion tooltips. Version 5 CSS stays under `.cm-s-apt-<slug>`. Keep its completion popup inside the themed wrapper with `hintOptions: {container: editor.getWrapperElement()}`. Version 6 exports `EditorView.theme(..., {dark:true})`, `HighlightStyle.define(...)`, and their combined syntax-highlighting extension. Both previews provide Markdown, JavaScript and Python editing plus an unrelated editor as an isolation control. Text is local and sample code is never executed.

## Generate and review locally

```powershell
.venv/Scripts/python.exe -m apt_theme.cli import output/apt-BlackGold/palette.toml --name Black-Gold --output pilot/my-markdown-editors --targets markdown,codemirror5,codemirror6
.venv/Scripts/python.exe -m http.server 8126 --bind 127.0.0.1 --directory pilot/my-markdown-editors
```

Open `http://127.0.0.1:8126/markdown-editors.html`. CodeMirror 6 ES modules require local HTTP; all runtime assets stay local. A normal run selecting all defaults also adds `markdown-editors.html` alongside the full `review.html`. Existing outputs are not refreshed automatically. Never overwrite a non-pipeline directory.

To rebuild vendor resources, use `npm ci` then `npm run build` in `tools/browser-themes`. The package lock pins all direct/transitive dependencies. The builder copies licenses and records SHA-256 hashes. Export verifies vendor bytes before copying them. Node and network are development-time requirements only; normal Python generation and review use packaged assets. Browser files need their normal JavaScript-enabled local browser environment.

## Evidence and limits

Fresh pilots: [Black-Gold](../pilot/markdown-editors-2026-10-16/black-gold/markdown-editors.html), [Ada](../pilot/markdown-editors-2026-10-16/ada/markdown-editors.html). Evidence: [acceptance record](../migration/browser-themes-acceptance-2026-10-16.json).

Run `tools/check_browser_themes.cjs PILOT_ROOT PLAYWRIGHT_MODULE CHROMIUM_EXECUTABLE` against a root containing `black-gold` and `ada`. The checker starts a temporary loopback server, rejects external requests, and verifies actual parsing, sanitization, highlighting, layouts, computed text contrast, editor interactions and isolation. It records screenshots and browser-validation.json in that pilot root. Palette contrast findings remain in each target's validation.json, including selected syntax and active-line pairs. Browser evidence does not establish acceptance inside Typora, SiYuan or any other downstream application. Print/PDF, installation, activation, publication and release readiness remain outside this extension.
