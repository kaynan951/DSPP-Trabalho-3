from app.models import *
from app.controller import *
from fastapi import APIRouter, Query
from typing import *

#todo

router_actions = APIRouter()

@router_actions.post("/pedir_prato/",response_model=Comanda_Prato,status_code=201)
async def pedir_prato(data : Pedir_Prato):
    return await ActionController.pedir_prato(data)


@router_actions.post("/link_ingrediente_prato/",response_model=Prato_Ingrediente,status_code=201)
async def criar_receita(data : Prato_Ingrediente):
    return await ActionController.criar_receita(data)

@router_actions.get("/info_mesa/{id}",status_code=200,response_model=List[ComandaInfo])
async def info_das_mesas(id : str):
    return await ActionController.pegar_info_da_mesa(id)

@router_actions.get("/comandas/total", response_model=dict, status_code=200)
async def total_de_comandas():
    return await ActionController.total_comandas()

@router_actions.get("/clientes/ordenados", response_model=List[dict], status_code=200)
async def clientes_em_ordem():
    return await ActionController.clientes_ordenados()