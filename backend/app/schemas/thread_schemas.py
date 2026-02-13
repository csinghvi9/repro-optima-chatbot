from pydantic import BaseModel


class ThreadEditRequest(BaseModel):
    name: str
    thread_id: str
