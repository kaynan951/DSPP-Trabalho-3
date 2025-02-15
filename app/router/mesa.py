from app.models import *
from app.controller import *
from fastapi import APIRouter, Query, HTTPException, Response
from starlette.status import HTTP_204_NO_CONTENT
from typing import *

router_mesa = APIRouter()


@router_mesa.post("/", response_model=Mesa, status_code=201)
async def create_mesa(mesa_data: MesaCreate):
    return await MesaController.create_mesa(mesa_data)

@router_mesa.get("/", response_model=Dict[str, Any], status_code=200)
async def list_mesas(
    page: int = Query(1, description="Número da página", ge=1),
    limit: int = Query(10, description="Número de itens por página", ge=1),
    localizacao: Optional[str] = Query(None, description="Filtrar por localização"),
    status: Optional[str] = Query(None, description="Filtrar por status")
):
    return await MesaController.list_mesas(page=page, limit=limit, localizacao=localizacao, status=status)

@router_mesa.get("/{mesa_id}", response_model=Mesa, status_code=200)
async def get_mesa(mesa_id: str):
    return await MesaController.get_mesa(mesa_id)

@router_mesa.put("/{mesa_id}", response_model=Mesa, status_code=200)
async def update_mesa(mesa_id: str, mesa_data: MesaUpdate):
    return await MesaController.update_mesa(mesa_id, mesa_data)

@router_mesa.delete("/{mesa_id}", status_code=204)
async def delete_mesa(mesa_id: str):
    try:
        success = await MesaController.delete_mesa(mesa_id)
        if success:
            return Response(status_code=204)
        else:
            raise HTTPException(status_code=404, detail="Mesa não encontrada")
    except HTTPException as e:
        raise e  # Re-levanta a exceção para que o tratamento de erros do FastAPI a capture
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) # Lidar com outros erros inesperados
    
    
@router_mesa.get("/info_mesa/{id}",status_code=200,response_model=List[ComandaInfo])
async def info_das_mesas(id : str):
    return await MesaController.pegar_info_da_mesa(id) 
    
    
@router_mesa.get("/num/",status_code=200)
async def get_num():
    return await MesaController.num_mesa()
