from pydantic import BaseModel,Field
from typing import Optional
from app.models import *

class Comanda_Prato(BaseModel):
    id : str = Field(None,alias="_id")
    id_comada : str
    id_prato : str