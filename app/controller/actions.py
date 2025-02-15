# from app.config import *
# from app.models import *
# from typing import *
# from bson import ObjectId
# from fastapi import HTTPException


# class ActionController:
#     @staticmethod
#     async def pedir_prato(pedir_prato: Pedir_Prato) -> Comanda_Prato: # Definir o tipo de retorno correto
#         # validar cliente
#         if not ObjectId.is_valid(pedir_prato.id_cliente):
#             logger.warning(f"ID de cliente inválido: {pedir_prato.id_cliente}")
#             raise HTTPException(status_code=404, detail="Id do cliente inválido")
#         # validar e pegar prato
#         if not ObjectId.is_valid(pedir_prato.id_prato):
#             logger.warning(f"ID de prato inválido: {pedir_prato.id_prato}")
#             raise HTTPException(status_code=404, detail="Id do prato inválido")

#         objectId_prato = ObjectId(pedir_prato.id_prato)

#         prato = await db.pratos.find_one({"_id": objectId_prato})
#         if not prato:
#             raise HTTPException(status_code=404, detail="Prato não encontrado")
#         prato["_id"] = str(prato["_id"])  # Converter ObjectId para string
#         prato_obj = Prato(**prato)

#         # pegar a comanda atraves do cliente
#         comanda = await db.comandas.find_one({"cliente_id": pedir_prato.id_cliente})

#         if not comanda:
#              raise HTTPException(status_code=404, detail="Comanda não encontrada para este cliente.")

#         comanda["_id"] = str(comanda["_id"])
#         comanda_obj = Comanda(**comanda)  
#         objectId_comanda = ObjectId(comanda_obj.id)

#         comanda_obj.valor_total += prato_obj.preco

#         comanda_dict = comanda_obj.model_dump(by_alias=True,exclude="_id")

#         # atualizar comanda
#         result = await db.comandas.update_one(
#             {"_id": objectId_comanda},
#             {"$set": comanda_dict} 
#         )

#         if result.modified_count == 0:
#             logger.warning(f"Comanda não encontrada ou dados iguais: {objectId_comanda}")
#             raise HTTPException(
#                 status_code=404, detail="Comanda não encontrada ou dados iguais."
#             )

#         # adicionar na tabela comanda_prato

#         comada_prato_dict = Comanda_Prato(id_comada=str(objectId_comanda), id_prato=str(objectId_prato)).model_dump(
#             by_alias=True,
#             exclude="_id"
#         )

#         novo_comanda_prato = await db.comandas_pratos.insert_one(comada_prato_dict)

#         response = await db.comandas_pratos.find_one({"_id": novo_comanda_prato.inserted_id})

#         if not response:
#             logger.error("Erro ao linkar Prato com Comanda")
#             raise HTTPException(status_code=500, detail="Erro ao linkar Prato com Comanda")

#         response["_id"] = str(response["_id"])
#         logger.info(f"Comanda_prato criado com sucesso")

#         return Comanda_Prato(**response)
    
#     @staticmethod
#     async def criar_receita(prato_ingrediente: Prato_Ingrediente) -> Prato_Ingrediente:
#         if not ObjectId.is_valid(prato_ingrediente.id_prato):
#             logger.warning(f"id de prato invalido: {prato_ingrediente.id_prato}")
#             raise HTTPException(status_code=404, detail="Id do prato inválido")

#         if not ObjectId.is_valid(prato_ingrediente.id_ingrediente):
#             logger.warning(
#                 f"id de ingrediente invalido: {prato_ingrediente.id_ingrediente}"
#             )
#             raise HTTPException(status_code=404, detail="Id do ingrediente inválido")

#         prato_ingrediente_dict = prato_ingrediente.model_dump(
#             by_alias=True, exclude={"id"}
#         )

#         result = await db.pratos_ingredientes.insert_one(prato_ingrediente_dict)

#         if not result.acknowledged:
#             logger.error("Erro ao linkar prato com ingrediente")
#             raise HTTPException(
#                 status_code=500, detail="Erro ao linkar prato com ingrediente"
#             )

#         response = await db.pratos_ingredientes.find_one({"_id": result.inserted_id})

#         if not response:
#             logger.error("Erro ao buscar prato_ingrediente recém-inserido")
#             raise HTTPException(
#                 status_code=500,
#                 detail="Erro ao buscar prato_ingrediente recém-inserido",
#             )

#         response["_id"] = str(response["_id"])
#         return Prato_Ingrediente(**response)
    
       
#     @staticmethod
#     async def pegar_info_da_mesa(id: str) -> List[ComandaInfo]: # consulta complexa
#         # valida o id da mesa
#         if not ObjectId.is_valid(id):
#             logger.warning(f"Id da mesa inválido: {id}")
#             raise HTTPException(400, detail="Id da mesa é invalido")  

#         # pega a mesa
#         mesa = await db.mesas.find_one({"_id": ObjectId(id)})
#         if not mesa:
#             logger.warning(f"Mesa não encontrada com id: {id}")
#             raise HTTPException(404, detail="Mesa não encontrada")
#         mesa["_id"] = str(mesa["_id"])

#         # pega os clientes que estão na mesa
#         clientes_na_mesa = []
#         async for cliente in db.clientes.find({"id_mesa": id}):  
#             cliente["_id"] = str(cliente["_id"])
#             clientes_na_mesa.append(cliente)

#         comandas_info: List[ComandaInfo] = []  

#         # pega os pratos dos clientes junto com o valor da comanda
#         for cliente in clientes_na_mesa:
#             async for comanda in db.comandas.find({"cliente_id": cliente["_id"]}):
#                 comanda["_id"] = str(comanda["_id"])
#                 pratos_ids = []
#                 async for comanda_prato in db.comandas_pratos.find({"id_comada": comanda["_id"]}):
#                     pratos_ids.append(comanda_prato["id_prato"])

#                 nomes_pratos = []
#                 for prato_id in pratos_ids:
#                     prato = await db.pratos.find_one({"_id": ObjectId(prato_id)})
#                     if prato:
#                         nomes_pratos.append(prato["nome"])

#                 comanda_info = ComandaInfo(
#                     cliente_nome=cliente["nome"],
#                     comanda_id=comanda["_id"],
#                     valor_total=comanda["valor_total"],
#                     pratos=nomes_pratos,
#                 )
#                 comandas_info.append(comanda_info)

#         return comandas_info
    
#     @staticmethod
#     async def clientes_ordenados(): # ordenação
#         # ordena os clientes por nome
#         clientes = []
#         async for cliente in db.clientes.find({}, {"_id": 0}).sort("nome", 1): 
#             clientes.append(cliente)
#         return clientes
    
    
#     @staticmethod
#     async def listar_clientes_com_comanda(
#         pagina: int = 1, limite: int = 10,
#     ) -> List[ClienteComComanda]: 
#         if pagina < 1 or limite < 1:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Página e limite devem ser maiores que zero.",
#             )

#         skip = (pagina - 1) * limite

#         try:
#             # Fetch clientes with pagination
#             clientes_cursor = db.clientes.find().skip(skip).limit(limite)
#             clientes = await clientes_cursor.to_list(length=limite)

#             cliente_list = []
#             for cliente in clientes:
#                 cliente["_id"] = str(cliente["_id"])

#                 # Fetch the associated comanda (if it exists)
#                 comanda = await db.comandas.find_one({"cliente_id": cliente["_id"]}) # Find, not aggregate

#                 if comanda:
#                     comanda["_id"] = str(comanda["_id"])
                
#                 cliente_com_comanda = ClienteComComanda(**cliente, comanda=comanda) # Construct model
#                 cliente_list.append(cliente_com_comanda)


#             return cliente_list

#         except Exception as e:
#             logger.error(f"Erro ao listar clientes com comanda: {e}")
#             raise HTTPException(
#                 status_code=500, detail="Erro ao listar clientes com comanda"
#             )
        
        
        
from app.config import *  # Import logger and db
from app.models import *
from typing import *
from bson import ObjectId
from fastapi import HTTPException
import logging

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

    

    @staticmethod
    async def listar_clientes_com_comanda(
        pagina: int = 1, limite: int = 10,
    ) -> List[ClienteComComanda]:
        if pagina < 1 or limite < 1:
            logger.warning("Página ou limite inválidos.")
            raise HTTPException(
                status_code=400,
                detail="Página e limite devem ser maiores que zero.",
            )

        skip = (pagina - 1) * limite

        try:
            clientes_cursor = db.clientes.find().skip(skip).limit(limite)
            clientes = await clientes_cursor.to_list(length=limite)

            cliente_list = []
            for cliente in clientes:
                cliente["_id"] = str(cliente["_id"])

                comanda = await db.comandas.find_one({"cliente_id": cliente["_id"]})
                if comanda:
                    comanda["_id"] = str(comanda["_id"])

                cliente_com_comanda = ClienteComComanda(**cliente, comanda=comanda)
                cliente_list.append(cliente_com_comanda)

            logger.info("Clientes com comandas listados com sucesso.")
            return cliente_list

        except Exception as e:
            logger.error(f"Erro ao listar clientes com comanda: {e}")
            raise HTTPException(
                status_code=500, detail="Erro ao listar clientes com comanda"
            )