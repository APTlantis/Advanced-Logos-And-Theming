"""Artwork generation identity, independent of the engine package version."""
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

PREFIXES = {1: "apt", 2: "dnf", 3: "rpm", 4: "yum", 5: "eopkg"}


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def split_name(value):
    normalized = slug(value)
    if normalized == "aptlantis" or normalized.startswith("aptlantis-"):
        normalized = normalized[len("aptlantis"):].lstrip("-")
    first, _, rest = normalized.partition("-")
    version = next((v for v, p in PREFIXES.items() if p == first), None)
    if version:
        normalized = rest
        if normalized.split("-", 1)[0] in (*PREFIXES.values(), "aptlantis"):
            raise ValueError("Stacked theme prefixes are invalid: " + value)
    if not normalized:
        raise ValueError("Theme name must contain a nonempty theme slug")
    return version, normalized


@dataclass(frozen=True)
class ThemeIdentity:
    version: int
    prefix: str
    slug: str
    evidence: tuple

    @property
    def key(self):
        return self.prefix + "-" + self.slug

    def record(self):
        return {**asdict(self), "evidence": list(self.evidence)}


def resolve_identity(name, version=None, source=None, imported=None):
    evidence = []
    def add(label, value):
        if value is not None:
            if type(value) is not int or value not in PREFIXES:
                raise ValueError("Invalid theme version in " + label)
            evidence.append({"source": label, "version": value})
    def named(label, value):
        inferred, _ = split_name(value)
        add(label, inferred)
    def metadata(label, data):
        if not isinstance(data, dict):
            raise ValueError("Invalid identity metadata in " + label)
        if data.get("name"):
            named(label + ".name", data["name"])
        identity = data.get("theme_identity", {})
        if not isinstance(identity, dict):
            raise ValueError("Invalid theme_identity in " + label)
        add(label + ".theme_identity", identity.get("version"))
        if identity.get("prefix"):
            prefix_version = next((v for v, p in PREFIXES.items() if p == identity["prefix"]), None)
            if prefix_version is None:
                raise ValueError("Unknown theme prefix in " + label)
            add(label + ".prefix", prefix_version)
    add("--theme-version", version)
    inferred, theme_slug = split_name(name)
    add("name", inferred)
    if imported:
        metadata("imported.theme", imported.get("theme", {}))
    if source is not None:
        source = Path(source)
        named("source.filename", source.stem)
        parent = source.parent.parent if source.parent.name == "source" else source.parent
        if parent.name:
            named("source.directory", parent.name)
        if (parent / "run.json").is_file():
            metadata("source.run", json.loads((parent / "run.json").read_text(encoding="utf-8-sig")))
    versions = {item["version"] for item in evidence}
    if len(versions) > 1:
        raise ValueError("Conflicting theme versions: " + json.dumps(evidence))
    if not versions:
        raise ValueError("Cannot determine theme version; supply --theme-version 1, 2, 3, 4 or 5")
    resolved = versions.pop()
    return ThemeIdentity(resolved, PREFIXES[resolved], theme_slug, tuple(evidence))
