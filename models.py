from sqlalchemy import Column, String, DateTime, Integer
from database import Base

class FileMetadata(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    content_type = Column(String)
    size = Column(Integer)
    upload_date = Column(DateTime)