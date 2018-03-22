import asyncio
import peewee
from peewee_async import Manager


class MyManager(Manager):
    """修改父類get 方法, 使得能够自动分辨返回list 还是单个对象,
        如果查询对象不存在只会返回None , 不再会报错
    """
    @asyncio.coroutine
    def get(self, source_, *args, **kwargs):
        """Get the model instance.

        :param source_: model or base query for lookup

        Example::

            async def my_async_func():
                obj1 = await objects.get(MyModel, id=1)
                obj2 = await objects.get(MyModel, MyModel.id == 1)
                obj3 = await objects.get(MyModel.select().where(MyModel.id == 1))

        All will return `MyModel` instance with `id = 1`
        """
        yield from self.connect()
        is_all = False
        if isinstance(source_, peewee.Query):
            query = source_
            model = query.model_class
            is_all = True
        else:
            query = source_.select()
            model = source_

        conditions = list(args) + [(getattr(model, k) == v)
                                   for k, v in kwargs.items()]

        if conditions:
            query = query.where(*conditions)

        try:
            result = yield from self.execute(query)
            if is_all is False:
                return list(result)[0]
            return list(result)
        except IndexError as f:
            print(f)
            return None


    @asyncio.coroutine
    def delete(self, obj, recursive=False, delete_nullable=False):
        """Delete object from database.
        """
        if obj is None:
            return None
        if recursive:
            dependencies = obj.dependencies(delete_nullable)
            for cond, fk in reversed(list(dependencies)):
                model = fk.model_class
                if fk.null and not delete_nullable:
                    sq = model.update(**{fk.name: None}).where(cond)
                else:
                    sq = model.delete().where(cond)
                yield from self.execute(sq)

        query = obj.delete().where(obj._pk_expr())
        return (yield from self.execute(query))

    @asyncio.coroutine
    def create(self, model_, **data):
        """Create a new object saved to database.
        """
        inst = model_(**data)
        query = model_.insert(**dict(inst._data))
        try:
            pk = yield from self.execute(query)
        except peewee.IntegrityError:
            return None
        if pk is None:
            pk = inst._get_pk_value()
        inst._set_pk_value(pk)
        inst._prepare_instance()
        return inst