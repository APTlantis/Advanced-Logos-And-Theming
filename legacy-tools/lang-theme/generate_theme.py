#!/usr/bin/env python3
"""
APTlantis Theme Forge — generate_theme.py

Pipeline:
  palette.txt (ImageMagick UTF-16 LE)
    → parse 16 hex colors
    → analyze brightness / saturation / hue
    → assign semantic tokens
    → generate VSCode .json, Notepad++ .xml, JetBrains .icls,
       Windows Terminal .json, Alacritty .toml
"""

import colorsys
import json
import re
import sys
from pathlib import Path

PALETTES_DIR = Path("palettes")
THEMES_DIR = Path("themes")


# ── Palette parsing ───────────────────────────────────────────────────────────

def parse_palette(path: Path) -> list[str]:
    """
    Read ImageMagick pixel enumeration file → list of 16 hex colors.
    Handles both UTF-16 LE with BOM (older exports) and UTF-8 (newer srgba exports).
    Also handles 8-character RGBA hex codes (#RRGGBBAA) by extracting the first 6 digits.
    """
    raw = path.read_bytes()
    encoding = "utf-16" if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else "utf-8"
    content = raw.decode(encoding)
    # Match 6-char hex (srgb) or 8-char hex (srgba) — always take first 6
    colors = re.findall(r"#([0-9A-Fa-f]{6})[0-9A-Fa-f]{0,2}\b", content)
    return ["#" + c.upper() for c in colors[:16]]


# ── Color math ────────────────────────────────────────────────────────────────

def metrics(hex_color: str) -> dict:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    hue, lightness, saturation = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return {
        "hex": hex_color,
        "r": r, "g": g, "b": b,
        "hue": hue,
        "lightness": lightness,
        "saturation": saturation,
    }


def nh(hex_color: str) -> str:
    """Strip # prefix (Notepad++ / JetBrains use bare hex)."""
    return hex_color.lstrip("#")


# ── Semantic token assignment ─────────────────────────────────────────────────

def assign_tokens(colors: list[str]) -> dict[str, str]:
    """
    Map 16 raw palette colors to named design tokens.

    Strategy:
      - Backgrounds  → darkest colors by lightness
      - Text         → brightest colors by lightness
      - Accents      → most-saturated mid-brightness colors
      - Syntax roles → derived from the accent layer
    """
    m = [metrics(c) for c in colors]

    by_light = sorted(m, key=lambda c: c["lightness"])
    by_sat   = sorted(m, key=lambda c: c["saturation"], reverse=True)

    # Background layer (darkest)
    background    = by_light[0]["hex"]
    surface       = by_light[1]["hex"]
    panel         = by_light[2]["hex"]
    border        = by_light[3]["hex"]
    selection     = by_light[4]["hex"]
    line_highlight = by_light[2]["hex"]

    # Text layer (brightest)
    text_primary = by_light[-1]["hex"]
    text_muted   = by_light[-2]["hex"]

    # Accent layer: most-saturated colors in the mid-brightness range
    mid = [c for c in by_sat if 0.08 < c["lightness"] < 0.92]
    if len(mid) < 4:
        mid = by_sat  # fallback: use full sorted list

    accent           = mid[0]["hex"]
    accent_secondary = mid[1]["hex"] if len(mid) > 1 else mid[0]["hex"]
    highlight        = mid[2]["hex"] if len(mid) > 2 else mid[0]["hex"]
    comment_color    = mid[3]["hex"] if len(mid) > 3 else accent_secondary

    return {
        # Structure
        "background":    background,
        "surface":       surface,
        "panel":         panel,
        "border":        border,
        "selection":     selection,
        "lineHighlight": line_highlight,
        # Text
        "textPrimary": text_primary,
        "textMuted":   text_muted,
        # Accents
        "accent":          accent,
        "accentSecondary": accent_secondary,
        "highlight":       highlight,
        # Syntax
        "keyword":    accent,
        "string":     highlight,
        "number":     accent_secondary,
        "comment":    comment_color,
        "function":   highlight,
        "type":       accent,
        "variable":   text_primary,
        "constant":   accent_secondary,
        "operator":   text_muted,
        "punctuation": text_muted,
    }


# ── VSCode (.json) ────────────────────────────────────────────────────────────

def generate_vscode(t: dict, name: str) -> str:
    theme = {
        "$schema": "vscode://schemas/color-theme",
        "name": f"APT {name.title()}",
        "type": "dark",
        "colors": {
            # Editor core
            "editor.background":                    t["background"],
            "editor.foreground":                    t["textPrimary"],
            "editor.lineHighlightBackground":       t["lineHighlight"],
            "editor.selectionBackground":           t["selection"],
            "editor.inactiveSelectionBackground":   t["panel"],
            "editorCursor.foreground":              t["accent"],
            "editorWhitespace.foreground":          t["border"],
            "editorIndentGuide.background1":        t["border"],
            "editorIndentGuide.activeBackground1":  t["accentSecondary"],
            "editorLineNumber.foreground":          t["textMuted"],
            "editorLineNumber.activeForeground":    t["textPrimary"],
            "editorBracketMatch.background":        t["selection"],
            "editorBracketMatch.border":            t["accent"],
            # Widgets
            "editorWidget.background":              t["surface"],
            "editorSuggestWidget.background":       t["surface"],
            "editorSuggestWidget.border":           t["border"],
            "editorSuggestWidget.selectedBackground": t["panel"],
            "editorHoverWidget.background":         t["surface"],
            "editorHoverWidget.border":             t["border"],
            # Panels / sidebar
            "panel.background":                     t["panel"],
            "panel.border":                         t["border"],
            "sideBar.background":                   t["surface"],
            "sideBar.foreground":                   t["textMuted"],
            "sideBar.border":                       t["border"],
            "sideBarTitle.foreground":              t["textPrimary"],
            "sideBarSectionHeader.background":      t["panel"],
            "sideBarSectionHeader.foreground":      t["textPrimary"],
            # Activity bar
            "activityBar.background":               t["background"],
            "activityBar.foreground":               t["textPrimary"],
            "activityBar.border":                   t["border"],
            "activityBarBadge.background":          t["accent"],
            "activityBarBadge.foreground":          t["background"],
            # Status bar
            "statusBar.background":                 t["surface"],
            "statusBar.foreground":                 t["textPrimary"],
            "statusBar.border":                     t["border"],
            "statusBarItem.hoverBackground":        t["panel"],
            # Title bar
            "titleBar.activeBackground":            t["background"],
            "titleBar.activeForeground":            t["textPrimary"],
            "titleBar.inactiveBackground":          t["surface"],
            "titleBar.inactiveForeground":          t["textMuted"],
            "titleBar.border":                      t["border"],
            # Tabs
            "tab.activeBackground":                 t["background"],
            "tab.activeForeground":                 t["textPrimary"],
            "tab.activeBorder":                     t["accent"],
            "tab.inactiveBackground":               t["surface"],
            "tab.inactiveForeground":               t["textMuted"],
            "tab.border":                           t["border"],
            # Breadcrumb
            "breadcrumb.background":                t["background"],
            "breadcrumb.foreground":                t["textMuted"],
            "breadcrumb.activeSelectionForeground": t["textPrimary"],
            # Inputs
            "focusBorder":                          t["accent"],
            "input.background":                     t["surface"],
            "input.foreground":                     t["textPrimary"],
            "input.border":                         t["border"],
            "input.placeholderForeground":          t["textMuted"],
            "inputOption.activeBorder":             t["accent"],
            # Dropdowns / buttons
            "dropdown.background":                  t["surface"],
            "dropdown.foreground":                  t["textPrimary"],
            "dropdown.border":                      t["border"],
            "button.background":                    t["accent"],
            "button.foreground":                    t["background"],
            "button.hoverBackground":               t["highlight"],
            # Badges / lists
            "badge.background":                     t["accent"],
            "badge.foreground":                     t["background"],
            "list.activeSelectionBackground":       t["panel"],
            "list.activeSelectionForeground":       t["textPrimary"],
            "list.hoverBackground":                 t["surface"],
            "list.hoverForeground":                 t["textPrimary"],
            "list.inactiveSelectionBackground":     t["panel"],
            "list.highlightForeground":             t["accent"],
            # Scrollbar
            "scrollbar.shadow":                     t["background"],
            "scrollbarSlider.background":           t["border"],
            "scrollbarSlider.hoverBackground":      t["panel"],
            "scrollbarSlider.activeBackground":     t["accentSecondary"],
            # Integrated terminal
            "terminal.background":                  t["background"],
            "terminal.foreground":                  t["textPrimary"],
            "terminal.ansiBlack":                   t["background"],
            "terminal.ansiBrightBlack":             t["surface"],
            "terminal.ansiWhite":                   t["textMuted"],
            "terminal.ansiBrightWhite":             t["textPrimary"],
            "terminal.ansiBlue":                    t["accentSecondary"],
            "terminal.ansiBrightBlue":              t["accent"],
            "terminal.ansiCyan":                    t["highlight"],
            "terminal.ansiBrightCyan":              t["highlight"],
            "terminal.ansiYellow":                  t["number"],
            "terminal.ansiBrightYellow":            t["number"],
            "terminal.ansiRed":                     t["keyword"],
            "terminal.ansiBrightRed":               t["keyword"],
            "terminal.ansiMagenta":                 t["comment"],
            "terminal.ansiBrightMagenta":           t["comment"],
            "terminal.ansiGreen":                   t["string"],
            "terminal.ansiBrightGreen":             t["string"],
        },
        "tokenColors": [
            {
                "scope": ["comment", "punctuation.definition.comment", "string.comment"],
                "settings": {"foreground": t["comment"], "fontStyle": "italic"},
            },
            {
                "scope": [
                    "keyword", "keyword.control", "keyword.operator.new",
                    "storage.type", "storage.modifier",
                ],
                "settings": {"foreground": t["keyword"], "fontStyle": "bold"},
            },
            {
                "scope": ["string", "string.quoted", "string.template"],
                "settings": {"foreground": t["string"]},
            },
            {
                "scope": ["constant.numeric", "constant.language", "constant.other"],
                "settings": {"foreground": t["number"]},
            },
            {
                "scope": [
                    "entity.name.function", "support.function",
                    "meta.function-call.generic",
                ],
                "settings": {"foreground": t["function"]},
            },
            {
                "scope": [
                    "entity.name.type", "entity.name.class",
                    "support.type", "support.class",
                ],
                "settings": {"foreground": t["type"]},
            },
            {
                "scope": ["variable", "variable.other"],
                "settings": {"foreground": t["variable"]},
            },
            {
                "scope": ["variable.parameter", "entity.name.variable.parameter"],
                "settings": {"foreground": t["textMuted"], "fontStyle": "italic"},
            },
            {
                "scope": ["keyword.operator", "punctuation.separator"],
                "settings": {"foreground": t["operator"]},
            },
            {
                "scope": ["punctuation"],
                "settings": {"foreground": t["punctuation"]},
            },
            {
                "scope": ["entity.name.tag", "meta.tag.sgml"],
                "settings": {"foreground": t["keyword"]},
            },
            {
                "scope": ["entity.other.attribute-name"],
                "settings": {"foreground": t["accent"]},
            },
            {
                "scope": ["markup.heading"],
                "settings": {"foreground": t["accent"], "fontStyle": "bold"},
            },
            {
                "scope": ["markup.bold"],
                "settings": {"fontStyle": "bold"},
            },
            {
                "scope": ["markup.italic"],
                "settings": {"fontStyle": "italic"},
            },
            {
                "scope": ["markup.inline.raw", "markup.fenced_code.block"],
                "settings": {"foreground": t["highlight"]},
            },
        ],
    }
    return json.dumps(theme, indent=2)


# ── Notepad++ (.xml) ──────────────────────────────────────────────────────────

def generate_notepadpp(t: dict, name: str) -> str:
    bg      = nh(t["background"])
    surface = nh(t["surface"])
    panel   = nh(t["panel"])
    border  = nh(t["border"])
    sel     = nh(t["selection"])
    accent  = nh(t["accent"])
    accent2 = nh(t["accentSecondary"])
    hi      = nh(t["highlight"])
    text    = nh(t["textPrimary"])
    selection_text = nh(t.get("selectionText", t["textPrimary"]))
    muted   = nh(t["textMuted"])
    cmt     = nh(t["comment"])
    kw      = nh(t["keyword"])
    st      = nh(t["string"])
    num     = nh(t["number"])
    fn      = nh(t["function"])

    return f"""\
<?xml version="1.0" encoding="UTF-8" ?>
<NotepadPlus>
    <LexerStyles>

        <LexerType name="python" desc="Python" ext="py">
            <WordsStyle name="DEFAULT"      fgColor="{text}"   bgColor="{bg}"    bold="no"  italic="no"  underline="no" />
            <WordsStyle name="COMMENTLINE"  fgColor="{cmt}"    bgColor=""        bold="no"  italic="yes" underline="no" />
            <WordsStyle name="NUMBER"       fgColor="{num}"    bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="STRING"       fgColor="{st}"     bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="CHARACTER"    fgColor="{st}"     bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="WORD"         fgColor="{kw}"     bgColor=""        bold="yes" italic="no"  underline="no" />
            <WordsStyle name="TRIPLE"       fgColor="{cmt}"    bgColor=""        bold="no"  italic="yes" underline="no" />
            <WordsStyle name="TRIPLEDOUBLE" fgColor="{cmt}"    bgColor=""        bold="no"  italic="yes" underline="no" />
            <WordsStyle name="CLASSNAME"    fgColor="{accent}" bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="DEFNAME"      fgColor="{fn}"     bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="OPERATOR"     fgColor="{muted}"  bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="IDENTIFIER"   fgColor="{text}"   bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="COMMENTBLOCK" fgColor="{cmt}"    bgColor=""        bold="no"  italic="yes" underline="no" />
            <WordsStyle name="STRINGEOL"    fgColor="{st}"     bgColor="{panel}" bold="no"  italic="no"  underline="no" />
            <WordsStyle name="WORD2"        fgColor="{accent2}" bgColor=""       bold="no"  italic="no"  underline="no" />
            <WordsStyle name="DECORATOR"    fgColor="{hi}"     bgColor=""        bold="no"  italic="no"  underline="no" />
        </LexerType>

        <LexerType name="cpp" desc="C, C++" ext="cpp c h cc cxx hpp">
            <WordsStyle name="DEFAULT"      fgColor="{text}"   bgColor="{bg}"    bold="no"  italic="no"  underline="no" />
            <WordsStyle name="COMMENT"      fgColor="{cmt}"    bgColor=""        bold="no"  italic="yes" underline="no" />
            <WordsStyle name="COMMENTLINE"  fgColor="{cmt}"    bgColor=""        bold="no"  italic="yes" underline="no" />
            <WordsStyle name="NUMBER"       fgColor="{num}"    bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="WORD"         fgColor="{kw}"     bgColor=""        bold="yes" italic="no"  underline="no" />
            <WordsStyle name="STRING"       fgColor="{st}"     bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="CHARACTER"    fgColor="{st}"     bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="OPERATOR"     fgColor="{muted}"  bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="IDENTIFIER"   fgColor="{text}"   bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="PREPROCESSOR" fgColor="{accent2}" bgColor=""       bold="no"  italic="no"  underline="no" />
            <WordsStyle name="WORD2"        fgColor="{accent}" bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="WORD3"        fgColor="{fn}"     bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="WORD4"        fgColor="{hi}"     bgColor=""        bold="no"  italic="no"  underline="no" />
        </LexerType>

        <LexerType name="xml" desc="XML" ext="xml xsl xsd">
            <WordsStyle name="DEFAULT"          fgColor="{text}"   bgColor="{bg}"    bold="no"  italic="no"  underline="no" />
            <WordsStyle name="COMMENT"          fgColor="{cmt}"    bgColor=""        bold="no"  italic="yes" underline="no" />
            <WordsStyle name="NUMBER"           fgColor="{num}"    bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="DOUBLESTRING"     fgColor="{st}"     bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="SINGLESTRING"     fgColor="{st}"     bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="TAG"              fgColor="{kw}"     bgColor=""        bold="yes" italic="no"  underline="no" />
            <WordsStyle name="TAGEND"           fgColor="{kw}"     bgColor=""        bold="yes" italic="no"  underline="no" />
            <WordsStyle name="ATTRIBUTE"        fgColor="{accent}" bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="CDATA"            fgColor="{hi}"     bgColor="{panel}" bold="no"  italic="no"  underline="no" />
        </LexerType>

        <LexerType name="json" desc="JSON" ext="json">
            <WordsStyle name="DEFAULT"          fgColor="{text}"   bgColor="{bg}"    bold="no"  italic="no"  underline="no" />
            <WordsStyle name="NUMBER"           fgColor="{num}"    bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="STRING"           fgColor="{st}"     bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="STRINGEOL"        fgColor="{st}"     bgColor="{panel}" bold="no"  italic="no"  underline="no" />
            <WordsStyle name="PROPERTYNAME"     fgColor="{accent}" bgColor=""        bold="no"  italic="no"  underline="no" />
            <WordsStyle name="ESCAPESEQUENCE"   fgColor="{accent2}" bgColor=""       bold="no"  italic="no"  underline="no" />
            <WordsStyle name="KEYWORD"          fgColor="{kw}"     bgColor=""        bold="yes" italic="no"  underline="no" />
            <WordsStyle name="OPERATOR"         fgColor="{muted}"  bgColor=""        bold="no"  italic="no"  underline="no" />
        </LexerType>

    </LexerStyles>

    <GlobalStyles>
        <WidgetStyle name="Global override"                   fgColor=""       bgColor=""        bold="no"  italic="no"  underline="no" />
        <WidgetStyle name="Default Style"                     fgColor="{text}" bgColor="{bg}"    bold="no"  italic="no"  underline="no" />
        <WidgetStyle name="Indent guideline style"            fgColor="{border}" bgColor=""      bold="no"  italic="no"  underline="no" />
        <WidgetStyle name="Brace highlight style"             fgColor="{accent}" bgColor=""      bold="yes" italic="no"  underline="no" />
        <WidgetStyle name="Bad brace colour"                  fgColor="FF4444" bgColor=""        bold="no"  italic="no"  underline="no" />
        <WidgetStyle name="Current line background colour"    fgColor=""       bgColor="{surface}" bold="no" italic="no" underline="no" />
        <WidgetStyle name="Selected text colour"              fgColor="{selection_text}" bgColor="{sel}"   bold="no"  italic="no"  underline="no" />
        <WidgetStyle name="Caret colour"                      fgColor="{accent}" bgColor="{bg}"  bold="no"  italic="no"  underline="no" />
        <WidgetStyle name="Edge colour"                       fgColor="{border}" bgColor=""      bold="no"  italic="no"  underline="no" />
        <WidgetStyle name="Line number margin"                fgColor="{muted}" bgColor="{surface}" bold="no" italic="no" underline="no" />
        <WidgetStyle name="Fold margin"                       fgColor="{border}" bgColor="{surface}" bold="no" italic="no" underline="no" />
        <WidgetStyle name="Fold margin highlight"             fgColor="{muted}" bgColor="{panel}" bold="no" italic="no"  underline="no" />
        <WidgetStyle name="Find Mark Style"                   fgColor=""       bgColor="{accent}" bold="no" italic="no"  underline="no" />
        <WidgetStyle name="Mark Style 1"                      fgColor=""       bgColor="{hi}"    bold="no"  italic="no"  underline="no" />
        <WidgetStyle name="Mark Style 2"                      fgColor=""       bgColor="{accent}" bold="no" italic="no"  underline="no" />
        <WidgetStyle name="Mark Style 3"                      fgColor=""       bgColor="{accent2}" bold="no" italic="no" underline="no" />
        <WidgetStyle name="Mark Style 4"                      fgColor=""       bgColor="{panel}" bold="no"  italic="no"  underline="no" />
        <WidgetStyle name="Mark Style 5"                      fgColor=""       bgColor="{border}" bold="no" italic="no"  underline="no" />
        <WidgetStyle name="Smart Highlighting"                fgColor=""       bgColor="{panel}" bold="no"  italic="no"  underline="no" />
        <WidgetStyle name="URL hovered"                       fgColor="{accent}" bgColor=""      bold="no"  italic="no"  underline="yes" />
        <WidgetStyle name="Tags match highlighting"           fgColor=""       bgColor="{sel}"   bold="no"  italic="no"  underline="no" />
        <WidgetStyle name="Tags attribute"                    fgColor="{accent}" bgColor=""      bold="no"  italic="no"  underline="no" />
    </GlobalStyles>

</NotepadPlus>
"""


# ── JetBrains (.icls) ─────────────────────────────────────────────────────────

def generate_jetbrains(t: dict, name: str) -> str:
    bg      = nh(t["background"])
    surface = nh(t["surface"])
    panel   = nh(t["panel"])
    border  = nh(t["border"])
    sel     = nh(t["selection"])
    accent  = nh(t["accent"])
    accent2 = nh(t["accentSecondary"])
    hi      = nh(t["highlight"])
    text    = nh(t["textPrimary"])
    selection_text = nh(t.get("selectionText", t["textPrimary"]))
    muted   = nh(t["textMuted"])
    cmt     = nh(t["comment"])
    kw      = nh(t["keyword"])
    st      = nh(t["string"])
    num     = nh(t["number"])
    fn      = nh(t["function"])

    scheme_name = f"APT {name.title()}"

    return f"""\
<scheme name="{scheme_name}" version="142" parent_scheme="Darcula">
  <metaInfo>
    <property name="created">2026-03-09</property>
    <property name="ide">idea</property>
    <property name="ideVersion">2024.1.0.0</property>
    <property name="modified">2026-03-09</property>
    <property name="originalScheme">{scheme_name}</property>
  </metaInfo>
  <colors>
    <option name="CARET_COLOR"              value="{accent}" />
    <option name="CARET_ROW_COLOR"          value="{surface}" />
    <option name="CONSOLE_BACKGROUND_KEY"   value="{bg}" />
    <option name="GUTTER_BACKGROUND"        value="{surface}" />
    <option name="INDENT_GUIDE"             value="{border}" />
    <option name="LINE_NUMBERS_COLOR"       value="{muted}" />
    <option name="RIGHT_MARGIN_COLOR"       value="{border}" />
    <option name="SELECTION_BACKGROUND"     value="{sel}" />
    <option name="SELECTION_FOREGROUND"     value="{selection_text}" />
    <option name="TEARLINE_COLOR"           value="{border}" />
    <option name="WHITESPACES"              value="{border}" />
    <option name="MATCHED_BRACES_INDENT_GUIDE_COLOR" value="{accent}" />
  </colors>
  <attributes>
    <option name="TEXT">
      <value>
        <option name="FOREGROUND" value="{text}" />
        <option name="BACKGROUND" value="{bg}" />
      </value>
    </option>
    <option name="DEFAULT_BACKGROUND">
      <value>
        <option name="BACKGROUND" value="{bg}" />
      </value>
    </option>
    <option name="DEFAULT_KEYWORD">
      <value>
        <option name="FOREGROUND" value="{kw}" />
        <option name="FONT_TYPE" value="1" />
      </value>
    </option>
    <option name="DEFAULT_STRING">
      <value>
        <option name="FOREGROUND" value="{st}" />
      </value>
    </option>
    <option name="DEFAULT_NUMBER">
      <value>
        <option name="FOREGROUND" value="{num}" />
      </value>
    </option>
    <option name="DEFAULT_LINE_COMMENT">
      <value>
        <option name="FOREGROUND" value="{cmt}" />
        <option name="FONT_TYPE" value="2" />
      </value>
    </option>
    <option name="DEFAULT_BLOCK_COMMENT">
      <value>
        <option name="FOREGROUND" value="{cmt}" />
        <option name="FONT_TYPE" value="2" />
      </value>
    </option>
    <option name="DEFAULT_DOC_COMMENT">
      <value>
        <option name="FOREGROUND" value="{cmt}" />
        <option name="FONT_TYPE" value="2" />
      </value>
    </option>
    <option name="DEFAULT_DOC_COMMENT_TAG">
      <value>
        <option name="FOREGROUND" value="{accent}" />
        <option name="FONT_TYPE" value="1" />
      </value>
    </option>
    <option name="DEFAULT_FUNCTION_DECLARATION">
      <value>
        <option name="FOREGROUND" value="{fn}" />
        <option name="FONT_TYPE" value="1" />
      </value>
    </option>
    <option name="DEFAULT_FUNCTION_CALL">
      <value>
        <option name="FOREGROUND" value="{fn}" />
      </value>
    </option>
    <option name="DEFAULT_CLASS_NAME">
      <value>
        <option name="FOREGROUND" value="{accent}" />
      </value>
    </option>
    <option name="CLASS_NAME_ATTRIBUTES">
      <value>
        <option name="FOREGROUND" value="{accent}" />
      </value>
    </option>
    <option name="DEFAULT_INTERFACE_NAME">
      <value>
        <option name="FOREGROUND" value="{accent2}" />
        <option name="FONT_TYPE" value="3" />
      </value>
    </option>
    <option name="DEFAULT_IDENTIFIER">
      <value>
        <option name="FOREGROUND" value="{text}" />
      </value>
    </option>
    <option name="DEFAULT_CONSTANT">
      <value>
        <option name="FOREGROUND" value="{accent2}" />
        <option name="FONT_TYPE" value="1" />
      </value>
    </option>
    <option name="DEFAULT_PARAMETER">
      <value>
        <option name="FOREGROUND" value="{text}" />
        <option name="FONT_TYPE" value="2" />
      </value>
    </option>
    <option name="DEFAULT_INSTANCE_FIELD">
      <value>
        <option name="FOREGROUND" value="{accent}" />
      </value>
    </option>
    <option name="DEFAULT_OPERATION_SIGN">
      <value>
        <option name="FOREGROUND" value="{muted}" />
      </value>
    </option>
    <option name="DEFAULT_BRACES">
      <value>
        <option name="FOREGROUND" value="{muted}" />
      </value>
    </option>
    <option name="DEFAULT_BRACKETS">
      <value>
        <option name="FOREGROUND" value="{muted}" />
      </value>
    </option>
    <option name="DEFAULT_COMMA">
      <value>
        <option name="FOREGROUND" value="{muted}" />
      </value>
    </option>
    <option name="DEFAULT_SEMICOLON">
      <value>
        <option name="FOREGROUND" value="{muted}" />
      </value>
    </option>
    <option name="DEFAULT_TAG">
      <value>
        <option name="FOREGROUND" value="{kw}" />
      </value>
    </option>
    <option name="DEFAULT_ENTITY">
      <value>
        <option name="FOREGROUND" value="{hi}" />
      </value>
    </option>
    <option name="DEFAULT_PREDEFINED_SYMBOL">
      <value>
        <option name="FOREGROUND" value="{hi}" />
      </value>
    </option>
    <option name="DEFAULT_VALID_STRING_ESCAPE">
      <value>
        <option name="FOREGROUND" value="{accent2}" />
        <option name="FONT_TYPE" value="1" />
      </value>
    </option>
    <option name="DEFAULT_TEMPLATE_LANGUAGE_COLOR">
      <value>
        <option name="BACKGROUND" value="{panel}" />
      </value>
    </option>
    <option name="SEARCH_RESULT_ATTRIBUTES">
      <value>
        <option name="BACKGROUND" value="{sel}" />
        <option name="ERROR_STRIPE_COLOR" value="{accent}" />
      </value>
    </option>
    <option name="FOLDED_TEXT_ATTRIBUTES">
      <value>
        <option name="FOREGROUND" value="{muted}" />
        <option name="BACKGROUND" value="{panel}" />
      </value>
    </option>
    <option name="IDENTIFIER_UNDER_CARET_ATTRIBUTES">
      <value>
        <option name="BACKGROUND" value="{panel}" />
        <option name="ERROR_STRIPE_COLOR" value="{accent2}" />
      </value>
    </option>
    <option name="WRITE_IDENTIFIER_UNDER_CARET_ATTRIBUTES">
      <value>
        <option name="BACKGROUND" value="{panel}" />
        <option name="ERROR_STRIPE_COLOR" value="{accent}" />
      </value>
    </option>
  </attributes>
</scheme>
"""


# ── Windows Terminal (.json) ──────────────────────────────────────────────────

def generate_windows_terminal(t: dict, name: str) -> str:
    theme = {
        "name": f"APT {name.title()}",
        "background":         t["background"],
        "foreground":         t["textPrimary"],
        "cursorColor":        t["accent"],
        "selectionBackground": t["selection"],
        "black":              t["background"],
        "red":                t["keyword"],
        "green":              t["string"],
        "yellow":             t["number"],
        "blue":               t["accentSecondary"],
        "purple":             t["comment"],
        "cyan":               t["accent"],
        "white":              t["textMuted"],
        "brightBlack":        t["surface"],
        "brightRed":          t["keyword"],
        "brightGreen":        t["highlight"],
        "brightYellow":       t["number"],
        "brightBlue":         t["accent"],
        "brightPurple":       t["accentSecondary"],
        "brightCyan":         t["highlight"],
        "brightWhite":        t["textPrimary"],
    }
    return json.dumps(theme, indent=2)


# ── Alacritty (.toml) ─────────────────────────────────────────────────────────

def generate_alacritty(t: dict, name: str) -> str:
    return f"""\
# APT {name.title()} — Alacritty color theme
# Generated by APTlantis Theme Forge

[colors.primary]
background = "{t['background']}"
foreground = "{t['textPrimary']}"

[colors.cursor]
cursor = "{t['accent']}"
text   = "{t['background']}"

[colors.selection]
background = "{t['selection']}"
text       = "{t['textPrimary']}"

[colors.normal]
black   = "{t['background']}"
red     = "{t['keyword']}"
green   = "{t['string']}"
yellow  = "{t['number']}"
blue    = "{t['accentSecondary']}"
magenta = "{t['comment']}"
cyan    = "{t['accent']}"
white   = "{t['textMuted']}"

[colors.bright]
black   = "{t['surface']}"
red     = "{t['keyword']}"
green   = "{t['highlight']}"
yellow  = "{t['number']}"
blue    = "{t['accent']}"
magenta = "{t['accentSecondary']}"
cyan    = "{t['highlight']}"
white   = "{t['textPrimary']}"
"""


# ── Web tokens (.json) ───────────────────────────────────────────────────────

def generate_web_tokens(t: dict, name: str) -> str:
    """Emit the structural UI tokens as JSON for consumption by page generators."""
    web = {
        "ecosystem":       name,
        "background":      t["background"],
        "surface":         t["surface"],
        "panel":           t["panel"],
        "border":          t["border"],
        "selection":       t["selection"],
        "lineHighlight":   t["lineHighlight"],
        "accent":          t["accent"],
        "accentSecondary": t["accentSecondary"],
        "highlight":       t["highlight"],
        "textPrimary":     t["textPrimary"],
        "textMuted":       t["textMuted"],
    }
    return json.dumps(web, indent=2)


# ── Utilities ─────────────────────────────────────────────────────────────────

def ecosystem_name(palette_path: Path) -> str:
    """apt-python-logo-palette.txt → 'python'"""
    parts = palette_path.stem.split("-")  # ['apt', 'python', 'logo', 'palette']
    try:
        start = parts.index("apt") + 1
        end   = parts.index("logo")
        return "-".join(parts[start:end])
    except ValueError:
        return parts[1] if len(parts) > 1 else palette_path.stem


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    palette_files = sorted(PALETTES_DIR.glob("*.txt"))
    if not palette_files:
        print(f"No palette files found in {PALETTES_DIR}/", file=sys.stderr)
        sys.exit(1)

    for subdir in ["vscode", "notepadpp", "jetbrains", "terminal/windows", "terminal/alacritty", "web"]:
        (THEMES_DIR / subdir).mkdir(parents=True, exist_ok=True)

    ok = 0
    for palette_path in palette_files:
        name = ecosystem_name(palette_path)
        try:
            colors = parse_palette(palette_path)
        except Exception as e:
            print(f"  SKIP  {palette_path.name}: parse error — {e}", file=sys.stderr)
            continue

        if len(colors) < 8:
            print(f"  SKIP  {palette_path.name}: only {len(colors)} colors", file=sys.stderr)
            continue

        tokens = assign_tokens(colors)

        (THEMES_DIR / "vscode"              / f"apt-{name}-theme.json").write_text(generate_vscode(tokens, name),           encoding="utf-8")
        (THEMES_DIR / "notepadpp"           / f"apt-{name}-theme.xml" ).write_text(generate_notepadpp(tokens, name),        encoding="utf-8")
        (THEMES_DIR / "jetbrains"           / f"apt-{name}-theme.icls").write_text(generate_jetbrains(tokens, name),        encoding="utf-8")
        (THEMES_DIR / "terminal" / "windows"  / f"apt-{name}-theme.json").write_text(generate_windows_terminal(tokens, name), encoding="utf-8")
        (THEMES_DIR / "terminal" / "alacritty" / f"apt-{name}-theme.toml").write_text(generate_alacritty(tokens, name),     encoding="utf-8")
        (THEMES_DIR / "web"                    / f"apt-{name}-tokens.json").write_text(generate_web_tokens(tokens, name),    encoding="utf-8")

        print(f"  OK    {name}")
        ok += 1

    print(f"\n{ok} theme sets -> {THEMES_DIR}/")


if __name__ == "__main__":
    # Gen 2 is the active entry point. Retain the old functions and artifacts as
    # historical evidence, but never run the 16-color batch from this command.
    from generate_theme32 import main as main32
    main32()
