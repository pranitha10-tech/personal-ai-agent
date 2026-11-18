from pathlib import Path


# ==================================================
# 1. RESOLVE PATH
# ==================================================

def resolve_path(path: str) -> Path:
    """
    Resolve a user-provided filesystem path.
    Supports absolute paths and paths relative to
    the current working directory.
    """

    return Path(path).expanduser().resolve()


# ==================================================
# 2. LIST DIRECTORY
# ==================================================

def list_directory(path: str) -> list:

    directory = resolve_path(path)

    if not directory.exists():
        raise FileNotFoundError("Directory does not exist.")

    if not directory.is_dir():
        raise NotADirectoryError("Path is not a directory.")

    return [
        {
            "name": item.name,
            "path": str(item),
            "type": "directory" if item.is_dir() else "file"
        }
        for item in directory.iterdir()
    ]


# ==================================================
# 3. GET FILE INFORMATION
# ==================================================

def get_file_info(path: str) -> dict:

    target = resolve_path(path)

    if not target.exists():
        raise FileNotFoundError("Path does not exist.")

    stat = target.stat()

    return {
        "name": target.name,
        "path": str(target),
        "type": "directory" if target.is_dir() else "file",
        "size_bytes": stat.st_size,
        "is_readable": target.is_file()
    }


# ==================================================
# 4. READ FILE
# ==================================================

def read_file(path: str) -> str:

    target = resolve_path(path)

    if not target.exists():
        raise FileNotFoundError("File does not exist.")

    if not target.is_file():
        raise IsADirectoryError("Path is not a file.")

    return target.read_text(encoding="utf-8")
