from pydantic import BaseModel

class InputSchema(BaseModel):
    prompt: str
