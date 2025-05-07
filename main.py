
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from minio import Minio
from minio.error import S3Error
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import os
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel

from database import SessionLocal, engine
from models import Base, FileMetadata
from schemas import FileUploadResponse
from dependencies import get_current_user
from config import settings

app = FastAPI(title="File Upload Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MinIO client
minio_client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=False
)

# Create bucket if not exists
bucket_name = "uploads"
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}

ALLOWED_MIME_TYPES = {
    "application/dicom": "dcm",
    "image/jpeg": "jpg",
    "image/png": "png",
    "application/pdf": "pdf"
}

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    # Validate file type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported types: {list(ALLOWED_MIME_TYPES.keys())}"
        )

    file_id = str(uuid.uuid4())
    extension = ALLOWED_MIME_TYPES[file.content_type]
    object_name = f"{file_id}.{extension}"

    try:
        # Upload to MinIO
        file_bytes = await file.read()
        minio_client.put_object(
            bucket_name,
            object_name,
            file.file,
            length=len(file_bytes),
            content_type=file.content_type
        )

        # Save metadata to PostgreSQL
        db_file = FileMetadata(
            id=file_id,
            filename=file.filename,
            content_type=file.content_type,
            size=len(file_bytes),
            upload_date=datetime.utcnow()
        )
        db.add(db_file)
        db.commit()

        # Generate URL
        url = f"http://{settings.minio_endpoint}/{bucket_name}/{object_name}"

        return {"file_id": file_id, "url": url}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {e}")
    finally:
        await file.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
