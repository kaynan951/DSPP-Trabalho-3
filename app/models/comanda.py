from typing import Optional,List
from pydantic import BaseModel,Field
from datetime import datetime


class Comanda(BaseModel):
    id: str = Field(None, alias="_id")
    data_abertura: datetime = Field(default_factory=datetime.now)
    data_fechamento: Optional[datetime] = Field(None)
    status: str = Field(default='aberta')
    valor_total: float = Field(default=0.0, ge=0)
    pratos_ids: List[str] = Field(default=[])
    
class ComandaCreate(Comanda):
    pass

class ComandaUpdate(Comanda):
    data_fechamento: Optional[datetime] 
    status: Optional[str]
    valor_total: Optional[float]
    pratos_ids: Optional[List[str]]