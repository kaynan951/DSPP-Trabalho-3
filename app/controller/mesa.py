from app.models import *
from app.config import *
from typing import Optional, Dict, Any, List
from fastapi import HTTPException
from bson import ObjectId
from starlette.status import HTTP_204_NO_CONTENT


class MesaController:
    @staticmethod
    async def create_mesa(mesa: MesaCreate) -> Mesa:
        mesa_dict = mesa.model_dump(by_alias=True, exclude="_id")
        nova_mesa = await db.mesas.insert_one(mesa_dict)

        response = await db.mesas.find_one({"_id": nova_mesa.inserted_id})
        if response is None:
            raise HTTPException(status_code=500, detail="Erro ao criar mesa")

        response["_id"] = str(response["_id"])
        return Mesa(**response)

    @staticmethod
    async def list_mesas(
        page: int = 1,
        limit: int = 10,
        localizacao: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        skip = (page - 1) * limit
        query = {}

        if localizacao:
            query["localizacao"] = localizacao
        if status:
            query["status"] = status

        mesas = []
        async for mesa in db.mesas.find(query).skip(skip).limit(limit):
            mesa["_id"] = str(mesa["_id"])
            mesas.append(Mesa(**mesa))

        total = await db.mesas.count_documents(query)
        totalPages = -(-total // limit)
        return {
            "mesas": mesas, 
            "pagination": {
                "total": total,    
                "currentPage": page,
                "totalPages": totalPages,
                "totalItemsPerPage": limit
            },
        }

    @staticmethod
    async def get_mesa(mesa_id: str) -> Mesa:
        try:
            mesa = await db.mesas.find_one({"_id": ObjectId(mesa_id)})
        except Exception as e:
            raise HTTPException(
                status_code=400, detail="ID da mesa inválido"
            )  # Trata ObjectId inválido

        if mesa is None:
            raise HTTPException(status_code=404, detail="Mesa não encontrada")

        mesa["_id"] = str(mesa["_id"])
        return Mesa(**mesa)

    @staticmethod
    async def update_mesa(mesa_id: str, mesa_data: MesaUpdate) -> Mesa:
        try:
            mesa = await db.mesas.find_one({"_id": ObjectId(mesa_id)})
        except Exception as e:
            raise HTTPException(
                status_code=400, detail="ID da mesa inválido"
            )  

        if mesa is None:
            raise HTTPException(status_code=404, detail="Mesa não encontrada")

        mesa_data_dict = mesa_data.model_dump(
            exclude_unset=True, by_alias=True, exclude={"id"}
        )  
        update_result = await db.mesas.update_one(
            {"_id": ObjectId(mesa_id)}, {"$set": mesa_data_dict}
        )

        if update_result.modified_count == 0:
            raise HTTPException(
                status_code=404, detail="Nenhum campo atualizado"
            )  

        updated_mesa = await db.mesas.find_one({"_id": ObjectId(mesa_id)})
        updated_mesa["_id"] = str(updated_mesa["_id"])
        return Mesa(**updated_mesa)

    @staticmethod
    async def delete_mesa(mesa_id: str) -> bool:
        try:
            if not ObjectId.is_valid(mesa_id):
                raise HTTPException(status_code=400, detail="ID da mesa é inválido")

            mesa = await db.mesas.find_one({"_id": ObjectId(mesa_id)})
            
            if mesa is None:
                raise HTTPException(status_code=404,detail="mesa não existe")
            
            delete_result = await db.mesas.delete_one({"_id": ObjectId(mesa_id)})
        except Exception as e:
            raise HTTPException(
                status_code=400, detail="ID da mesa inválido"
            )  # Trata ObjectId inválido

        if delete_result.deleted_count == 1:
            return True
        else:
            raise HTTPException(status_code=404, detail="Mesa não encontrada")
    
    async def num_mesa() -> Dict[str,int] :
        logger.debug("Contando o número total de mesas")
        try:
            total_mesas = await db.mesas.count_documents({})
            logger.info(f"Número total de mesas: {total_mesas}")
            return {"total" : total_mesas}
        except Exception as e:
            logger.exception(f"Erro ao contar mesas: {e}")
            raise HTTPException(
                status_code=500,detail="Erro interno ao contar mesas"
            )
            
    @staticmethod
    async def pegar_info_da_mesa(id: str) -> List[ComandaInfo]:
        if not ObjectId.is_valid(id):
            logger.warning(f"Id da mesa inválido: {id}")
            raise HTTPException(400, detail="Id da mesa é invalido")

        try:
            mesa = await db.mesas.find_one({"_id": ObjectId(id)})
            if not mesa:
                logger.warning(f"Mesa não encontrada com id: {id}")
                raise HTTPException(404, detail="Mesa não encontrada")
            mesa["_id"] = str(mesa["_id"])
        except Exception as e:
            logger.error(f"Erro ao obter mesa: {e}")
            raise HTTPException(status_code=500, detail="Erro ao obter mesa")

        try:
            clientes_na_mesa = []
            async for cliente in db.clientes.find({"id_mesa": id}):
                cliente["_id"] = str(cliente["_id"])
                clientes_na_mesa.append(cliente)
        except Exception as e:
            logger.error(f"Erro ao obter clientes da mesa: {e}")
            raise HTTPException(status_code=500, detail="Erro ao obter clientes da mesa")

        comandas_info: List[ComandaInfo] = []

        try:
            for cliente in clientes_na_mesa:
                comanda = await db.comandas.find_one({"cliente_id": cliente["_id"]})
                if comanda:
                    comanda["_id"] = str(comanda["_id"])
                    pratos_ids = []
                    async for comanda_prato in db.comandas_pratos.find({"id_comada": comanda["_id"]}):
                        pratos_ids.append(comanda_prato["id_prato"])

                    nomes_pratos = []
                    for prato_id in pratos_ids:
                        prato = await db.pratos.find_one({"_id": ObjectId(prato_id)})
                        if prato:
                            nomes_pratos.append(prato["nome"])

                    comanda_info = ComandaInfo(
                        cliente_nome=cliente["nome"],
                        comanda_id=comanda["_id"],
                        valor_total=comanda["valor_total"],
                        pratos=nomes_pratos,
                    )
                    comandas_info.append(comanda_info)
        except Exception as e:
            logger.error(f"Erro ao obter info da comanda: {e}")
            raise HTTPException(status_code=500, detail="Erro ao obter info da comanda")

        return comandas_info