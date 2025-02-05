from app.models import *
from app.config import *
from typing import Optional, Dict, Any
from fastapi import HTTPException
from bson import ObjectId


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
        return {"mesas": mesas, "total": total, "page": page, "limit": limit}

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