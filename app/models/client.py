from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime

class Cliente(BaseModel):
    id: str = Field(None, alias="_id")
    nome: str = Field(min_length=2)
    telefone: str = Field(min_length=10)
    email: Optional[str] = Field(None)
    data_cadastro: datetime = Field(default_factory=datetime.now)
    comanda_id: Optional[str] = Field(None) 

class ClienteCreate(Cliente):
    pass

class ClienteUpdate(Cliente):
    nome: Optional[str] 
    telefone: Optional[str] 
    email: Optional[str] 
    comanda_id: Optional[str] 