from pydantic import BaseModel,Field
from typing import Optional
from app.models import *

class Prato_Ingrediente(BaseModel):
    id : Optional[str] = Field(None,alias="_id")
    id_prato : str 
    id_ingrediente: str
    
    
    