from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from bson import ObjectId
from app.models import *
from app.config import *

class IngredienteController:
    @staticmethod
    async def create_ingrediente(ingrediente: IngredienteCreate) -> Ingrediente:
        try:
            ingrediente_dict = ingrediente.model_dump(by_alias=True, exclude={"id"})
            novo_ingrediente = await db.ingredientes.insert_one(ingrediente_dict)
            response = await db.ingredientes.find_one({"_id": novo_ingrediente.inserted_id})

            if not response:
                logger.error("Erro ao criar ingrediente no banco de dados.")
                raise HTTPException(
                    status_code=500, detail="Erro ao criar ingrediente no banco de dados."
                )

            response["_id"] = str(response["_id"])
            logger.info(f"Ingrediente {response['_id']} criado com sucesso.")
            return Ingrediente(**response)

        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.error(f"Erro ao criar ingrediente: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao criar ingrediente."
            )

    @staticmethod
    async def get_ingrediente(ingrediente_id: str) -> Ingrediente:
        try:
            try:
                object_id = ObjectId(ingrediente_id)
            except Exception:
                logger.warning(f"ID de ingrediente inválido: {ingrediente_id}")
                raise HTTPException(status_code=400, detail="ID de ingrediente inválido.")

            ingrediente = await db.ingredientes.find_one({"_id": object_id})
            if not ingrediente:
                logger.warning(f"Ingrediente não encontrado com ID: {ingrediente_id}")
                raise HTTPException(status_code=404, detail="Ingrediente não encontrado.")

            ingrediente["_id"] = str(ingrediente["_id"])
            logger.info(f"Ingrediente {ingrediente_id} encontrado com sucesso.")
            return Ingrediente(**ingrediente)
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.error(f"Erro ao buscar ingrediente com ID {ingrediente_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao buscar ingrediente."
            )

    @staticmethod
    async def update_ingrediente(ingrediente_id: str, ingrediente_data: IngredienteUpdate) -> Ingrediente:
        try:
            try:
                object_id = ObjectId(ingrediente_id)
            except Exception:
                logger.warning(f"ID de ingrediente inválido: {ingrediente_id}")
                raise HTTPException(status_code=400, detail="ID de ingrediente inválido.")

            update_data = ingrediente_data.model_dump(exclude_unset=True)

            if "_id" in update_data:
                del update_data["_id"]

            result = await db.ingredientes.update_one(
                {"_id": object_id}, {"$set": update_data}
            )

            if result.modified_count == 0:
                logger.warning(f"Ingrediente não encontrado ou dados iguais: {ingrediente_id}")
                raise HTTPException(
                    status_code=404, detail="Ingrediente não encontrado ou dados iguais."
                )

            ingrediente = await db.ingredientes.find_one({"_id": object_id})
            ingrediente["_id"] = str(ingrediente["_id"])

            logger.info(f"Ingrediente {ingrediente_id} atualizado com sucesso.")
            return Ingrediente(**ingrediente)
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.error(f"Erro ao atualizar ingrediente com ID {ingrediente_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao atualizar ingrediente."
            )

    @staticmethod
    async def delete_ingrediente(ingrediente_id: str) -> bool:
        try:
            try:
                object_id = ObjectId(ingrediente_id)
            except Exception:
                logger.warning(f"ID de ingrediente inválido: {ingrediente_id}")
                raise HTTPException(status_code=400, detail="ID de ingrediente inválido.")

            result = await db.ingredientes.delete_one({"_id": object_id})
            if result.deleted_count == 0:
                logger.warning(f"Ingrediente não encontrado: {ingrediente_id}")
                raise HTTPException(status_code=404, detail="Ingrediente não encontrado.")

            logger.info(f"Ingrediente {ingrediente_id} deletado com sucesso.")
            return True
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.error(f"Erro ao deletar ingrediente com ID {ingrediente_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao deletar ingrediente."
            )

    @staticmethod
    async def list_ingredientes(
        page: int = 1,
        limit: int = 10,
        nome: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            skip = (page - 1) * limit
            query = {}

            if nome:
                query["nome"] = {"$regex": nome, "$options": "i"}

            ingredientes = (
                await db.ingredientes.find(query)
                .skip(skip)
                .limit(limit)
                .to_list(length=limit)
            )
            total_ingredientes = await db.ingredientes.count_documents(query)

            ingredientes_list = []
            for ingrediente in ingredientes:
                ingrediente["_id"] = str(ingrediente["_id"])
                ingredientes_list.append(Ingrediente(**ingrediente))

            logger.info(
                f"Listagem de ingredientes retornou {len(ingredientes_list)} ingredientes (total: {total_ingredientes})"
            )

            return {
                "ingredientes": ingredientes_list,
                "pagination": {
                    "total": total_ingredientes,
                    "currentPage": page,
                    "totalPages": -(-total_ingredientes // limit),
                    "totalItemsPerPage": limit,
                },
            }
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            logger.error(f"Erro ao listar ingredientes: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao listar ingredientes."
            )

    @staticmethod
    async def num_ingredientes() -> Dict[str, int]:
        try:
            total_ingredientes = await db.ingredientes.count_documents({})
            logger.info(f"Número total de ingredientes: {total_ingredientes}")
            return {"total": total_ingredientes}
        except Exception as e:
            logger.error(f"Erro ao contar ingredientes: {e}")
            raise HTTPException(
                status_code=500, detail="Erro interno ao contar ingredientes."
            )