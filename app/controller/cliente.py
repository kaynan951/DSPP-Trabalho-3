from app.models import *
from app.config import *
from typing import Optional,Dict,Any

class ClienteController:
    @staticmethod
    async def create_cliente(cliente : ClienteCreate) ->Cliente :
        pass

    @staticmethod
    async def list_clientes(
        page: int = 1,
        limit: int = 10,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        cpf: Optional[str] = None,
    ) -> Dict[str, Any]:
        pass
    
    @staticmethod
    async def get_cliente(cliente_id: str) -> Cliente:
        pass
        
    @staticmethod
    async def update_cliente(cliente_id: str, cliente_data: ClienteUpdate) -> Cliente:
       pass

    @staticmethod
    async def delete_cliente(cliente_id: str) -> bool:
        pass

    @staticmethod
    async def num_cliente() -> Dict[str, int]:
       pass
        
    
       

