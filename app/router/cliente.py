from app.models import *
from app.controller import *
from fastapi import APIRouter, Query
from typing import *

router_cliente = APIRouter() 

@router_cliente.post("/", response_model=Cliente,status_code=201)
async def create_cliente(cliente_data: ClienteCreate):
    return await ClienteController.create_cliente(cliente_data)

@router_cliente.get("/", response_model=Dict[str, Any],status_code=200)
async def list_clientes(
    page: int = Query(1, description="Número da página", ge=1),
    limit: int = Query(10, description="Número de itens por página", ge=1),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    email: Optional[str] = Query(None, description="Filtrar por email"),
    cpf: Optional[str] = Query(None, description="Filtrar por CPF"),
):
    return await ClienteController.list_clientes(page=page, limit=limit, nome=nome, email=email, cpf=cpf)

@router_cliente.get("/{cliente_id}", response_model=Cliente,status_code=200)
async def get_cliente(cliente_id: str):
    return await ClienteController.get_cliente(cliente_id)


@router_cliente.put("/{cliente_id}", response_model=Cliente,status_code=200)
async def update_cliente(cliente_id: str, cliente_data: ClienteUpdate):
    return await ClienteController.update_cliente(cliente_id, cliente_data)


@router_cliente.delete("/{cliente_id}",status_code=204)
async def delete_cliente(cliente_id: str):
    return {"ok": await ClienteController.delete_cliente(cliente_id)}

@router_cliente.get("/num/",status_code=200)
async def get_num():
    return await ClienteController.num_cliente()