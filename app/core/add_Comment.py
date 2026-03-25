from pydantic import BaseModel
from .security import decode_response


class CommentRequest(BaseModel):
    post_id:str
    user_id:str
    comment: str
