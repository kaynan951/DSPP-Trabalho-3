from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime
from app.models import *

class Cliente(BaseModel):
    id: str = Field(None, alias="_id")
    nome: str = Field(min_length=2)
    telefone: str = Field(min_length=10)
    email: Optional[str] = Field(None)
    cpf: Optional[str] = Field(min_length=11,max_length=11)
    comanda : Optional[Comanda] = Field(None)
    id_mesa : str = Field(None)


class ClienteCreate(Cliente):
    pass

class ClienteUpdate(Cliente):
    nome: Optional[str] 
    telefone: Optional[str] 
    email: Optional[str] 
  