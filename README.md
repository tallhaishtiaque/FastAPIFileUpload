# File Upload Service

REST API for uploading files to MinIO storage with metadata management in PostgreSQL.

## Features

- JWT Authentication
- File validation (DICOM, JPG, PNG, PDF)
- Metadata storage
- Dockerized environment

## Installation

1. Clone repository
2. Create `test.jpg` and `test.txt` for testing
3. Run:
```bash
docker-compose up --build