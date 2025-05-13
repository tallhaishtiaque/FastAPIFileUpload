from fastapi.testclient import TestClient
from main import app
from jose import jwt

client = TestClient(app)

def test_upload_file():
    # Generate valid JWT token
    token = jwt.encode({"sub": "user"}, "secret-key", algorithm="HS256")

    # Test valid file upload
    with open("test.png", "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("test.jpg", f, "image/jpeg")},
            headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert "url" in data

    # Test invalid file type
    with open("test.txt", "w") as f:
        f.write("invalid content")
    with open("test.txt", "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("test.txt", f, "text/plain")},
            headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 400