"""Supabase storage backend for production."""

from __future__ import annotations

from app.storage.base import StorageBackend
from app.config import settings


class SupabaseStorage(StorageBackend):
    """Supabase Storage backend for production file storage.

    Requires SUPABASE_URL and SUPABASE_SERVICE_KEY to be configured.
    """

    def __init__(self) -> None:
        if not settings.supabase_url or not settings.supabase_service_key:
            raise RuntimeError(
                "Supabase Storage requires SUPABASE_URL and SUPABASE_SERVICE_KEY"
            )
        from supabase import create_client
        self.client = create_client(settings.supabase_url, settings.supabase_service_key)
        self.bucket = settings.supabase_bucket

    async def upload(self, content: bytes, path: str) -> str:
        """Upload file to Supabase Storage."""
        self.client.storage.from_(self.bucket).upload(path, content)
        return path

    async def download(self, path: str) -> bytes:
        """Download file from Supabase Storage."""
        response = self.client.storage.from_(self.bucket).download(path)
        return response

    async def delete(self, path: str) -> None:
        """Delete file from Supabase Storage."""
        self.client.storage.from_(self.bucket).remove([path])

    async def get_url(self, path: str) -> str:
        """Get public URL from Supabase Storage."""
        result = self.client.storage.from_(self.bucket).get_public_url(path)
        return result
