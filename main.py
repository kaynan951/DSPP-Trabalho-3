from fastapi import FastAPI
from app.router import *

from app.config.logging_config import setup_logging

app = FastAPI()

logger = setup_logging()

app.include_router(router_cliente, prefix="/cliente",tags=["cliente"])
app.include_router(router_mesa, prefix="/mesa",tags=["mesa"])
app.include_router(router_comanda, prefix="/comanda",tags=["comanda"])
app.include_router(router_ingrediente, prefix="/ingrediente",tags=["ingrediente"])
app.include_router(router_prato, prefix="/prato",tags=["prato"])


@app.get("/")
def read_root():
    logger.info("API inicializada")
    return {"message": "API de Gerenciamento de Restaurante"}
