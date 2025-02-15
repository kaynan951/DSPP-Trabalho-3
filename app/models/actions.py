from pydantic import BaseModel,Field
from typing import *

class Pedir_Prato(BaseModel):
    id_cliente : str = Field("")
    id_prato : str = Field("")

class ComandaInfo(BaseModel):
    cliente_nome: str
    comanda_id: str
    valor_total: float
    pratos: List[str]
    
class ClienteComComanda(BaseModel): 
    id: Optional[str] = Field(alias="_id")
    nome: str
    telefone: str
    email: Optional[str] = None
    cpf: Optional[str] = None
    id_mesa: str
    comanda: Optional[Dict[str, Any]]  