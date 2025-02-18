from app.models import *
from app.controller import *
from fastapi import APIRouter, Query, HTTPException, Response
from starlette.status import HTTP_204_NO_CONTENT
from typing import *

router_comanda = APIRouter()

@router_comanda.post("/", response_model=Comanda, status_code=201)
async def create_comanda(comanda_data: ComandaCreate):
    return await ComandaController.create_comanda(comanda_data)

@router_comanda.get("/", response_model=Dict[str, Any], status_code=200)
async def list_comandas(
    page: int = Query(1, description="Número da página", ge=1),
    limit: int = Query(10, description="Número de itens por página", ge=1),
    status: Optional[str] = Query(None, description="Filtrar por status")
):
    return await ComandaController.list_comandas(page=page, limit=limit, status=status)

@router_comanda.get("/abertas", response_model=List[Comanda])
async def list_comandas_abertas():
    return await ComandaController.list_comandas_abertas()

@router_comanda.get("/{comanda_id}", response_model=Comanda, status_code=200)
async def get_comanda(comanda_id: str):
    return await ComandaController.get_comanda(comanda_id)

@router_comanda.put("/{comanda_id}", response_model=Comanda, status_code=200)
async def update_comanda(comanda_id: str, comanda_data: ComandaUpdate):
    return await ComandaController.update_comanda(comanda_id, comanda_data)

@router_comanda.get('/data/')
async def read_comandas(
    data_abertura: str = Query(..., description="Data de abertura (MM/DD/AAAA)"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamanho da página")
):
    return await ComandaController.listar_comandas_por_data(data_abertura, page, page_size)

@router_comanda.delete("/{comanda_id}", status_code=204)
async def delete_comanda(comanda_id: str):  
    return {'ok' :  await ComandaController.delete_comanda(comanda_id)}
       
@router_comanda.get("/num/",status_code=200)
async def get_num():
    return await ComandaController.num_comandas()


@router_comanda.put("/{comanda_id}/fechar", response_model=Comanda)
async def close_comanda(comanda_id: str):
    return await ComandaController.close_comanda(comanda_id)
    

@router_comanda.get("/{comanda_id}/cliente-mesa", status_code=200)
async def get_cliente_mesa(comanda_id: str):
    return await ComandaController.get_cliente_mesa_por_comanda(comanda_id)
    