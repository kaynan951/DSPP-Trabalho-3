from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from bson import ObjectId
from app.models import *  # Certifique-se de que Comanda existe em models.py
from app.config import *  # Importe a configuração do banco de dados (db)
from .cliente import ClienteController # Importa o cliente controller

class ComandaController:
    @staticmethod
    async def create_comanda(comanda: ComandaCreate) -> Comanda:
        """Cria uma nova comanda."""
        logger.debug(f"Criando comanda para cliente_id: {comanda.cliente_id}")
        try:
            # Validar se o cliente_id é um ObjectId válido
            if comanda.cliente_id:
                try:
                    ObjectId(comanda.cliente_id)
                except Exception:
                    logger.warning(f"cliente_id inválido: {comanda.cliente_id}")
                    raise HTTPException(
                        status_code=400, detail="cliente_id inválido."
                    )
            
            #Validar se o cliente existe:
            try:
                await ClienteController.get_cliente(comanda.cliente_id)
            except HTTPException as e:
                 raise HTTPException(
                        status_code=404, detail="Cliente não encontrado."
                    )
                
            # Verificar se já existe uma comanda aberta para este cliente
            existing_comanda = await db.comandas.find_one({
                "cliente_id": comanda.cliente_id,
                "status": "aberta"
            })

            if existing_comanda:
                logger.warning(
                    f"Já existe uma comanda aberta para o cliente {comanda.cliente_id}."
                )
                raise HTTPException(
                    status_code=400,
                    detail="Já existe uma comanda aberta para este cliente. Feche a comanda existente antes de criar uma nova.",
                )

            comanda_dict = comanda.model_dump(by_alias=True, exclude={"id"})
            novo_comanda = await db.comandas.insert_one(comanda_dict)
            response = await db.comandas.find_one({"_id": novo_comanda.inserted_id})

            if not response:
                logger.error("Erro ao criar comanda no banco de dados.")
                raise HTTPException(
                    status_code=500, detail="Erro ao criar comanda no banco de dados."
                )

            response["_id"] = str(response["_id"])
            logger.info(f"Comanda {response['_id']} criada com sucesso.")
            return Comanda(**response)

        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.exception(f"Erro ao criar comanda: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao criar comanda."
            )
        
    @staticmethod
    async def get_comanda(comanda_id: str) -> Comanda:
        """Busca uma comanda pelo ID."""
        logger.debug(f"Buscando comanda com ID: {comanda_id}")
        try:
            try:
                object_id = ObjectId(comanda_id)
            except Exception:
                logger.warning(f"ID de comanda inválido: {comanda_id}")
                raise HTTPException(status_code=400, detail="ID de comanda inválido.")

            comanda = await db.comandas.find_one({"_id": object_id})
            if not comanda:
                logger.warning(f"Comanda não encontrada com ID: {comanda_id}")
                raise HTTPException(status_code=404, detail="Comanda não encontrada.")

            comanda["_id"] = str(comanda["_id"])
            logger.info(f"Comanda {comanda_id} encontrada com sucesso.")
            return Comanda(**comanda)
        except HTTPException as http_ex:
            raise http_ex  # Re-levanta a exceção HTTP já tratada
        except Exception as e:
            logger.exception(f"Erro ao buscar comanda com ID {comanda_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao buscar comanda."
            )

    @staticmethod
    async def update_comanda(comanda_id: str, comanda_data: ComandaUpdate) -> Comanda:
        """Atualiza uma comanda."""
        logger.debug(f"Atualizando comanda com ID: {comanda_id}, dados: {comanda_data}")
        try:
            try:
                object_id = ObjectId(comanda_id)
            except Exception:
                logger.warning(f"ID de comanda inválido: {comanda_id}")
                raise HTTPException(status_code=400, detail="ID de comanda inválido.")

            update_data = comanda_data.model_dump(exclude_unset=True)

            # Impedir a alteração do _id
            if "_id" in update_data:
                del update_data["_id"]

            result = await db.comandas.update_one(
                {"_id": object_id}, {"$set": update_data}
            )

            if result.modified_count == 0:
                logger.warning(f"Comanda não encontrada ou dados iguais: {comanda_id}")
                raise HTTPException(
                    status_code=404, detail="Comanda não encontrada ou dados iguais."
                )

            comanda = await db.comandas.find_one({"_id": object_id})
            comanda["_id"] = str(comanda["_id"])

            logger.info(f"Comanda {comanda_id} atualizada com sucesso.")
            return Comanda(**comanda)
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.exception(f"Erro ao atualizar comanda com ID {comanda_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao atualizar comanda."
            )

    @staticmethod
    async def delete_comanda(comanda_id: str) -> bool:
        """Deleta uma comanda."""
        logger.debug(f"Deletando comanda com ID: {comanda_id}")
        try:
            try:
                object_id = ObjectId(comanda_id)
            except Exception:
                logger.warning(f"ID de comanda inválido: {comanda_id}")
                raise HTTPException(status_code=400, detail="ID de comanda inválido.")

            result = await db.comandas.delete_one({"_id": object_id})
            if result.deleted_count == 0:
                logger.warning(f"Comanda não encontrada: {comanda_id}")
                raise HTTPException(status_code=404, detail="Comanda não encontrada.")

            logger.info(f"Comanda {comanda_id} deletada com sucesso.")
            return True
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.exception(f"Erro ao deletar comanda com ID {comanda_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao deletar comanda."
            )

    @staticmethod
    async def list_comandas(
        page: int = 1,
        limit: int = 10,
        status: Optional[str] = None,
        cliente_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Lista comandas com paginação e filtros."""
        logger.debug(
            f"Listando comandas - página: {page}, limite: {limit}, status: {status}, cliente_id: {cliente_id}"
        )
        try:
            skip = (page - 1) * limit
            query = {}

            if status:
                query["status"] = status
            
            if cliente_id:
                try:
                    ObjectId(cliente_id)
                except Exception:
                    logger.warning(f"ID de cliente inválido: {cliente_id}")
                    raise HTTPException(status_code=400, detail="ID de cliente inválido.")
                query["cliente_id"] = cliente_id
            

            comandas = (
                await db.comandas.find(query)
                .skip(skip)
                .limit(limit)
                .to_list(length=limit)
            )
            total_comandas = await db.comandas.count_documents(query)

            comandas_list = []
            for comanda in comandas:
                comanda["_id"] = str(comanda["_id"])
                comandas_list.append(Comanda(**comanda))

            logger.info(
                f"Listagem de comandas retornou {len(comandas_list)} comandas (total: {total_comandas})"
            )

            return {
                "comandas": comandas_list,
                "pagination": {
                    "total": total_comandas,
                    "currentPage": page,
                    "totalPages": -(-total_comandas // limit),
                    "totalItemsPerPage": limit,
                }
            }
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.exception(f"Erro ao listar comandas: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao listar comandas."
            )

    @staticmethod
    async def num_comandas() -> Dict[str, int]:
        """Retorna o número total de comandas."""
        logger.debug("Contando o número total de comandas.")
        try:
            total_comandas = await db.comandas.count_documents({})
            logger.info(f"Número total de comandas: {total_comandas}")
            return {"total": total_comandas}
        except Exception as e:
            logger.exception(f"Erro ao contar comandas: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao contar comandas."
            )
        
    @staticmethod
    async def close_comanda(comanda_id: str) -> Comanda:
        """Fecha uma comanda."""
        logger.debug(f"Fechando comanda com ID: {comanda_id}")
        try:
            try:
                object_id = ObjectId(comanda_id)
            except Exception:
                logger.warning(f"ID de comanda inválido: {comanda_id}")
                raise HTTPException(status_code=400, detail="ID de comanda inválido.")

            update_data = {"status": "fechada"}

            result = await db.comandas.update_one(
                {"_id": object_id}, {"$set": update_data}
            )

            if result.modified_count == 0:
                logger.warning(f"Comanda não encontrada ou já fechada: {comanda_id}")
                raise HTTPException(
                    status_code=404, detail="Comanda não encontrada ou já fechada."
                )

            comanda = await db.comandas.find_one({"_id": object_id})
            comanda["_id"] = str(comanda["_id"])

            logger.info(f"Comanda {comanda_id} fechada com sucesso.")
            return Comanda(**comanda)
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.exception(f"Erro ao fechar comanda com ID {comanda_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao fechar comanda."
            )
        
    @staticmethod
    async def list_comandas_abertas() -> List[Comanda]:
        """Lista comandas abertas."""
        logger.debug("Listando comandas abertas.")
        try:
            query = {"status": "aberta"}
            comandas = await db.comandas.find(query).to_list(length=1000)

            comandas_list = []
            for comanda in comandas:
                comanda["_id"] = str(comanda["_id"])

                if "cliente_id" in comanda:
                    try:
                        comanda["cliente_id"] = str(ObjectId(comanda["cliente_id"]))
                    except Exception:
                        logger.warning(f"ID de cliente inválido: {comanda['cliente_id']}")
                        raise HTTPException(status_code=400, detail="ID de cliente inválido.")

                comandas_list.append(Comanda(**comanda))

            logger.info(f"Listagem de comandas abertas retornou {len(comandas_list)} comandas.")
            return comandas_list

        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.exception(f"Erro ao listar comandas abertas: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao listar comandas abertas."
            )
        
    @staticmethod
    async def get_cliente_mesa_por_comanda(comanda_id: str) -> dict:
        """Retorna o nome do cliente e a capacidade da mesa associada a uma comanda."""
        logger.debug(f"Buscando cliente e mesa para a comanda com ID: {comanda_id}")
        try:
            try:
                object_id = ObjectId(comanda_id)
            except Exception:
                logger.warning(f"ID de comanda inválido: {comanda_id}")
                raise HTTPException(status_code=400, detail="ID de comanda inválido.")

            comanda = await db.comandas.find_one({"_id": object_id})
            if not comanda:
                logger.warning(f"Comanda não encontrada: {comanda_id}")
                raise HTTPException(status_code=404, detail="Comanda não encontrada.")

            cliente = await db.clientes.find_one({"_id": ObjectId(comanda["cliente_id"])})
            if not cliente:
                logger.warning(f"Cliente não encontrado para comanda: {comanda_id}")
                raise HTTPException(status_code=404, detail="Cliente não encontrado.")

            mesa = await db.mesas.find_one({"_id": ObjectId(cliente["id_mesa"])})
            if not mesa:
                logger.warning(f"Mesa não encontrada para cliente: {cliente['_id']}")
                raise HTTPException(status_code=404, detail="Mesa não encontrada.")

            resultado = {
                "nome_cliente": cliente["nome"],
                "capacidade_mesa": mesa["capacidade"]
            }

            logger.info(f"Dados encontrados para comanda {comanda_id}: {resultado}")
            return resultado
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.exception(f"Erro ao buscar dados para comanda {comanda_id}: {e}")
            raise HTTPException(status_code=500, detail="Erro interno ao buscar dados da comanda.")