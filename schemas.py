from pydantic import BaseModel
from datetime import datetime

class FileUploadResponse(BaseModel):
    file_id: str
    url: str

    class Config:
        orm_mode = True