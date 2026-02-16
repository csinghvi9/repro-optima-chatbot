from pydantic import BaseModel
from typing import Union, List


class MessageCreate(BaseModel):
    content: Union[str, List[str]]
    sender: str
