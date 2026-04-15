"""Клиент S3/MinIO для работы с файловым хранилищем."""

import uuid
from pathlib import Path

import aiobotocore.session
from aiobotocore.session import AioBaseClient

from app.config import settings

_s3_client: AioBaseClient | None = None


async def get_s3_client() -> AioBaseClient:
    """Создаёт новый клиент S3 на каждый вызов (aiobotocore контекстный)."""
    session = aiobotocore.session.get_session()
    return session.create_client(
        "s3",
        region_name=settings.s3_region,
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )


class StorageService:
    """Сервис загрузки и удаления файлов в S3."""

    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
    ALLOWED_DOC_TYPES = {"application/pdf", "image/jpeg", "image/png"}
    MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10 MB
    MAX_DOC_SIZE = 20 * 1024 * 1024     # 20 MB

    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        bucket: str = "",
        subfolder: str = "",
    ) -> str:
        """
        Загружает файл в S3 и возвращает публичный URL.

        Args:
            file_data:    байты файла
            filename:     оригинальное имя файла (для расширения)
            content_type: MIME-тип
            bucket:       имя бакета (по умолчанию — media)
            subfolder:    подпапка внутри бакета

        Returns:
            Публичный URL загруженного файла
        """
        target_bucket = bucket or settings.s3_bucket_media
        ext = Path(filename).suffix.lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"
        key = f"{subfolder}/{unique_name}" if subfolder else unique_name

        async with await get_s3_client() as client:
            await client.put_object(
                Bucket=target_bucket,
                Key=key,
                Body=file_data,
                ContentType=content_type,
            )

        return f"{settings.s3_public_url}/{key}"

    async def delete_file(self, key: str, bucket: str = "") -> None:
        """Удаляет файл из S3."""
        target_bucket = bucket or settings.s3_bucket_media
        async with await get_s3_client() as client:
            await client.delete_object(Bucket=target_bucket, Key=key)

    async def generate_presigned_url(
        self,
        key: str,
        bucket: str = "",
        expires_in: int = 3600,
    ) -> str:
        """Генерирует временную ссылку для приватных файлов."""
        target_bucket = bucket or settings.s3_bucket_docs
        async with await get_s3_client() as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": target_bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        return url


storage = StorageService()
