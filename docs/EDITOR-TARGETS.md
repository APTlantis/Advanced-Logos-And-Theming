# Alacritty, Notepad++ and Sublime Text exports

Contract review: 2026-10-08. These are dark exports derived from the unchanged canonical 32 colors. Budgets limit named tokens; reuse and counts below the budget are intentional.

| Target ID | Default budget | Planning range | Native artifact |
| --- | ---: | ---: | --- |
| `alacritty` | 20 | 16–24 | `<name>.toml` |
| `notepad_plus_plus` | 32 | 24–40 | `<name>.xml` |
| `sublime_text` | 40 | 32–56 | `<name>.sublime-color-scheme` |

Ranges are planning guidance, not enforced promises. Alacritty requires 20 tokens for primary colors, cursor, selection and the 16 ANSI entries; a 16-token budget is rejected. Editor targets require 22 base tokens and add up to eight semantic variants, so defaults currently emit 30 tokens. Larger budgets do not add filler colors. Optional variants alias their base semantic tokens when omitted.

## Alacritty

Uses the current [official TOML configuration contract](https://alacritty.org/config-alacritty.html): `colors.primary`, `colors.cursor`, `colors.selection`, `colors.normal` and `colors.bright`. Cursor text reuses the background; selection text reuses the foreground. Dim colors, search/hint colors and indexed colors beyond ANSI remain application defaults. Contrast checks cover foreground/selection, cursor/background and ANSI/background, with an opaque background; terminal applications can override colors at runtime.

For operator installation, keep the generated TOML in a stable location and add its path to `[general] import = ["path/to/theme.toml"]` in the Alacritty config. On Windows the config is `%APPDATA%\alacritty\alacritty.toml`. Later imports and the parent config can override these colors. Generation performs no installation. Native configuration loading and an ANSI/selection/cursor screen review are pending.

## Notepad++

Uses `NotepadPlus/LexerStyles/LexerType/WordsStyle` and `NotepadPlus/GlobalStyles/WidgetStyle`, with names and style IDs checked against the [official shipped Obsidian theme](https://github.com/notepad-plus-plus/notepad-plus-plus/blob/master/PowerEditor/installer/themes/Obsidian.xml). Python, C++ and JSON lexers are explicitly mapped. Keyword classes retain application language keyword lists; the export does not supply replacements. Other lexers, plugins, user-defined languages and native dark-mode chrome are outside this acceptance contract. A partial lexer theme must be reviewed before use across other languages.

For operator installation, copy the XML to the themes directory used by the active Notepad++ installation (normally `%APPDATA%\Notepad++\themes` for a standard installation), restart and choose its filename under Settings → Style Configurator. Portable installations use their own themes directory. The application may retain or supply styles absent from this partial theme.

Notepad++ normally ignores the selection foreground unless `enableSelectFgColor.xml` is enabled. The exporter supplies the value but never changes that application setting. Declared selection contrast covers the exported foreground/background pair only; selection readability with syntax colors retained remains unverified. Native selection, lexer, gutter, caret, folding and application loading checks are pending.

## Sublime Text

Uses the [official JSON color-scheme contract](https://www.sublimetext.com/docs/color_schemes.html), with editor globals and 16 scope rules. Broad rules precede narrower numeric/operator/tag/attribute/escape rules. Scope coverage depends on the installed syntax definitions. This is an editor color scheme; menus, tabs and sidebar chrome retain the selected Sublime UI theme. Targets Sublime Text 4; legacy `.tmTheme` output is not generated.

For operator installation, use Preferences → Browse Packages and copy the file into `User`, then use Select Color Scheme. Selection and find matches explicitly set foreground and background colors. Native scheme selection, representative syntax, inactive selection, gutter and diff review are pending.

## Recovery and evidence

Existing pilot outputs and historical exporter files remain preserved. Generate into a new run directory to review these targets; existing collections require deliberate regeneration. Each target includes `tokens.json` and `validation.json`; editor token records include acceptance limits. Static parsing, provenance, canonical immutability and contrast checks establish local output properties only. The offline report is a preview, not a native renderer. No installation, activation or theme publication is performed.
