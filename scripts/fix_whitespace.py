"""Script to remove trailing whitespace from Python files."""

import os
from pathlib import Path


def fix_file_whitespace(file_path: Path) -> None:
    """Remove trailing whitespace from a file.

    Args:
        file_path: Path to the file to fix
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Remove trailing whitespace from each line
        fixed_lines = [line.rstrip() + '\n' for line in lines]

        # Remove any trailing newlines at end of file
        while fixed_lines and fixed_lines[-1].isspace():
            fixed_lines.pop()

        # Add single newline at end of file if missing
        if fixed_lines and not fixed_lines[-1].endswith('\n'):
            fixed_lines[-1] += '\n'

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)

        print(f"Fixed whitespace in {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")


def main():
    """Find and fix all Python files in the project."""
    project_root = Path(__file__).parent.parent
    python_files = list(project_root.rglob("*.py"))

    print(f"Found {len(python_files)} Python files")
    for file_path in python_files:
        fix_file_whitespace(file_path)


if __name__ == "__main__":
    main()
