from pydantic import BaseModel,Field


class Pedir_Prato(BaseModel):
    id_cliente : str = Field("")
    id_prato : str = Field("")
    