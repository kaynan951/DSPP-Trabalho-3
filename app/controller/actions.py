from app.config import *
from app.models import *
from typing import Dict
from bson import ObjectId
from fastapi import HTTPException

class ActionController:
    @staticmethod
    async def pedir_prato(pedir_prato: Pedir_Prato) -> Comanda_Prato: # Definir o tipo de retorno correto
        # validar cliente
        if not ObjectId.is_valid(pedir_prato.id_cliente):
            logger.warning(f"ID de cliente inválido: {pedir_prato.id_cliente}")
            raise HTTPException(status_code=404, detail="Id do cliente inválido")
        # validar e pegar prato
        if not ObjectId.is_valid(pedir_prato.id_prato):
            logger.warning(f"ID de prato inválido: {pedir_prato.id_prato}")
            raise HTTPException(status_code=404, detail="Id do prato inválido")

        objectId_prato = ObjectId(pedir_prato.id_prato)

        prato = await db.pratos.find_one({"_id": objectId_prato})
        if not prato:
            raise HTTPException(status_code=404, detail="Prato não encontrado")
        prato["_id"] = str(prato["_id"])  # Converter ObjectId para string
        prato_obj = Prato(**prato)

        # pegar a comanda atraves do cliente
        comanda = await db.comandas.find_one({"cliente_id": pedir_prato.id_cliente})

        if not comanda:
             raise HTTPException(status_code=404, detail="Comanda não encontrada para este cliente.")

        comanda["_id"] = str(comanda["_id"])
        comanda_obj = Comanda(**comanda)  # Cria um objeto Comanda
        objectId_comanda = ObjectId(comanda_obj.id)

        # adicionar no total da comanda o valor do prato
        comanda_obj.valor_total += prato_obj.preco

        # Converter o objeto Comanda para um dicionário antes de atualizar
        comanda_dict = comanda_obj.model_dump(by_alias=True,exclude="_id")

        # atualizar comanda
        result = await db.comandas.update_one(
            {"_id": objectId_comanda},
            {"$set": comanda_dict}  # Use um dicionário para atualizar
        )

        if result.modified_count == 0:
            logger.warning(f"Comanda não encontrada ou dados iguais: {objectId_comanda}")
            raise HTTPException(
                status_code=404, detail="Comanda não encontrada ou dados iguais."
            )

        # adicionar na tabela comanda_prato

        comada_prato_dict = Comanda_Prato(id_comada=str(objectId_comanda), id_prato=str(objectId_prato)).model_dump(
            by_alias=True,
            exclude="_id"
        )

        novo_comanda_prato = await db.comandas_pratos.insert_one(comada_prato_dict)

        response = await db.comandas_pratos.find_one({"_id": novo_comanda_prato.inserted_id})

        if not response:
            logger.error("Erro ao linkar Prato com Comanda")
            raise HTTPException(status_code=500, detail="Erro ao linkar Prato com Comanda")

        response["_id"] = str(response["_id"])
        logger.info(f"Comanda_prato criado com sucesso")

        return Comanda_Prato(**response)
    
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

        prato_ingrediente_dict = prato_ingrediente.model_dump(
            by_alias=True, exclude={"id"}
        )

        result = await db.pratos_ingredientes.insert_one(prato_ingrediente_dict)

        if not result.acknowledged:
            logger.error("Erro ao linkar prato com ingrediente")
            raise HTTPException(
                status_code=500, detail="Erro ao linkar prato com ingrediente"
            )

        # Buscar o documento recém-inserido usando o inserted_id
        response = await db.pratos_ingredientes.find_one({"_id": result.inserted_id})

        if not response:
            logger.error("Erro ao buscar prato_ingrediente recém-inserido")
            raise HTTPException(
                status_code=500,
                detail="Erro ao buscar prato_ingrediente recém-inserido",
            )

        response["_id"] = str(response["_id"])
        return Prato_Ingrediente(**response)
        