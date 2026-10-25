"""An authoritative artifact inventory shared by writers and their references."""
import hashlib
import json
from pathlib import Path, PurePosixPath
from .identity import resolve_identity, slug

SCHEMA = "aptlantis.artifact-manifest.v2"
SIYUAN = {"theme.css", "theme.json", "README.md", "icon.png", "preview.png"}


class ArtifactNames:
    def __init__(self, identity, target, name):
        self.identity, self.target = identity, target
        self.stem = identity.key + "-" + slug(target)
        native = slug(name)
        self.primary = {
            "windows_terminal": "windows-terminal.json", "alacritty": native + ".toml",
            "notepad_plus_plus": native + ".xml", "sublime_text": native + ".sublime-color-scheme",
            "typora": native + ".css", "powerpoint": native + ".xml",
            "markdown": "markdown.css", "codemirror5": "theme.css", "codemirror6": "theme.mjs",
            "website": "theme.css", "syntax_highlighting": "prism.css",
            "data_visualization": native + ".mplstyle", "siyuan": "package.zip",
        }.get(target)
        self.paths, self.roles, self.exceptions = {}, {}, {}

    def __call__(self, logical):
        if logical in self.paths:
            return self.paths[logical]
        path = PurePosixPath(logical)
        if path.name != logical or logical in (".", ".."):
            raise ValueError("Artifact keys must be top-level filenames: " + logical)
        fixed = (self.target == "siyuan" and logical in SIYUAN) or (self.target == "kmindz" and logical == "KMINDS.json")
        role = "primary" if logical == self.primary or logical == "KMINDS.json" else slug(path.stem)
        if role.startswith(slug(self.target) + "-"):
            role = role[len(slug(self.target)) + 1:]
        if self.target == "powerpoint" and path.suffix in (".pptx", ".potx"):
            role = "sample" if path.suffix == ".pptx" else "template"
        destination = logical if fixed else self.stem + ("" if role == "primary" else "-" + role) + path.suffix.lower()
        if destination in self.paths.values():
            raise ValueError("Artifact naming collision: " + destination)
        self.paths[logical], self.roles[logical] = destination, role
        if fixed:
            self.exceptions[logical] = "SiYuan native package member" if self.target == "siyuan" else "Supplied Kmindz native package contract"
        return destination

    def finish(self, directory, result, name):
        actual = {p.name for p in directory.iterdir() if p.is_file()}
        if actual != set(self.paths.values()):
            raise ValueError("Artifact inventory mismatch: " + repr(actual.symmetric_difference(self.paths.values())))
        records = [{"file": file, "role": self.roles[key], "logical_name": key,
                    "fixed_name_reason": self.exceptions.get(key),
                    "sha256": hashlib.sha256((directory / file).read_bytes()).hexdigest()}
                   for key, file in sorted(self.paths.items())]
        manifest = self.stem + "-files.json"
        if (directory / manifest).exists():
            raise ValueError("Artifact naming collision: " + manifest)
        (directory / manifest).write_text(json.dumps({"schema": SCHEMA, "target": self.target,
            "theme": name, "theme_identity": self.identity.record(), "stem": self.stem,
            "files": records}, indent=2) + "\n", encoding="utf-8")
        result["artifact_manifest"] = {"manifest": manifest, "files": records}


def artifact_names(result):
    return result["_artifact_names"]


def artifact_stem(name, target, theme_version=None):
    return resolve_identity(name, theme_version).key + "-" + slug(target)


def artifact_file(run, target, logical):
    """Locate a new manifest artifact or a historical generic entry point."""
    run = Path(run)
    metadata = json.loads((run / 'run.json').read_text(encoding='utf-8-sig'))
    if 'artifact_manifests' not in metadata:
        return run / target / logical
    relative = metadata['artifact_manifests'][target]
    if Path(relative).parts != (target, Path(relative).name) or '\\' in relative:
        raise ValueError('Unsafe artifact manifest path')
    manifest = json.loads((run / relative).read_text(encoding='utf-8-sig'))
    if manifest.get('schema') != SCHEMA or manifest.get('target') != target:
        raise ValueError('Unexpected artifact manifest')
    matches = [r['file'] for r in manifest['files'] if r['logical_name'] == logical]
    if len(matches) != 1 or PurePosixPath(matches[0]).name != matches[0] or '\\' in matches[0] or matches[0] in ('.', '..'):
        raise ValueError('Missing, duplicate or unsafe artifact: ' + logical)
    return run / target / matches[0]
