from app.models import *
from config import *
from typing import Optional, Dict, Any, List
class IngredienteController:
    @staticmethod
    async def create_ingrediente(ingrediente: IngredienteCreate) -> Ingrediente:
        pass

    @staticmethod
    async def list_ingredientes(page: int = 1, limit: int = 10, nome: Optional[str] = None) -> Dict[str, Any]:
        pass

    @staticmethod
    async def get_ingrediente(ingrediente_id: str) -> Ingrediente:
        pass

    @staticmethod
    async def update_ingrediente(ingrediente_id: str, ingrediente_data: IngredienteUpdate) -> Ingrediente:
        pass

    @staticmethod
    async def delete_ingrediente(ingrediente_id: str) -> bool:
        pass
