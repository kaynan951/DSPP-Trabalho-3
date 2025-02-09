from typing import Optional,List
from pydantic import BaseModel,Field

class Prato(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str = Field(min_length=2)
    descricao: str = Field(min_length=5)
    preco: float = Field(ge=0)
    categoria: str = Field(min_length=2)
    
    
class PratoCreate(Prato):
    pass

class PratoUpdate(Prato):
    nome: Optional[str]
    descricao: Optional[str]
    preco: Optional[float] 
    categoria: Optional[str] 
