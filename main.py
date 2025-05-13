import io
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from minio import Minio
from minio.error import S3Error
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from database import SessionLocal, engine, get_session_local
from models import Base, FileMetadata
from schemas import FileUploadResponse
from dependencies import get_current_user
from config import settings
import mimetypes

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
try:
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
except:
    print("MinIO not connected!")

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
    db: Session = Depends(get_session_local)
):
    # Validate file type
    mime_type, encoding = mimetypes.guess_type(file.filename)

    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported types: {list(ALLOWED_MIME_TYPES.keys())}"
        )

    file_id = str(uuid.uuid4())
    extension = ALLOWED_MIME_TYPES[mime_type]
    object_name = f"{file_id}.{extension}"

    try:
        # Upload to MinIO
        file_bytes = await file.read()
        file_bytes_stream = io.BytesIO(file_bytes)
        minio_client.put_object(
            bucket_name,
            object_name,
            file_bytes_stream,
            length=len(file_bytes),
            content_type=mime_type
        )

        # Save metadata to PostgreSQL
        db_file = FileMetadata(
            id=file_id,
            filename=file.filename,
            content_type=mime_type,
            size=len(file_bytes),
            upload_date=datetime.utcnow()
        )
        db.add(db_file)
        db.commit()

        # Generate URL
        url = f"http://{settings.minio_console_endpoint}/{bucket_name}/{object_name}"

        return {"file_id": file_id, "url": url}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {e}")
    finally:
        await file.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
