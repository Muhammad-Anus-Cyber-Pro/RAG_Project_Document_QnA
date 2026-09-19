from pydantic import BaseModel, Field
from typing import Annotated

class UploadResponse(BaseModel):
    session_id: Annotated[str, Field(..., description="session id of the vector store.")]