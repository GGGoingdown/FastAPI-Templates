import typing
from tortoise.models import Model
from tortoise.queryset import QuerySet

from src.pkg import models as db_models, schema


ModelType = typing.TypeVar("ModelType", bound=Model)


class CRUDBase(typing.Generic[ModelType]):
    __slots__ = ("model",)

    def __init__(self, model: typing.Type[ModelType]):
        self.model = model

    async def _create(self, **kwargs: typing.Any) -> ModelType:
        _model = await self.model.create(**kwargs)
        return _model

    def _filter(
        self,
        lock: bool = False,
        prefetch: typing.Iterable[str] = None,
        order_by: str = None,
        **filter: typing.Any,
    ) -> QuerySet:
        model = self.model.filter(**filter)
        if lock:
            model = model.select_for_update()

        if prefetch:
            model = model.prefetch_related(*prefetch)

        if order_by:
            model = model.order_by(order_by)

        return model

    async def filter_one(
        self,
        lock: bool = False,
        prefetch: typing.Iterable[str] = None,
        order_by: str = None,
        **filter: typing.Any,
    ) -> typing.Optional[ModelType]:
        model = self._filter(lock, prefetch, order_by, **filter)
        _model = await model.first()
        return _model

    async def filter_many(
        self,
        lock: bool = False,
        prefetch: typing.Iterable[str] = None,
        order_by: str = None,
        offset: int = 0,
        limit: int = 10,
        **filter: typing.Any,
    ) -> typing.Iterable[ModelType]:
        model = self._filter(lock, prefetch, order_by, **filter)
        _model = await model.all().offset(offset).limit(limit)
        return _model

    async def select_update(
        self, update_schema: typing.Dict, **filter: typing.Any
    ) -> int:
        return (
            await self.model.filter(**filter)
            .select_for_update()
            .update(**update_schema)
        )


class UserRepository(CRUDBase):
    def __init__(self):
        super().__init__(db_models.User)

    async def create(self, password_hash: str, **fields: typing.Any) -> schema.UserInDB:
        model = await super()._create(**fields, password_hash=password_hash)
        return schema.UserInDB.model_validate(model)
