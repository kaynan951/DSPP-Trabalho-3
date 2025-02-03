from pydantic import BaseModel,Field
from app.models import *

class Prato_Ingrediente(BaseModel):
    id : str = Field(None,alias="_id")
    id_prato : str 
    id_ingrediente: str
    
    
    