from typing import Optional,List
from pydantic import BaseModel,Field

class Mesa(BaseModel):
    id: str = Field(None, alias="_id")
    numero: int = Field(ge=1)
    capacidade: int = Field(ge=1)
    localizacao: str = Field(min_length=3)
    status: str = Field(default='disponivel')
    comandas_ids: List[str] = Field([])

class MesaCreate(Mesa):
    pass

class MesaUpdate(Mesa):
    id: Optional[str]  
    numero: Optional[int]  
    capacidade: Optional[int]  
    localizacao: Optional[str]  
    status: Optional[str]  
    comandas_ids:Optional[ List[str] ] 