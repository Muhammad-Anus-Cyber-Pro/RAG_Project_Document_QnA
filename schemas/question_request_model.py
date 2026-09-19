from pydantic import BaseModel, Field
from typing import Annotated

class QuestionRequestModel(BaseModel):
    session_id: Annotated[str,Field(...,description="ID of the session.")]
    question: Annotated[str, Field(..., description="Question the user.", examplr="RAG stands for?")]

class QuestionResponseModel(BaseModel):
    answer: Annotated[str, Field(..., description="Answer of the question.")]