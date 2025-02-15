from app.config import *
from app.models import *
from typing import *
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
    
       
    @staticmethod
    async def pegar_info_da_mesa(id: str) -> List[ComandaInfo]:
        # valida o id da mesa
        if not ObjectId.is_valid(id):
            logger.warning(f"Id da mesa inválido: {id}")
            raise HTTPException(400, detail="Id da mesa é invalido")  

        # pega a mesa
        mesa = await db.mesas.find_one({"_id": ObjectId(id)})
        if not mesa:
            logger.warning(f"Mesa não encontrada com id: {id}")
            raise HTTPException(404, detail="Mesa não encontrada")
        mesa["_id"] = str(mesa["_id"])

        # pega os clientes que estão na mesa
        clientes_na_mesa = []
        async for cliente in db.clientes.find({"id_mesa": id}):  
            cliente["_id"] = str(cliente["_id"])
            clientes_na_mesa.append(cliente)

        comandas_info: List[ComandaInfo] = []  

        # pega os pratos dos clientes junto com o valor da comanda
        for cliente in clientes_na_mesa:
            async for comanda in db.comandas.find({"cliente_id": cliente["_id"]}):
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

        return comandas_info
    
    @staticmethod
    async def total_comandas():
        # usa a pipeline aggregate para agregar dados
        resultado = await db.comandas.aggregate([
            {
                "$group": {
                    "_id": None,  
                    "valor_total": {"$sum": "$valor_total"}, 
                    "quantidade_comandas": {"$sum": 1}  
                }
            }
        ]).to_list(1)  

        if resultado:
            return resultado[0]  
        return {"valor_total": 0, "quantidade_comandas": 0} 

    @staticmethod
    async def clientes_ordenados():
        # ordena os clientes por nome
        clientes = []
        async for cliente in db.clientes.find({}, {"_id": 0}).sort("nome", 1): 
            clientes.append(cliente)
        return clientes