from typing import Optional,List
from pydantic import BaseModel,Field
from datetime import datetime
from app.models import *

class Comanda(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    cliente_id : Optional[str] = Field("")
    data_abertura: datetime = Field(default_factory=datetime.now)
    data_fechamento: Optional[datetime] = Field(None)
    status: str = Field(default='aberta')
    valor_total: float = Field(default=0.0, ge=0)
    
    
    
class ComandaCreate(Comanda):
    pass

class ComandaUpdate(Comanda):
    data_fechamento: Optional[datetime] 
    status: Optional[str]
    valor_total: Optional[float]
    pratos_ids: Optional[List[str]]