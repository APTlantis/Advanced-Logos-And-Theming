
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlsplit
from collections import Counter
import csv
import html
import re

ROOT = Path(r"T:\MAN-PAGES\linuxcommandlibrary.com")
DRY_RUN = True

stats = Counter()
broken_links = []

def replace_html(match):
    """Convert known inline HTML without parsing the whole Markdown document."""
    soup = BeautifulSoup(match.group(0), "html.parser")
    tag = soup.find()

    if tag is None:
        return match.group(0)

    if tag.name == "span" and "code" in tag.get("class", []):
        value = html.unescape(tag.get_text())
        value = value.replace("\xa0", " ")
        value = re.sub(r"\\([\[\]`])", r"\1", value)
        ticks = "`" * (max(
            (len(x) for x in re.findall(r"`+", value)),
            default=0
        ) + 1)
        return f"{ticks}{value}{ticks}"

    if tag.name == "a":
        label = tag.get_text()
        href = tag.get("href", "")

        # Heading anchors contain only their own titles.
        if tag.get("id") and "#" in href:
            return label

        if href:
            return f"[{label}]({href})"

        return label

    return match.group(0)


def normalize_links(text, source):
    """Rewrite local HTML paths when corresponding MD files exist."""

    pattern = re.compile(
        r'(?<!!)\[([^\]\n]+)\]\(([^)\s]+)(\s+"[^"]*")?\)'
    )

    def rewrite(match):
        label, url, title = match.groups()
        title = title or ""

        parsed = urlsplit(url)

        # Preserve external URLs and fragment-only links.
        if parsed.scheme or parsed.netloc or not parsed.path:
            return match.group(0)

        if not parsed.path.lower().endswith(".html"):
            return match.group(0)

        new_path = parsed.path[:-5] + ".md"
        candidate = source.parent / unquote(new_path)

        if not candidate.is_file():
            broken_links.append({
                "source": str(source.relative_to(ROOT)),
                "target": url
            })
            stats["unresolved"] += 1
            return match.group(0)

        new_url = new_path

        if parsed.query:
            new_url += "?" + parsed.query

        if parsed.fragment:
            new_url += "#" + parsed.fragment

        stats["links_fixed"] += 1
        return f"[{label}]({new_url}{title})"

    return pattern.sub(rewrite, text)


def normalize(text, source):

    # Convert HTML code spans into Markdown code.
    text = re.sub(
        r'<span\b[^>]*class=["\'][^"\']*\bcode\b[^"\']*["\'][^>]*>.*?</span>',
        replace_html,
        text,
        flags=re.I | re.S
    )

    # Convert inline HTML anchors.
    text = re.sub(
        r'<a\b[^>]*>.*?</a>',
        replace_html,
        text,
        flags=re.I | re.S
    )

    # Decode nonbreaking spaces outside code.
    text = text.replace("\xa0", " ")

    # Rewrite links to local Markdown documents.
    text = normalize_links(text, source)

    # Reduce excessive empty lines.
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    return text.strip() + "\n"


files = sorted(ROOT.rglob("*.md"))

for file in files:
    try:
        original = file.read_text(encoding="utf-8-sig")
        cleaned = normalize(original, file)

        if cleaned != original:
            stats["changed"] += 1

            if not DRY_RUN:
                file.write_text(cleaned, encoding="utf-8")
        else:
            stats["unchanged"] += 1

    except Exception as exc:
        stats["errors"] += 1
        print(f"ERROR: {file}: {exc}")


report = Path("unresolved_command_links.csv")

with report.open("w", newline="", encoding="utf-8") as out:
    writer = csv.DictWriter(
        out, fieldnames=["source", "target"]
    )
    writer.writeheader()
    writer.writerows(broken_links)


print(f"Files:           {len(files)}")
print(f"Changed:         {stats['changed']}")
print(f"Unchanged:       {stats['unchanged']}")
print(f"Links corrected: {stats['links_fixed']}")
print(f"Unresolved:      {stats['unresolved']}")
print(f"Errors:          {stats['errors']}")
print(f"Dry run:         {DRY_RUN}")
print(f"Report:          {report.resolve()}")
