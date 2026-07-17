"""Abstract storage backend interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class StorageBackend(ABC):
    """Abstract file storage interface.

    Implementations: LocalStorage (dev), SupabaseStorage (prod).
    """

    @abstractmethod
    async def upload(self, content: bytes, path: str) -> str:
        """Upload file content and return the storage path/URL."""
        ...

    @abstractmethod
    async def download(self, path: str) -> bytes:
        """Download file content by path."""
        ...

    @abstractmethod
    async def delete(self, path: str) -> None:
        """Delete a file by path."""
        ...

    @abstractmethod
    async def get_url(self, path: str) -> str:
        """Get a public or signed URL for the file."""
        ...
