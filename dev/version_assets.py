"""Write immutable CSS/JS snapshots and point HTML at their content-based names.

Run after editing CSS or JavaScript: python dev/version_assets.py
Validate without modifying files: python dev/version_assets.py --check
No package installation or site build system is required. Old snapshots stay
available for visitors whose HTML is cached. Legacy styles.css is preserved.
"""
from pathlib import Path
import argparse
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("assets/site.css", "assets/contact.css", "assets/contact-config.js", "assets/contact.js")
PAGES = ("index.html", "contact.html")


def normalized(path):
    return path.read_text(encoding="utf-8").encode("utf-8")


def snapshots(root=ROOT):
    result = {}
    for source in SOURCES:
        path = Path(source)
        data = normalized(root / path)
        digest = hashlib.sha256(data).hexdigest()[:12]
        destination = path.with_name(f"{path.stem}.{digest}{path.suffix}").as_posix()
        result[source] = (destination, data)
    return result


def rewrite(html, mapping):
    def replace(match):
        attribute, path = match.groups()
        canonical = re.sub(r"\.[a-f0-9]{12}(?=\.(?:css|js)$)", "", path)
        # Migration from the original shared URL; preserve the file itself.
        if canonical == "assets/styles.css":
            canonical = "assets/site.css"
        if canonical in mapping:
            path = mapping[canonical][0]
        return f'{attribute}="{path}"'
    return re.sub(r'(href|src)="([^"?#]+\.(?:css|js))"', replace, html)


def version_assets(root=ROOT, check=False):
    mapping = snapshots(root)
    problems = []
    for destination, data in mapping.values():
        path = root / destination
        if path.exists() and normalized(path) != data:
            raise ValueError(f"Refusing to overwrite an immutable snapshot: {destination}")
        if not path.exists():
            if check:
                problems.append(f"Missing snapshot: {destination}")
            else:
                path.write_bytes(data)
    for name in PAGES:
        path = root / name
        current = path.read_text(encoding="utf-8")
        updated = rewrite(current, mapping)
        if updated != current:
            if check:
                problems.append(f"Outdated asset references: {name}")
            else:
                path.write_bytes(updated.encode("utf-8"))
    if problems:
        raise ValueError("\n".join(problems) + "\nRun python dev/version_assets.py")
    return mapping


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for source, (destination, _) in version_assets(check=args.check).items():
        print(f"{source} -> {destination}")
