from typing import List, Type, TypeVar, Generic
from pydantic import BaseModel
from src.dao.base_dao import BaseDao

DTOType = TypeVar("DTOType", bound=BaseModel)  # DTO类型

class BaseService(Generic[DTOType]):

    def __init__(self,dao:BaseDao,dto_class:Type[DTOType]):
        self.dao = dao
        self.dto_class = dto_class


    # 增
    async def create(self,**kwargs) -> DTOType:
        instance = await self.dao.create(**kwargs)
        return self.dto_class.model_validate(instance)
    async def create_batch(self,objects:list[DTOType]) -> List[DTOType]:
        instances = await self.dao.create_batch(objects)
        return [self.dto_class.model_validate(instance) for instance in instances]

    
    # 删
    async def delete_by_primary_key(self,primary_key):
        return await self.dao.delete_by_primary_key(primary_key)


    # 改
    async def update_by_primary_key(self,primary_key,**kwargs) -> DTOType:
        instance = await self.dao.update_by_primary_key(primary_key,**kwargs)
        return self.dto_class.model_validate(instance)


    # 查
    async def get_by_primary_key(self,primary_key) -> DTOType:
        instance = await self.dao.get_by_primary_key(primary_key)
        if instance:
            return self.dto_class.model_validate(instance)
        else:
            return None
    async def get_all(self) -> List[DTOType]:
        instances = await self.dao.get_all()
        try:
            if instances:
                return [self.dto_class.model_validate(instance) for instance in instances]
        except Exception as e:
            print(e)
            raise
        return []