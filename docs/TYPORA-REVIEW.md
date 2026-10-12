# Typora Markdown review

Fresh local pilot: [browser simulation](../pilot/typora-markdown-2026-10-11/typora/examples.html), [Markdown stress document](../pilot/typora-markdown-2026-10-11/typora/examples.md), [CSS](../pilot/typora-markdown-2026-10-11/typora/aptlantis-black-gold.css). The image fixture must remain beside the Markdown document. All fixture data is illustrative.

This pass styles screens using existing tokens, without changing the canonical 32 colors or the 40-token budget. Browser simulation does not reproduce Typora's base stylesheet, CodeMirror initialization, editing DOM or application settings. Heavy wrapping in very dense narrow tables is expected. Print/PDF, math/diagram rendering and exhaustive application chrome remain outside this acceptance scope.

## Native acceptance checklist

Status: **pending**. Generation did not install or activate a theme. If the operator chooses to test it in Typora, record the application version, OS, theme overrides, document settings and results separately.

1. Load the CSS through Typora's theme folder and open `examples.md` beside `example-image.png`, following [official theme guidance](https://theme.typora.io/doc/Write-Custom-Theme/).
2. Review ordinary, long-content, 100-row and 12-column tables at normal and narrow window widths. Confirm header/row distinction and left/center/right alignment, with all content accessible.
3. Edit cells, move the caret using Tab/Shift+Tab and arrow keys, insert/delete rows and columns, select cell text and undo edits. Confirm native controls remain usable.
4. Review six heading levels, nested and task lists, nested quotes, inline/fenced code, links, emphasis, highlights, footnotes, TOC and image sizing. Enable optional Markdown features in preferences when needed.
5. Check selection, caret visibility, syntax highlighting, sidebar, dialogs and link hover/focus. Change the preferred font size and confirm relative sizing follows it.
6. Record pass/fail findings and screenshots before claiming native acceptance. Return to the prior theme if desired; the original output remains preserved.

## Local evidence

[Acceptance record](../migration/typora-markdown-acceptance-2026-10-11.json) records 35 focused tests, Chromium at 1440/900/390 pixels, isolated wheel generation, original output hash equality and unchanged SiYuan CSS. Typora token colors and origins match the prior output; palette import adds only legacy-family metadata to underived tokens. Import provenance identifies the canonical palette file rather than claiming a new extraction from the original artwork.

The exporter and specimens are Python package code in `apt_theme/typora.py`; no external Markdown parser, fonts, CDN or framework is needed. The shared run report links to the browser specimen through the existing examples interface. Project identity, stage, parent registration and root discovery paths are unchanged, so the D-drive index and parent manifests require no updates.
