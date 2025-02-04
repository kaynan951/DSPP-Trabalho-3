from typing import Optional
from pydantic import BaseModel,Field
from datetime import datetime

class Ingrediente(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    nome: str = Field(min_length=2)
    unidade_medida: str = Field(min_length=1)
    preco_unitario: float = Field(ge=0)
    data_validade: Optional[datetime] = Field(None)
    
    
class IngredienteCreate(Ingrediente):
    pass

class IngredienteUpdate(Ingrediente):
    nome: Optional[str]
    unidade_medida: Optional[str] 
    preco_unitario: Optional[float] 
    data_validade: Optional[datetime] 