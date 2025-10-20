"""Storage adapter for object storage (S3/MinIO)."""

from typing import Optional
from minio import Minio
from minio.error import S3Error
import io


class StorageAdapter:
    """Storage adapter using MinIO/S3."""
    
    def __init__(self, config: dict):
        self.config = config
        self.client = Minio(
            endpoint=config["endpoint"],
            access_key=config["access_key"],
            secret_key=config["secret_key"],
            secure=config.get("secure", False)
        )
        self.bucket = config["bucket"]
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """Ensure the bucket exists."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            raise RuntimeError(f"Failed to create bucket {self.bucket}: {e}")
    
    async def store_file(
        self, 
        key: str, 
        content: bytes, 
        content_type: str
    ) -> None:
        """Store file in object storage."""
        try:
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=key,
                data=io.BytesIO(content),
                length=len(content),
                content_type=content_type
            )
        except S3Error as e:
            raise RuntimeError(f"Failed to store file {key}: {e}")
    
    async def get_file(self, key: str) -> bytes:
        """Get file from object storage."""
        try:
            response = self.client.get_object(self.bucket, key)
            return response.read()
        except S3Error as e:
            raise RuntimeError(f"Failed to get file {key}: {e}")
    
    async def delete_file(self, key: str) -> None:
        """Delete file from object storage."""
        try:
            self.client.remove_object(self.bucket, key)
        except S3Error as e:
            raise RuntimeError(f"Failed to delete file {key}: {e}")
    
    async def file_exists(self, key: str) -> bool:
        """Check if file exists in storage."""
        try:
            self.client.stat_object(self.bucket, key)
            return True
        except S3Error:
            return False
