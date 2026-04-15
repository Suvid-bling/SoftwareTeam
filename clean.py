#!/usr/bin/env python
"""Remove module-level triple-quoted docstrings from all .py files under sdeteam/."""

import re
from pathlib import Path

# Pattern: matches a module-level """...""" that appears right after
# optional shebang, encoding, and blank lines at the top of the file.
# It captures everything before the docstring, the docstring itself,
# and everything after.
MODULE_DOCSTRING_RE = re.compile(
    r"""
    ^                                   # start of file
    (                                   # group 1: preamble (shebang, encoding, blanks)
        (?:\#[^\n]*\n)*                 # zero or more comment lines
        \s*                             # optional whitespace/blank lines
    )
    \"{3}[\s\S]*?\"{3}\s*?\n?          # triple-quoted docstring (non-greedy)
    """,
    re.VERBOSE,
)


def clean_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    m = MODULE_DOCSTRING_RE.match(text)
    if not m:
        return False

    preamble_end = m.end()
    new_text = m.group(1).rstrip("\n") + "\n\n" + text[preamble_end:].lstrip("\n")
    if new_text == text:
        return False

    path.write_text(new_text, encoding="utf-8")
    return True


def main():
    root = Path("sdeteam")
    changed = []
    for py_file in sorted(root.rglob("*.py")):
        if clean_file(py_file):
            changed.append(str(py_file))

    if changed:
        print(f"Cleaned {len(changed)} file(s):")
        for f in changed:
            print(f"  {f}")
    else:
        print("No module-level docstrings found.")


if __name__ == "__main__":
    main()
