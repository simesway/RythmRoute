from pydantic import BaseModel
from typing import Optional

class GraphUpdate(BaseModel):
  action: str
  id: Optional[int] = None
  name: Optional[str] = None