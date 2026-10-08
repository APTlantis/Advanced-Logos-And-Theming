"""Native editor contracts; editor color schemes do not replace application chrome."""
import json
import xml.etree.ElementTree as ET


def export_editor(result, directory, name):
    from .targets import slug
    tokens = result["tokens"]
    fallback = {"invalid": "error", "diff_added": "success", "diff_deleted": "error",
                "diff_changed": "warning", "tag": "keyword", "attribute": "type",
                "escape": "constant", "label": "function"}
    def h(key):
        return tokens[key if key in tokens else fallback[key]]["hex"]
    if result["target"] == "sublime_text":
        globals_map = {"background": "background", "foreground": "foreground",
                       "caret": "foreground", "line_highlight": "panel", "gutter": "panel",
                       "gutter_foreground": "muted", "selection": "selection",
                       "selection_foreground": "selection_text", "selection_border": "border",
                       "inactive_selection": "selection", "inactive_selection_foreground": "selection_text",
                       "find_highlight": "selection", "find_highlight_foreground": "selection_text",
                       "accent": "primary", "line_diff_added": "diff_added",
                       "line_diff_deleted": "diff_deleted", "line_diff_modified": "diff_changed"}
        scopes = {"comment": "comment", "string": "string", "constant": "constant",
                  "constant.numeric": "number", "keyword": "keyword", "keyword.operator": "operator",
                  "entity.name.function, support.function": "function",
                  "entity.name.type, support.type, support.class": "type",
                  "entity.name.tag": "tag", "entity.other.attribute-name": "attribute",
                  "constant.character.escape": "escape", "entity.name.label": "label",
                  "invalid": "invalid", "markup.inserted": "diff_added",
                  "markup.deleted": "diff_deleted", "markup.changed": "diff_changed"}
        scheme = {"name": name, "globals": {key: h(token) for key, token in globals_map.items()},
                  "rules": [{"scope": scope, "foreground": h(token)} for scope, token in scopes.items()]}
        (directory / (slug(name) + ".sublime-color-scheme")).write_text(
            json.dumps(scheme, indent=2) + "\n", encoding="utf-8")
    else:
        root = ET.Element("NotepadPlus")
        lexers = ET.SubElement(root, "LexerStyles")
        # Style names and IDs follow the official shipped theme contract.
        python = [(0, "DEFAULT", "foreground"), (1, "COMMENTLINE", "comment"),
                  (2, "NUMBER", "number"), (3, "STRING", "string"), (4, "CHARACTER", "string"),
                  (5, "KEYWORDS", "keyword"), (6, "TRIPLE", "string"), (7, "TRIPLEDOUBLE", "string"),
                  (8, "CLASSNAME", "type"), (9, "DEFNAME", "function"), (10, "OPERATOR", "operator"),
                  (11, "IDENTIFIER", "foreground"), (12, "COMMENTBLOCK", "comment"),
                  (13, "STRINGEOL", "invalid"), (14, "BUILTINS", "constant"),
                  (15, "DECORATOR", "label"), (16, "F STRING", "string"), (17, "F CHARACTER", "string"),
                  (18, "F TRIPLE", "string"), (19, "F TRIPLEDOUBLE", "string"), (20, "ATTRIBUTE", "attribute")]
        cpp = [(11, "DEFAULT", "foreground"), (9, "PREPROCESSOR", "keyword"),
               (5, "INSTRUCTION WORD", "keyword"), (16, "TYPE WORD", "type"),
               (4, "NUMBER", "number"), (6, "STRING", "string"), (20, "STRINGRAW", "string"),
               (7, "CHARACTER", "string"), (10, "OPERATOR", "operator"), (13, "VERBATIM", "string"),
               (14, "REGEX", "string"), (1, "COMMENT", "comment"), (2, "COMMENT LINE", "comment"),
               (3, "COMMENT DOC", "comment"), (15, "COMMENT LINE DOC", "comment"),
               (17, "COMMENT DOC KEYWORD", "keyword"), (18, "COMMENT DOC KEYWORD ERROR", "invalid"),
               (23, "PREPROCESSOR COMMENT", "comment"), (24, "PREPROCESSOR COMMENT DOC", "comment")]
        json_styles = [(0, "DEFAULT", "foreground"), (1, "NUMBER", "number"), (2, "STRING", "string"),
                       (3, "STRINGEOL", "invalid"), (4, "PROPERTYNAME", "attribute"),
                       (5, "ESCAPESEQUENCE", "escape"), (6, "LINECOMMENT", "comment"),
                       (7, "BLOCKCOMMENT", "comment"), (8, "OPERATOR", "operator"),
                       (9, "URI", "primary"), (10, "COMPACTIRI", "primary"),
                       (11, "KEYWORD", "constant"), (12, "LDKEYWORD", "keyword"), (13, "ERROR", "invalid")]
        for lexer, desc, styles in (("python", "Python", python), ("cpp", "C++", cpp),
                                    ("json", "JSON", json_styles)):
            node = ET.SubElement(lexers, "LexerType", name=lexer, desc=desc, ext="")
            for ident, label, token in styles:
                attrs = {"name": label, "styleID": str(ident), "fgColor": h(token)[1:],
                         "bgColor": h("background")[1:], "fontName": "", "fontStyle": "0", "fontSize": ""}
                keyword_class = {"python": {5: "instre1", 14: "instre2"},
                                 "cpp": {5: "instre1", 16: "type1"},
                                 "json": {11: "instre1", 12: "instre2"}}[lexer].get(ident)
                if keyword_class:
                    attrs["keywordClass"] = keyword_class
                ET.SubElement(node, "WordsStyle", attrs)
        globals_node = ET.SubElement(root, "GlobalStyles")
        styles = [("Default Style", 32, "foreground", "background"),
                  ("Indent guideline style", 37, "border", "background"),
                  ("Brace highlight style", 34, "primary", "background"),
                  ("Bad brace colour", 35, "invalid", "background"),
                  ("Current line background colour", 0, None, "panel"),
                  ("Selected text colour", 0, "selection_text", "selection"),
                  ("Caret colour", 2069, "foreground", None),
                  ("Line number margin", 33, "muted", "panel"),
                  ("Fold", 0, "muted", "panel"), ("Fold margin", 0, "panel", "panel"),
                  ("Find status: Not found", 0, "error", None),
                  ("Find status: Message", 0, "info", None),
                  ("Find status: Search end reached", 0, "success", None),
                  ("Change History modified", 0, "diff_changed", "diff_changed"),
                  ("Change History saved", 0, "diff_added", "diff_added")]
        for label, ident, fg, bg in styles:
            attrs = {"name": label, "styleID": str(ident)}
            if fg:
                attrs["fgColor"] = h(fg)[1:]
            if bg:
                attrs["bgColor"] = h(bg)[1:]
            ET.SubElement(globals_node, "WidgetStyle", attrs)
        ET.indent(root)
        ET.ElementTree(root).write(directory / (slug(name) + ".xml"), encoding="utf-8", xml_declaration=True)
    result["acceptance_limits"] = (
        "Sublime Text 4 editor color scheme; syntax scopes depend on installed syntax definitions; UI theme unchanged."
        if result["target"] == "sublime_text" else
        "Notepad++ editor globals and Python/C++/JSON lexers; other lexers and application dark-mode chrome require separate review. "
        "Selection foreground requires Notepad++ enableSelectFgColor.xml; without it syntax text retains its colors.")
