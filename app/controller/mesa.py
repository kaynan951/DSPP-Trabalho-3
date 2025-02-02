from app.models import *
from config import *
from typing import Optional, Dict, Any

class MesaController:
    @staticmethod
    async def create_mesa(mesa: MesaCreate) -> Mesa:
        pass

    @staticmethod
    async def list_mesas(page: int = 1, limit: int = 10, localizacao: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
        pass

    @staticmethod
    async def get_mesa(mesa_id: str) -> Mesa:
        pass

    @staticmethod
    async def update_mesa(mesa_id: str, mesa_data: MesaUpdate) -> Mesa:
        pass

    @staticmethod
    async def delete_mesa(mesa_id: str) -> bool:
        pass