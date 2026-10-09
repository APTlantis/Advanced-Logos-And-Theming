"""Explicit maintainer-only download of pinned Prism assets; never run by generation."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

VERSION = "1.30.0"
BASE = f"https://raw.githubusercontent.com/PrismJS/prism/v{VERSION}/"
LANGUAGES = ["markup", "css", "javascript", "typescript", "python", "csharp", "cpp",
             "json", "sql", "bash", "powershell", "toml"]


def vendor():
    destination = Path(__file__).resolve().parents[1] / "apt_theme/vendor/prism"
    destination.mkdir(parents=True, exist_ok=True)
    metadata = json.loads(urlopen(BASE + "components.json", timeout=30).read())
    order = []

    def visit(language):
        if language in order:
            return
        component = metadata["languages"][language]
        for kind in ("require", "modify", "optional"):
            dependencies = component.get(kind, [])
            if isinstance(dependencies, str):
                dependencies = [dependencies]
            for dependency in dependencies:
                if kind != "optional" or dependency in LANGUAGES:
                    visit(dependency)
        order.append(language)

    for language in LANGUAGES:
        visit(language)
    paths = ["LICENSE", "components.json", "components/prism-core.js"]
    paths += [f"components/prism-{language}.js" for language in order]
    records = []
    for path in paths:
        raw = urlopen(BASE + path, timeout=30).read()
        filename = Path(path).name
        (destination / filename).write_bytes(raw)
        records.append({"file": filename, "url": BASE + path,
                        "sha256": hashlib.sha256(raw).hexdigest()})
    manifest = {"name": "Prism", "version": VERSION, "license": "MIT",
                "languages": LANGUAGES, "load_order": ["prism-core.js"] +
                [f"prism-{language}.js" for language in order], "files": records}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Vendored {len(records)} assets; grammars: {', '.join(order)}")


if __name__ == "__main__":
    vendor()
