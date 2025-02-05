from app.models import *
from app.config import *
from typing import Optional, Dict, Any, List

class PratoController:
    @staticmethod
    async def create_prato(prato: PratoCreate) -> Prato:
        pass

    @staticmethod
    async def list_pratos(page: int = 1, limit: int = 10, categoria: Optional[str] = None) -> Dict[str, Any]:
        pass

    @staticmethod
    async def get_prato(prato_id: str) -> Prato:
        pass

    @staticmethod
    async def update_prato(prato_id: str, prato_data: PratoUpdate) -> Prato:
        pass

    @staticmethod
    async def delete_prato(prato_id: str) -> bool:
        pass
