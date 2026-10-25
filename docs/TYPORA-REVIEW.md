# Typora Markdown review

Fresh local pilot: [browser simulation](../pilot/typora-markdown-2026-10-11/typora/examples.html), [Markdown stress document](../pilot/typora-markdown-2026-10-11/typora/examples.md), [CSS](../pilot/typora-markdown-2026-10-11/typora/aptlantis-black-gold.css). The image fixture must remain beside the Markdown document. All fixture data is illustrative.

The 2026-10-11 pass styles screens using existing tokens, without changing the canonical 32 colors or the 40-token budget. Browser simulation does not reproduce Typora's base stylesheet, CodeMirror initialization, editing DOM or application settings. Heavy wrapping in very dense narrow tables is expected. Print/PDF, math/diagram rendering and exhaustive application chrome remain outside that historical acceptance scope.

## Shared diagram defaults — 2026-10-25

Future Typora exports include the following defaults in their theme CSS:

```css
:root {
  --mermaid-theme: dark;
  --sequence-theme: simple;
  --mermaid-font-family: "trebuchet ms", verdana, arial, sans-serif;
  --mermaid-sequence-numbers: off;
  --mermaid-flowchart-curve: linear;
  --mermaid--gantt-left-padding: 75;
}
```

These settings do not add palette tokens; the canonical 32 colors and 40-token budget are unchanged. Diagram alignment is left to Typora and user overrides. Mermaid's built-in dark renderer is not a custom mapping of the canonical palette.

Fresh isolated pilot: [browser source preview](../pilot/typora-diagrams-2026-10-25/typora/apt-black-gold-typora-examples.html), [Markdown fixtures](../pilot/typora-diagrams-2026-10-25/typora/apt-black-gold-typora-examples.md), [acceptance evidence](../migration/typora-diagrams-acceptance-2026-10-25.json). Artifact filenames were resolved through the run's v2 Typora manifest. All 25 focused tests and three browser viewport checks passed; native diagram rendering/export acceptance remains pending.

Enable **Diagrams** in **Preferences → Markdown** for native rendering. The new Markdown fixtures cover js-sequence, a Mermaid flowchart, a per-diagram sequence-number override and Gantt padding. Their HTML counterparts show escaped source only, with a native-review label; no Mermaid runtime is bundled. The earlier pilot above remains historical.

[Typora documents](https://support.typora.io/Draw-Diagrams-With-Markdown/#global-mermaid-options) Mermaid themes `base`, `default`, `dark`, `forest`, `neutral` and `night`; sequence styles `simple` and `hand`; numbering `off`/`on`; and flowchart curves including `linear`, `basis`, `natural` and `step`. Font stacks and numeric Gantt padding may also be customized. Preserve the documented double hyphen in `--mermaid--gantt-left-padding`. Alternatives are operator choices; generated themes remain dark by default.

Use `base.user.css` to override all themes or `{current-theme}.user.css` to override one theme, matching the CSS filename's case. Typora loads these after the selected theme, in that order; see [custom CSS guidance](https://support.typora.io/Add-Custom-CSS/). For example, `:root { --mermaid-sequence-numbers: on; }` enables numbering globally. The specimen also demonstrates Typora's documented inline `%%{init: ...}%%` configuration for an individual diagram; compatibility depends on its bundled Mermaid version.

When exporting HTML/PDF/images with a different theme from the active editing theme, some Mermaid options from the export theme may not apply. Review using the intended active theme, and record export results separately. These controls cover diagrams, not all Typora preferences.

## Native acceptance checklist

Status: **pending**. Generation did not install or activate a theme. If the operator chooses to test it in Typora, record the application version, OS, theme overrides, document settings and results separately.

1. Load the CSS through Typora's theme folder and open `examples.md` beside `example-image.png`, following [official theme guidance](https://theme.typora.io/doc/Write-Custom-Theme/).
2. Review ordinary, long-content, 100-row and 12-column tables at normal and narrow window widths. Confirm header/row distinction and left/center/right alignment, with all content accessible.
3. Edit cells, move the caret using Tab/Shift+Tab and arrow keys, insert/delete rows and columns, select cell text and undo edits. Confirm native controls remain usable.
4. Review six heading levels, nested and task lists, nested quotes, inline/fenced code, links, emphasis, highlights, footnotes, TOC and image sizing. Enable optional Markdown features in preferences when needed.
5. Check selection, caret visibility, syntax highlighting, sidebar, dialogs and link hover/focus. Change the preferred font size and confirm relative sizing follows it.
6. For a newly generated specimen, review all four diagram fixtures, default dark Mermaid styling, sequence style, flowchart curves, Gantt padding and the inline numbering override. Record Typora/Mermaid versions and user CSS overrides; check same-theme and different-theme export behavior separately. Browser source previews do not establish these results.
7. Record pass/fail findings and screenshots before claiming native acceptance. Return to the prior theme if desired; the original output remains preserved.

## Local evidence

[Acceptance record](../migration/typora-markdown-acceptance-2026-10-11.json) records 35 focused tests, Chromium at 1440/900/390 pixels, isolated wheel generation, original output hash equality and unchanged SiYuan CSS. Typora token colors and origins match the prior output; palette import adds only legacy-family metadata to underived tokens. Import provenance identifies the canonical palette file rather than claiming a new extraction from the original artwork.

The exporter and specimens are Python package code in `apt_theme/typora.py`; no external Markdown parser, fonts, CDN or framework is needed. The shared run report links to the browser specimen through the existing examples interface. Project identity, stage, parent registration and root discovery paths are unchanged, so the D-drive index and parent manifests require no updates.
