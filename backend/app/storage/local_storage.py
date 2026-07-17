"""Local filesystem storage backend for development."""

from __future__ import annotations

from pathlib import Path

from app.storage.base import StorageBackend


class LocalStorage(StorageBackend):
    """Local filesystem storage for development."""

    def __init__(self, base_dir: str = "uploads") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def upload(self, content: bytes, path: str) -> str:
        """Store file to local filesystem."""
        full_path = self.base_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)
        return str(full_path)

    async def download(self, path: str) -> bytes:
        """Read file from local filesystem."""
        full_path = self.base_dir / path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return full_path.read_bytes()

    async def delete(self, path: str) -> None:
        """Delete file from local filesystem."""
        full_path = self.base_dir / path
        if full_path.exists():
            full_path.unlink()

    async def get_url(self, path: str) -> str:
        """Return local file path as URL."""
        return f"/uploads/{path}"
