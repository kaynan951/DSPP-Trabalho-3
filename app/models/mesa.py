from typing import Optional,List
from pydantic import BaseModel,Field
from app.models import *
class Mesa(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    numero: int = Field(ge=1)
    capacidade: int = Field(ge=1)
    localizacao: str = Field(min_length=3)
    status: str = Field(default='disponivel')


class MesaCreate(Mesa):
    pass

class MesaUpdate(Mesa):
    numero: Optional[int]  
    capacidade: Optional[int]  
    localizacao: Optional[str]  
    status: Optional[str]
    