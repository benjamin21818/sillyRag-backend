from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

class BaseDao:
    def __init__(self,session: AsyncSession,model,primary_key:str='uuid'):
        self.session = session          # 数据库会话
        self.model = model              # 表模版
        self.primary_key = primary_key  


    # 增
    async def create(self,**kwargs):
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()          # 会生成SQL INSERT INTO ... 语句并发送给数据库
        await self.session.refresh(instance) # 会发送一个 SELECT 查询，重新从数据库拉取该记录的最新数据，并更新到 instance 对象中
        return instance
    async def create_batch(self,objects:list):
        instances = []
        for obj in objects:
            kwargs = {}
            for key,value in obj:
                kwargs[key] = value
            instance = self.model(**kwargs)
            instances.append(instance)
        self.session.add_all(instances)
        await self.session.commit()
        for instance in instances: # 可选：如果需要刷新实例以获取数据库生成的字段
            await self.session.refresh(instance)
        return instances


    # 删
    async def delete_by_primary_key(self,primary_key):
        stmt = delete(self.model).where(getattr(self.model,self.primary_key)==primary_key)
        await self.session.execute(stmt)
        await self.session.commit()
        return True


    # 改
    async def update_by_primary_key(self,primary_key,**kwargs):
        stmt = update(self.model).where(getattr(self.model,self.primary_key)==primary_key).values(**kwargs).returning(self.model)
        result = await self.session.execute(stmt) # 由于使用了returning，所以会返回更新后的记录
        await self.session.commit()
        return result.scalar_one_or_none()


    # 查
    async def get_by_primary_key(self,primary_key):
        stmt = select(self.model).where(getattr(self.model,self.primary_key)==primary_key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    async def get_all(self):
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    