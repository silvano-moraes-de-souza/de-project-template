"""Create a new project of the series from this template.

    uv run python scripts/new_project.py ../ecommerce-data-pipeline \
        --day 1 --title "E-commerce Data Pipeline" \
        --tagline "Batch ETL from raw orders to a PostgreSQL star schema" \
        --stack Python PostgreSQL Docker

Copies the template, renames the package, fills the README placeholders,
renders the banner, locks dependencies and makes the first commit with the
GitHub noreply identity (so the commit counts on the contribution graph).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent
SKIP = {".git", ".venv", ".pytest_cache", ".ruff_cache", "__pycache__", "uv.lock", ".coverage"}
TEXT_SUFFIXES = {".py", ".toml", ".md", ".yml", ".yaml", ".txt", ".cfg", ".example", ""}
GIT_NAME = "Silvano Moraes de Souza"
GIT_EMAIL = "134219085+silvano-moraes-de-souza@users.noreply.github.com"

TEMPLATE_ONLY = re.compile(r"<!-- template-only:start -->.*?<!-- template-only:end -->\n\n", re.S)

OLD_SLUG = "de-project-template"
OLD_PACKAGE = "project_template"
OLD_TITLE = "Project Template"
OLD_TAGLINE = "Starter layout for the 30 Days of Data & Software Engineering series"


def _ignore(_dir: str, names: list[str]) -> set[str]:
    return {n for n in names if n in SKIP}


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def create(dest: Path, day: int, title: str, tagline: str, stack: list[str]) -> Path:
    if dest.exists():
        sys.exit(f"{dest} already exists")
    slug = dest.name
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        sys.exit(f"folder name must be kebab-case, got {slug!r}")
    package = slug.replace("-", "_")

    shutil.copytree(TEMPLATE, dest, ignore=_ignore)
    (dest / "scripts" / "new_project.py").unlink()
    shutil.move(dest / "src" / OLD_PACKAGE, dest / "src" / package)

    replacements = [
        (OLD_TAGLINE, tagline),
        (OLD_TITLE, title),
        (OLD_SLUG, slug),
        (OLD_PACKAGE, package),
        ("day%20XX", f"day%20{day:02d}"),
        ("day XX", f"day {day:02d}"),
    ]
    for path in dest.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES or ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        new = TEMPLATE_ONLY.sub("", text)
        for old, value in replacements:
            new = new.replace(old, value)
        if new != text:
            path.write_text(new, encoding="utf-8", newline="\n")

    _run(
        [
            sys.executable,
            "scripts/animated_banner.py",
            "--kicker",
            f"30 DAYS · DAY {day:02d}",
            "--scene",
            "flow",
            "--title",
            title,
            "--tagline",
            tagline,
            "--stack",
            *stack,
        ],
        dest,
    )
    _run(["uv", "lock", "-q"], dest)
    _run(["git", "init", "-q", "-b", "main"], dest)
    _run(["git", "config", "user.name", GIT_NAME], dest)
    _run(["git", "config", "user.email", GIT_EMAIL], dest)
    _run(["git", "add", "-A"], dest)
    _run(["git", "commit", "-q", "-m", f"chore: scaffold {slug} from de-project-template"], dest)
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dest", type=Path)
    parser.add_argument("--day", type=int, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--tagline", required=True)
    parser.add_argument("--stack", nargs="*", default=[])
    args = parser.parse_args()
    print(create(args.dest.resolve(), args.day, args.title, args.tagline, args.stack))


if __name__ == "__main__":
    main()
