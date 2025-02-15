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

