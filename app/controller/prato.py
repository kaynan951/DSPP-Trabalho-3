from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from bson import ObjectId
from app.models import *  # Certifique-se de que Prato existe em models.py
from app.config import *  # Importe a configuração do banco de dados (db)
from .comanda import ComandaController # Importa o comanda controller

class PratoController:
    @staticmethod
    async def create_prato(prato: PratoCreate) -> Prato:
        """Cria um novo prato."""
        logger.debug(f"Criando prato: {prato.nome}")
        try:
            prato_dict = prato.model_dump(by_alias=True, exclude={"id"})
            novo_prato = await db.pratos.insert_one(prato_dict)
            response = await db.pratos.find_one({"_id": novo_prato.inserted_id})

            if not response:
                logger.error("Erro ao criar prato no banco de dados.")
                raise HTTPException(
                    status_code=500, detail="Erro ao criar prato no banco de dados."
                )

            response["_id"] = str(response["_id"])
            logger.info(f"Prato {response['_id']} criado com sucesso.")
            return Prato(**response)

        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.exception(f"Erro ao criar prato: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao criar prato."
            )

    @staticmethod
    async def get_prato(prato_id: str) -> Prato:
        """Busca um prato pelo ID."""
        logger.debug(f"Buscando prato com ID: {prato_id}")
        try:
            try:
                object_id = ObjectId(prato_id)
            except Exception:
                logger.warning(f"ID de prato inválido: {prato_id}")
                raise HTTPException(status_code=400, detail="ID de prato inválido.")

            prato = await db.pratos.find_one({"_id": object_id})
            if not prato:
                logger.warning(f"Prato não encontrado com ID: {prato_id}")
                raise HTTPException(status_code=404, detail="Prato não encontrado.")

            prato["_id"] = str(prato["_id"])
            logger.info(f"Prato {prato_id} encontrado com sucesso.")
            return Prato(**prato)
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.exception(f"Erro ao buscar prato com ID {prato_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao buscar prato."
            )

    @staticmethod
    async def update_prato(prato_id: str, prato_data: PratoUpdate) -> Prato:
        """Atualiza um prato."""
        logger.debug(f"Atualizando prato com ID: {prato_id}, dados: {prato_data}")
        try:
            try:
                object_id = ObjectId(prato_id)
            except Exception:
                logger.warning(f"ID de prato inválido: {prato_id}")
                raise HTTPException(status_code=400, detail="ID de prato inválido.")

            update_data = prato_data.model_dump(exclude_unset=True)

            # Impedir a alteração do _id
            if "_id" in update_data:
                del update_data["_id"]

            result = await db.pratos.update_one(
                {"_id": object_id}, {"$set": update_data}
            )

            if result.modified_count == 0:
                logger.warning(f"Prato não encontrado ou dados iguais: {prato_id}")
                raise HTTPException(
                    status_code=404, detail="Prato não encontrado ou dados iguais."
                )

            prato = await db.pratos.find_one({"_id": object_id})
            prato["_id"] = str(prato["_id"])

            logger.info(f"Prato {prato_id} atualizado com sucesso.")
            return Prato(**prato)
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.exception(f"Erro ao atualizar prato com ID {prato_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao atualizar prato."
            )

    @staticmethod
    async def delete_prato(prato_id: str) -> bool:
        """Deleta um prato."""
        logger.debug(f"Deletando prato com ID: {prato_id}")
        try:
            try:
                object_id = ObjectId(prato_id)
            except Exception:
                logger.warning(f"ID de prato inválido: {prato_id}")
                raise HTTPException(status_code=400, detail="ID de prato inválido.")

            result = await db.pratos.delete_one({"_id": object_id})
            if result.deleted_count == 0:
                logger.warning(f"Prato não encontrado: {prato_id}")
                raise HTTPException(status_code=404, detail="Prato não encontrado.")

            logger.info(f"Prato {prato_id} deletado com sucesso.")
            return True
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.exception(f"Erro ao deletar prato com ID {prato_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao deletar prato."
            )

    @staticmethod
    async def list_pratos(
        page: int = 1,
        limit: int = 10,
        nome: Optional[str] = None,
        categoria: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Lista pratos com paginação e filtros."""
        logger.debug(
            f"Listando pratos - página: {page}, limite: {limit}, nome: {nome}, categoria: {categoria}"
        )
        try:
            skip = (page - 1) * limit
            query = {}

            if nome:
                query["nome"] = {"$regex": nome, "$options": "i"}  # Case-insensitive search
            if categoria:
                query["categoria"] = categoria
            
            pratos = (
                await db.pratos.find(query)
                .skip(skip)
                .limit(limit)
                .to_list(length=limit)
            )
            total_pratos = await db.pratos.count_documents(query)

            pratos_list = []
            for prato in pratos:
                prato["_id"] = str(prato["_id"])
                pratos_list.append(Prato(**prato))

            logger.info(
                f"Listagem de pratos retornou {len(pratos_list)} pratos (total: {total_pratos})"
            )

            return {
                "pratos": pratos_list,
                "pagination": {
                    "total": total_pratos,
                    "currentPage": page,
                    "totalPages": -(-total_pratos // limit),
                    "totalItemsPerPage": limit,
                },
            }
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.exception(f"Erro ao listar pratos: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao listar pratos."
            )

    @staticmethod
    async def num_pratos() -> Dict[str, int]:
        """Retorna o número total de pratos."""
        logger.debug("Contando o número total de pratos.")
        try:
            total_pratos = await db.pratos.count_documents({})
            logger.info(f"Número total de pratos: {total_pratos}")
            return {"total": total_pratos}
        except Exception as e:
            logger.exception(f"Erro ao contar pratos: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao contar pratos."
            )