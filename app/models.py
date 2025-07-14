from sqlalchemy import Column, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class DocumentData(Base):
    """
    Represents a chunk of a document stored in the database.

    Attributes:
        chunk_id (UUID): Unique identifier for the chunk.
        document_name (str): Name of the original document.
        chunk_number (int): Sequence number of the chunk in the document.
        chunk_content (str): The actual text content of the chunk.
        role (str): The role required to access this chunk.
        keywords (str): Optional comma-separated keywords extracted from the chunk.
        summary (str): Optional summary of the chunk.
    """
    __tablename__ = "document_data"

    chunk_id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_name: str = Column(Text, nullable=False)
    chunk_number: int = Column(Integer, nullable=False)
    chunk_content: str = Column(Text, nullable=False)
    role: str = Column(Text, nullable=False)
    keywords: str = Column(Text, nullable=True)
    summary: str = Column(Text, nullable=True)

class UserRoleMap(Base):
    """
    Maps a user to a role for access control.

    Attributes:
        id (UUID): Unique ID for the mapping.
        username (str): The username (should match application login).
        role (str): The role assigned to the user.
    """
    __tablename__ = "user_role_map"

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: str = Column(Text, nullable=False)
    role: str = Column(Text, nullable=False)
