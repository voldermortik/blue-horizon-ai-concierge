"""Script to vacuum ChromaDB database."""

import subprocess
from pathlib import Path

from blue_horizon.utils.logger import log, LogLevel


def vacuum_chroma_db():
    """
    Vacuum the ChromaDB database to clean up unused space and optimize the database structure.
    """
    persist_dir = Path("vector_store")
    if not persist_dir.exists():
        log(f"ChromaDB directory not found at: {persist_dir}", LogLevel.ERROR)
        return False

    log(f"Vacuuming ChromaDB at: {persist_dir}", LogLevel.ON)
    try:
        result = subprocess.run(
            [
                "chroma",
                "utils",
                "vacuum",
                "--force",
                "--path",
                str(persist_dir.absolute()),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        log(f"Vacuum output: {result.stdout}", LogLevel.ON)
        if result.stderr:
            log(f"Vacuum warnings: {result.stderr}", LogLevel.WARNING)
        return True
    except subprocess.CalledProcessError as e:
        log(f"Error during vacuum: {e.stderr}", LogLevel.ERROR)
        return False
    except (FileNotFoundError, PermissionError, OSError) as e:
        log(f"File system error during vacuum: {e}", LogLevel.ERROR)
        return False


if __name__ == "__main__":
    vacuum_chroma_db()
