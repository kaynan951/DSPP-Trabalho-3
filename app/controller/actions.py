from app.config import *  
from app.models import *
from typing import *
from bson import ObjectId
from fastapi import HTTPException

class ActionController:
    @staticmethod
    async def pedir_prato(pedir_prato: Pedir_Prato) -> Comanda_Prato:
        if not ObjectId.is_valid(pedir_prato.id_cliente):
            logger.warning(f"ID de cliente inválido: {pedir_prato.id_cliente}")
            raise HTTPException(status_code=404, detail="Id do cliente inválido")

        if not ObjectId.is_valid(pedir_prato.id_prato):
            logger.warning(f"ID de prato inválido: {pedir_prato.id_prato}")
            raise HTTPException(status_code=404, detail="Id do prato inválido")

        try:
            objectId_prato = ObjectId(pedir_prato.id_prato)
            prato = await db.pratos.find_one({"_id": objectId_prato})
            if not prato:
                raise HTTPException(status_code=404, detail="Prato não encontrado")
            prato["_id"] = str(prato["_id"])
            prato_obj = Prato(**prato)
        except Exception as e:
            logger.error(f"Erro ao obter prato: {e}")
            raise HTTPException(status_code=500, detail="Erro ao obter prato")

        try:
            comanda = await db.comandas.find_one({"cliente_id": pedir_prato.id_cliente})
            if not comanda:
                 raise HTTPException(status_code=404, detail="Comanda não encontrada para este cliente.")
            comanda["_id"] = str(comanda["_id"])
            comanda_obj = Comanda(**comanda)
            objectId_comanda = ObjectId(comanda_obj.id)
        except Exception as e:
            logger.error(f"Erro ao obter comanda: {e}")
            raise HTTPException(status_code=500, detail="Erro ao obter comanda")

        try:
            comanda_obj.valor_total += prato_obj.preco
            comanda_dict = comanda_obj.model_dump(by_alias=True,exclude={"id"})
            result = await db.comandas.update_one(
                {"_id": objectId_comanda},
                {"$set": comanda_dict}
            )

            if result.modified_count == 0:
                logger.warning(f"Comanda não encontrada ou dados iguais: {objectId_comanda}")
                raise HTTPException(
                    status_code=404, detail="Comanda não encontrada ou dados iguais."
                )
        except Exception as e:
            logger.error(f"Erro ao atualizar comanda: {e}")
            raise HTTPException(status_code=500, detail="Erro ao atualizar comanda")

        try:
            comada_prato_dict = Comanda_Prato(id_comada=str(objectId_comanda), id_prato=str(objectId_prato)).model_dump(
                by_alias=True,
                exclude={"id"}
            )
            novo_comanda_prato = await db.comandas_pratos.insert_one(comada_prato_dict)
            response = await db.comandas_pratos.find_one({"_id": novo_comanda_prato.inserted_id})

            if not response:
                logger.error("Erro ao linkar Prato com Comanda")
                raise HTTPException(status_code=500, detail="Erro ao linkar Prato com Comanda")

            response["_id"] = str(response["_id"])
            logger.info(f"Comanda_prato criado com sucesso")
            return Comanda_Prato(**response)

        except Exception as e:
            logger.error(f"Erro ao criar comanda_prato: {e}")
            raise HTTPException(status_code=500, detail="Erro ao criar comanda_prato")

    @staticmethod
    async def criar_receita(prato_ingrediente: Prato_Ingrediente) -> Prato_Ingrediente:
        if not ObjectId.is_valid(prato_ingrediente.id_prato):
            logger.warning(f"id de prato invalido: {prato_ingrediente.id_prato}")
            raise HTTPException(status_code=404, detail="Id do prato inválido")

        if not ObjectId.is_valid(prato_ingrediente.id_ingrediente):
            logger.warning(
                f"id de ingrediente invalido: {prato_ingrediente.id_ingrediente}"
            )
            raise HTTPException(status_code=404, detail="Id do ingrediente inválido")

        try:
            prato_ingrediente_dict = prato_ingrediente.model_dump(
                by_alias=True, exclude={"id"}
            )

            result = await db.pratos_ingredientes.insert_one(prato_ingrediente_dict)

            if not result.acknowledged:
                logger.error("Erro ao linkar prato com ingrediente")
                raise HTTPException(
                    status_code=500, detail="Erro ao linkar prato com ingrediente"
                )

            response = await db.pratos_ingredientes.find_one({"_id": result.inserted_id})

            if not response:
                logger.error("Erro ao buscar prato_ingrediente recém-inserido")
                raise HTTPException(
                    status_code=500,
                    detail="Erro ao buscar prato_ingrediente recém-inserido",
                )

            response["_id"] = str(response["_id"])
            return Prato_Ingrediente(**response)
        except Exception as e:
            logger.error(f"Erro ao criar receita: {e}")
            raise HTTPException(status_code=500, detail="Erro ao criar receita")

    