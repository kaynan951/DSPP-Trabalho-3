from pydantic import BaseModel,Field
from typing import Optional
from app.models import *

class Cliente(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    nome: str = Field(min_length=2)
    telefone: str = Field(min_length=10)
    email: Optional[str] = Field(default=None)
    cpf: Optional[str] = Field(min_length=11,max_length=11)
    id_mesa : str = Field(default=None)


class ClienteCreate(Cliente):
    pass

class ClienteUpdate(Cliente):
    nome: Optional[str] 
    telefone: Optional[str] 
    email: Optional[str] 
  