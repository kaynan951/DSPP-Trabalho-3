from .cliente import Cliente, ClienteCreate, ClienteUpdate
from .mesa import Mesa, MesaCreate, MesaUpdate
from .comanda import Comanda, ComandaCreate, ComandaUpdate
from .prato import Prato, PratoCreate, PratoUpdate
from .ingrediente import Ingrediente, IngredienteCreate, IngredienteUpdate

__all__ = [
    "Cliente", "ClienteCreate", "ClienteUpdate",
    "Mesa", "MesaCreate", "MesaUpdate",
    "Comanda", "ComandaCreate", "ComandaUpdate",
    "Prato", "PratoCreate", "PratoUpdate",
    "Ingrediente", "IngredienteCreate", "IngredienteUpdate"
]


Cliente.model_rebuild()
ClienteCreate.model_rebuild()
ClienteUpdate.model_rebuild()
Mesa.model_rebuild()
MesaCreate.model_rebuild()
MesaUpdate.model_rebuild()
Comanda.model_rebuild()
ComandaCreate.model_rebuild()
ComandaUpdate.model_rebuild()
Prato.model_rebuild()
PratoCreate.model_rebuild()
PratoUpdate.model_rebuild()
Ingrediente.model_rebuild()
IngredienteCreate.model_rebuild()
IngredienteUpdate.model_rebuild()
