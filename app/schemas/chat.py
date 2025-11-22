from pydantic import BaseModel
from uuid import UUID
from typing import Dict, Any, Union, Literal

class ChatResponse(BaseModel):
    session_id: UUID


class SendMessageRequest(BaseModel):
    user_msg: str
    flag: int
    

class NeedMoreInfoResponse(BaseModel):
    msg: str
    flag: Literal[1]


class ComposeResult(BaseModel):
    message: str
    card: Dict[str, Any]


class RagSuccessResponse(BaseModel):
    result: ComposeResult
    flag: Literal[0]


class PlainLLMResponse(BaseModel):
    msg: str


SendMessageOutput = Union[
    NeedMoreInfoResponse,
    RagSuccessResponse,
    PlainLLMResponse
]