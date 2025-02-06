from app.models import *
from app.config import *
from typing import Optional,Dict,Any
from fastapi import HTTPException
from bson import ObjectId

class ClienteController:
    @staticmethod
    async def create_cliente(cliente: ClienteCreate) -> Cliente:
        logger.debug(f"Iniciando create_cliente para o cliente: {cliente.nome}")

        try:
            if not ObjectId.is_valid(cliente.id_mesa):
                logger.warning(f"ID de mesa inválido: {cliente.id_mesa}")
                raise HTTPException(
                    status_code=400, detail="id_mesa inválido. Deve ser um ObjectId válido."
                )

            mesa_id = ObjectId(cliente.id_mesa)

            # Buscar a mesa
            mesa = await db.mesas.find_one({"_id": mesa_id})
            if not mesa:
                logger.warning(f"Mesa não encontrada com ID: {cliente.id_mesa}")
                raise HTTPException(
                    status_code=404, detail="Mesa não encontrada."
                )

            capacidade_total = mesa["capacidade"]

            clientes_na_mesa = await db.clientes.count_documents({"id_mesa": str(mesa["_id"])})
            logger.debug(f"Clientes na mesa {mesa['_id']}: {clientes_na_mesa}, Capacidade: {capacidade_total}")

            if clientes_na_mesa >= capacidade_total:
                logger.warning(
                    f"Mesa {mesa['_id']} está cheia. Capacidade: {capacidade_total}, Clientes: {clientes_na_mesa}"
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Mesa {mesa['numero']} está cheia. Não é possível adicionar mais clientes.",
                )


            cliente_dict = cliente.model_dump(by_alias=True, exclude="_id")
            novo_cliente = await db.clientes.insert_one(cliente_dict)

            response = await db.clientes.find_one({"_id": novo_cliente.inserted_id})

            if not response:
                logger.error("Erro ao criar cliente no banco de dados.")
                raise HTTPException(
                    status_code=500, detail="Erro ao criar cliente no banco de dados."
                )

            response["_id"] = str(response["_id"])
            logger.info(f"Cliente {response['_id']} criado com sucesso na mesa {mesa['_id']}")
            return Cliente(**response)

        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.exception(f"Erro inesperado ao criar cliente: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao criar cliente."
            )
            

    @staticmethod
    async def list_clientes(
        page: int = 1,
        limit: int = 10,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        cpf: Optional[str] = None,
    ) -> Dict[str, Any]:
        pass
    
    @staticmethod
    async def get_cliente(cliente_id: str) -> Cliente:
        pass
        
    @staticmethod
    async def update_cliente(cliente_id: str, cliente_data: ClienteUpdate) -> Cliente:
       pass

    @staticmethod
    async def delete_cliente(cliente_id: str) -> bool:
        pass

    @staticmethod
    async def num_cliente() -> Dict[str, int]:
       pass
        
    
       

