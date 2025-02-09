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

@router_comanda.get("/{comanda_id}", response_model=Comanda, status_code=200)
async def get_comanda(comanda_id: str):
    return await ComandaController.get_comanda(comanda_id)

@router_comanda.put("/{comanda_id}", response_model=Comanda, status_code=200)
async def update_comanda(comanda_id: str, comanda_data: ComandaUpdate):
    return await ComandaController.update_comanda(comanda_id, comanda_data)

@router_comanda.delete("/{comanda_id}", status_code=204)
async def delete_comanda(comanda_id: str):
    try:
        success = await ComandaController.delete_comanda(comanda_id)
        if success:
            return Response(status_code=204)
        else:
            raise HTTPException(status_code=404, detail="Comanda não encontrada")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router_comanda.get("/num/",status_code=200)
async def get_num():
    return await ComandaController.num_comandas()
