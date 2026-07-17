"""Pluggable object storage: local disk for dev, S3 for production.

Selected by STORAGE_BACKEND. The rest of the app only depends on this
interface, so switching to S3 needs no code changes elsewhere.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod

from fastapi.responses import FileResponse, RedirectResponse, Response

from .config import get_settings

settings = get_settings()


class Storage(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes, content_type: str) -> None: ...

    @abstractmethod
    def exists(self, key: str) -> bool: ...

    @abstractmethod
    def read(self, key: str) -> bytes: ...

    @abstractmethod
    def response(self, key: str, content_type: str) -> Response:
        """Return a FastAPI response that serves the object efficiently."""


class LocalStorage(Storage):
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def _path(self, key: str) -> str:
        return os.path.join(self.base_dir, key)

    def save(self, key: str, data: bytes, content_type: str) -> None:
        os.makedirs(self.base_dir, exist_ok=True)
        with open(self._path(key), "wb") as f:
            f.write(data)

    def exists(self, key: str) -> bool:
        return os.path.exists(self._path(key))

    def read(self, key: str) -> bytes:
        with open(self._path(key), "rb") as f:
            return f.read()

    def response(self, key: str, content_type: str) -> Response:
        return FileResponse(self._path(key), media_type=content_type)


class S3Storage(Storage):
    def __init__(self, bucket: str, region: str, endpoint_url: str = ""):
        import boto3  # imported lazily so local dev needs no boto3

        self.bucket = bucket
        self._client = boto3.client(
            "s3",
            region_name=region or None,
            endpoint_url=endpoint_url or None,
        )

    def save(self, key: str, data: bytes, content_type: str) -> None:
        self._client.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)

    def exists(self, key: str) -> bool:
        from botocore.exceptions import ClientError

        try:
            self._client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False

    def read(self, key: str) -> bytes:
        obj = self._client.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read()

    def response(self, key: str, content_type: str) -> Response:
        # Redirect to a short-lived presigned URL — avoids proxying bytes.
        url = self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=300,
        )
        return RedirectResponse(url)


def _build_storage() -> Storage:
    if settings.storage_backend == "s3":
        return S3Storage(settings.s3_bucket, settings.s3_region, settings.s3_endpoint_url)
    return LocalStorage(settings.upload_dir)


_storage: Storage | None = None


def get_storage() -> Storage:
    global _storage
    if _storage is None:
        _storage = _build_storage()
    return _storage
