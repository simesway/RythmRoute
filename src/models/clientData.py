from pydantic import BaseModel

class GraphUpdate(BaseModel):
  action: str
  id: int