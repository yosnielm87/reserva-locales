#!/usr/bin/env python3
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT   = ROOT_DIR / "estructura_actual.txt"

# extensiones de código y archivos de config que nos interesan
CODE_EXT = {
    ".py", ".js", ".ts", ".html", ".css", ".scss", ".json", ".sql", ".yml", ".yaml",
    ".env", ".example", ".md", ".dockerignore", ".txt"
}
SKIP_DIRS = {
    "node_modules", "__pycache__", ".git", ".angular", "dist", "coverage",
    "postgres_data", ".venv", "venv", "venv312", ".venv312", ".idea", ".vscode"
}

def is_code(f: Path) -> bool:
    return f.suffix in CODE_EXT and f.is_file()

def walk_and_write(root: Path, fh, prefix=""):
    dirs = []
    files = []
    try:
        for p in sorted(root.iterdir(), key=lambda x: (x.is_file(), x.name)):
            if p.is_dir() and p.name not in SKIP_DIRS and not p.name.startswith("."):
                dirs.append(p)
            elif is_code(p):
                files.append(p)
    except PermissionError:
        return

    for i, file in enumerate(files):
        connector = "└── " if i == len(files) - 1 and not dirs else "├── "
        fh.write(f"{prefix}{connector}{file.name}\n")

    for i, dr in enumerate(dirs):
        connector = "└── " if i == len(dirs) - 1 else "├── "
        fh.write(f"{prefix}{connector}{dr.name}/\n")
        next_prefix = prefix + ("    " if i == len(dirs) - 1 else "│   ")
        walk_and_write(dr, fh, next_prefix)

def main():
    with OUTPUT.open("w", encoding="utf-8") as fh:
        fh.write(f"{ROOT_DIR.name}/\n")
        walk_and_write(ROOT_DIR, fh)
    print(f"✅ Árbol actualizado → {OUTPUT}")

if __name__ == "__main__":
    main()