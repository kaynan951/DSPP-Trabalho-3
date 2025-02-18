from app.models import *
from app.controller import *
from fastapi import APIRouter, Query, HTTPException, Response
from typing import *

router_prato = APIRouter()

@router_prato.post("/", response_model=Prato, status_code=201)
async def create_prato(prato_data: PratoCreate):
    return await PratoController.create_prato(prato_data)

@router_prato.get("/", response_model=Dict[str, Any], status_code=200)
async def list_pratos(
    page: int = Query(1, description="Número da página", ge=1),
    limit: int = Query(10, description="Número de itens por página", ge=1),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    nome : Optional[str] = Query(None,description="Filtrar por nome do prato")
):
    return await PratoController.list_pratos(page=page, limit=limit, categoria=categoria)

@router_prato.get("/{prato_id}", response_model=Prato, status_code=200)
async def get_prato(prato_id: str):
    return await PratoController.get_prato(prato_id)

@router_prato.put("/{prato_id}", response_model=Prato, status_code=200)
async def update_prato(prato_id: str, prato_data: PratoUpdate):
    return await PratoController.update_prato(prato_id, prato_data)

@router_prato.delete("/{prato_id}", status_code=204)
async def delete_prato(prato_id: str):
   return {'ok' :  await PratoController.delete_prato(prato_id)}
    
@router_prato.get("/mais_pedidos/",status_code=200)
async def get_pratos_mais_pedidos(
    page: int = Query(1, description="Número da página", ge=1),
    limit: int = Query(10, description="Número de itens por página", ge=1),
):
    return await PratoController.get_pratos_mais_pedidos(page,limit)
    
@router_prato.get("/num/",status_code=200)
async def get_num():
    return await PratoController.num_pratos()