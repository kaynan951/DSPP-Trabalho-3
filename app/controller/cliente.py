from app.models import *
from app.config import *
from typing import Optional, Dict, Any
from fastapi import HTTPException
from bson import ObjectId

#python -m uvicorn main:app --reload

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
        """Lista clientes com paginação e filtros."""
        logger.debug(
            f"Listando clientes - página: {page}, limite: {limit}, nome: {nome}, email: {email}, cpf: {cpf}"
        )
        try:
            skip = (page - 1) * limit  # Calcula quantos documentos pular
            query = {}  # Query inicial vazia

            # Adiciona filtros se forem fornecidos
            if nome:
                query["nome"] = {"$regex": nome, "$options": "i"}  # Case-insensitive search
            if email:
                query["email"] = {"$regex": email, "$options": "i"}
            if cpf:
                query["cpf"] = cpf

            # Busca os clientes com paginação
            clientes = (
                await db.clientes.find(query)
                .skip(skip)
                .limit(limit)
                .to_list(length=limit)
            )
            total_clientes = await db.clientes.count_documents(query)  # Total de clientes (sem paginação)

            # Converte _id para string e cria objetos Cliente
            clientes_list = []
            for cliente in clientes:
                cliente["_id"] = str(cliente["_id"])
                clientes_list.append(Cliente(**cliente))

            logger.info(
                f"Listagem de clientes retornou {len(clientes_list)} clientes (total: {total_clientes})"
            )

            return {
                "clientes": clientes_list,
                "pagination": {
                    "total": total_clientes,
                    "currentPage": page,
                    "totalPages": -(-total_clientes // limit),
                    "totalItemsPerPage": limit,
                },
            }
        except Exception as e:
            logger.exception(f"Erro ao listar clientes: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao listar clientes."
            )

    @staticmethod
    async def get_cliente(cliente_id: str) -> Cliente:
        """Busca um cliente pelo ID."""
        logger.debug(f"Buscando cliente com ID: {cliente_id}")
        try:
            try:
                object_id = ObjectId(cliente_id)  # Tenta criar o ObjectId
            except Exception:
                logger.warning(f"ID de cliente inválido: {cliente_id}")
                raise HTTPException(status_code=400, detail="ID de cliente inválido.")

            cliente = await db.clientes.find_one({"_id": object_id})
            if not cliente:
                logger.warning(f"Cliente não encontrado com ID: {cliente_id}")
                raise HTTPException(status_code=404, detail="Cliente não encontrado.")

            cliente["_id"] = str(cliente["_id"])  # Converte _id para string
            logger.info(f"Cliente {cliente_id} encontrado com sucesso.")
            return Cliente(**cliente)

        except HTTPException as http_ex:
            raise http_ex  # Re-levanta a exceção HTTP já tratada
        except Exception as e:  # Captura qualquer outro erro
            logger.exception(f"Erro ao buscar cliente com ID {cliente_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao buscar cliente."
            )

    @staticmethod
    async def update_cliente(cliente_id: str, cliente_data: ClienteUpdate) -> Cliente:
        """Atualiza um cliente."""
        logger.debug(f"Atualizando cliente com ID: {cliente_id}, dados: {cliente_data}")
        try:
            try:
                object_id = ObjectId(cliente_id)  # Tenta criar o ObjectId
            except Exception:
                logger.warning(f"ID de cliente inválido: {cliente_id}")
                raise HTTPException(status_code=400, detail="ID de cliente inválido.")
                
            # Converte o model para um dict, excluindo campos que não foram enviados
            update_data = cliente_data.model_dump(exclude_unset=True)

            # Garante que não está tentando atualizar o _id
            if "_id" in update_data:
                del update_data["_id"]

            # Atualiza o cliente no banco de dados
            result = await db.clientes.update_one(
                {"_id": object_id}, {"$set": update_data}
            )

            if result.modified_count == 0:
                logger.warning(f"Cliente não encontrado ou dados iguais: {cliente_id}")
                raise HTTPException(
                    status_code=404, detail="Cliente não encontrado ou dados iguais."
                )

            # Busca o cliente atualizado
            cliente = await db.clientes.find_one({"_id": object_id})
            cliente["_id"] = str(cliente["_id"])

            logger.info(f"Cliente {cliente_id} atualizado com sucesso.")
            return Cliente(**cliente)

        except HTTPException as http_ex:
            raise http_ex  # Re-levanta a exceção HTTP já tratada
        except Exception as e:  # Captura qualquer outro erro
            logger.exception(f"Erro ao atualizar cliente com ID {cliente_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao atualizar cliente."
            )

    @staticmethod
    async def delete_cliente(cliente_id: str) -> bool:
        """Deleta um cliente."""
        logger.debug(f"Deletando cliente com ID: {cliente_id}")
        try:
            try:
                object_id = ObjectId(cliente_id)  # Tenta criar o ObjectId
            except Exception:
                logger.warning(f"ID de cliente inválido: {cliente_id}")
                raise HTTPException(status_code=400, detail="ID de cliente inválido.")

            result = await db.clientes.delete_one({"_id": object_id})
            if result.deleted_count == 0:
                logger.warning(f"Cliente não encontrado: {cliente_id}")
                raise HTTPException(status_code=404, detail="Cliente não encontrado.")

            logger.info(f"Cliente {cliente_id} deletado com sucesso.")
            return True  # Indica que a deleção foi bem-sucedida

        except HTTPException as http_ex:
            raise http_ex  # Re-levanta a exceção HTTP já tratada
        except Exception as e:  # Captura qualquer outro erro
            logger.exception(f"Erro ao deletar cliente com ID {cliente_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao deletar cliente."
            )

    @staticmethod
    async def num_cliente() -> Dict[str, int]:
        """Retorna o número total de clientes."""
        logger.debug("Contando o número total de clientes.")
        try:
            total_clientes = await db.clientes.count_documents({})
            logger.info(f"Número total de clientes: {total_clientes}")
            return {"total": total_clientes}
        except Exception as e:
            logger.exception(f"Erro ao contar clientes: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao contar clientes."
            )