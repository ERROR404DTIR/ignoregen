#!/usr/bin/env python3
"""ignoregen - generate a .gitignore from built-in templates. One file, zero dependencies."""
import argparse
import difflib
import os
import sys

__version__ = "1.0.0"

TEMPLATES = {
    "python": ["__pycache__/", "*.py[cod]", "*.egg-info/", "dist/", "build/", ".venv/", "venv/",
               ".pytest_cache/", ".mypy_cache/", ".ruff_cache/", ".coverage", "htmlcov/"],
    "node": ["node_modules/", "npm-debug.log*", "yarn-error.log*", "dist/", ".next/", ".nuxt/",
             "coverage/", ".parcel-cache/"],
    "java": ["*.class", "*.jar", "*.war", "target/", ".gradle/", "build/", "out/"],
    "go": ["*.exe", "*.test", "*.out", "vendor/", "bin/"],
    "rust": ["target/", "**/*.rs.bk"],
    "c": ["*.o", "*.obj", "*.a", "*.so", "*.dylib", "*.exe", "*.out", "build/"],
    "dotnet": ["bin/", "obj/", "*.user", "*.suo", ".vs/", "packages/"],
    "php": ["vendor/", "composer.phar", ".phpunit.result.cache"],
    "ruby": ["*.gem", ".bundle/", "vendor/bundle/", "log/", "tmp/"],
    "macos": [".DS_Store", ".AppleDouble", ".LSOverride", "._*"],
    "windows": ["Thumbs.db", "ehthumbs.db", "Desktop.ini", "$RECYCLE.BIN/"],
    "linux": ["*~", ".directory", ".Trash-*", ".nfs*"],
    "vscode": [".vscode/*", "!.vscode/settings.json", "!.vscode/extensions.json", "!.vscode/launch.json"],
    "jetbrains": [".idea/", "*.iml"],
    "env": [".env", ".env.*", "!.env.example", "*.pem", "*.key"],
    "logs": ["*.log", "logs/"],
}

ALIASES = {
    "py": "python", "js": "node", "ts": "node", "typescript": "node", "javascript": "node",
    "mac": "macos", "osx": "macos", "win": "windows", "cpp": "c", "csharp": "dotnet",
    "idea": "jetbrains", "code": "vscode", "rb": "ruby", "golang": "go",
}


def resolve(name):
    key = name.lower().lstrip(".")
    key = ALIASES.get(key, key)
    if key not in TEMPLATES:
        hint = difflib.get_close_matches(key, list(TEMPLATES) + list(ALIASES), n=1)
        extra = f" - did you mean '{hint[0]}'?" if hint else " (see --list)"
        raise SystemExit(f"ignoregen: unknown template '{name}'{extra}")
    return key


def build(names, existing=()):
    seen = set(existing)
    out = []
    for name in dict.fromkeys(resolve(n) for n in names):
        lines = [line for line in TEMPLATES[name] if line not in seen]
        if not lines:
            continue
        seen.update(lines)
        out.append(f"# {name}")
        out.extend(lines)
        out.append("")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="ignoregen", description="Generate a .gitignore from built-in templates.")
    ap.add_argument("names", nargs="*", help="templates, e.g. python node macos vscode")
    ap.add_argument("-l", "--list", action="store_true", help="list available templates")
    ap.add_argument("-o", "--output", metavar="FILE", help="write to FILE instead of stdout")
    ap.add_argument("-a", "--append", action="store_true", help="with -o: only add lines missing from FILE")
    ap.add_argument("-f", "--force", action="store_true", help="with -o: overwrite FILE if it exists")
    ap.add_argument("--version", action="version", version=__version__)
    args = ap.parse_args(argv)

    if args.list:
        for key in sorted(TEMPLATES):
            print(key)
        return 0
    if not args.names:
        print("ignoregen: give at least one template name (see --list)", file=sys.stderr)
        return 2

    if not args.output:
        print(build(args.names), end="")
        return 0

    path = args.output
    if os.path.exists(path) and args.append:
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        have = {line.strip() for line in content.splitlines()}
        text = build(args.names, have)
        if not text:
            print("ignoregen: nothing to add, file already covers these templates")
            return 0
        prefix = "" if not content or content.endswith("\n") else "\n"
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(prefix + text)
        print(f"ignoregen: appended to {path}")
        return 0
    if os.path.exists(path) and not args.force:
        print(f"ignoregen: {path} exists - use --append or --force", file=sys.stderr)
        return 2
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(build(args.names))
    print(f"ignoregen: wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
