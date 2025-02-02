from app.models import *
from app.controller import *
from fastapi import APIRouter, Query
from typing import *

router_ingrediente = APIRouter()

@router_ingrediente.post("/", response_model=Ingrediente, status_code=201)
async def create_ingrediente(ingrediente_data: IngredienteCreate):
    return await IngredienteController.create_ingrediente(ingrediente_data)

@router_ingrediente.get("/", response_model=Dict[str, Any], status_code=200)
async def list_ingredientes(
    page: int = Query(1, description="Número da página", ge=1),
    limit: int = Query(10, description="Número de itens por página", ge=1),
    nome: Optional[str] = Query(None, description="Filtrar por nome")
):
    return await IngredienteController.list_ingredientes(page=page, limit=limit, nome=nome)

@router_ingrediente.get("/{ingrediente_id}", response_model=Ingrediente, status_code=200)
async def get_ingrediente(ingrediente_id: str):
    return await IngredienteController.get_ingrediente(ingrediente_id)

@router_ingrediente.put("/{ingrediente_id}", response_model=Ingrediente, status_code=200)
async def update_ingrediente(ingrediente_id: str, ingrediente_data: IngredienteUpdate):
    return await IngredienteController.update_ingrediente(ingrediente_id, ingrediente_data)

@router_ingrediente.delete("/{ingrediente_id}", status_code=204)
def delete_ingrediente(ingrediente_id: str):
    return {"ok": IngredienteController.delete_ingrediente(ingrediente_id)}
