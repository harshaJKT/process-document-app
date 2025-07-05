from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


class DocumentData(Base):
    __tablename__ = "document_data"

    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_name = Column(Text, nullable=False)
    chunk_number = Column(Integer, nullable=False)
    chunk_content = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    keywords = Column(Text)
    summary = Column(Text)

class UserRoleMap(Base):
    __tablename__ = "user_role_map"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
