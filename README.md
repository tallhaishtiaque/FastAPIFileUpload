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
```

## API Documentation (Swagger)


http://localhost:8000/docs


## Testing 


1. Get a JWT token (example):
```bash
python -c 'from jose import jwt; print(jwt.encode({"sub": "user"}, "secret-key", algorithm="HS256"))'
```

2. Upload a file
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" -F "file=@test.jpg" http://localhost:8000/upload
```

3. For automated test create test files

```bash
# Create a valid test image
dd if=/dev/urandom of=test.jpg bs=1 count=1024

# Create an invalid test file
echo "invalid content" > test.txt
```
4. Run the test
```bash
docker-compose exec app pytest test_main.py -v
```