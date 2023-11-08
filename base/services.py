from typing import Type

from django.db.models import Model, QuerySet

from base.repositories import BaseRepository


class BaseService:
    def __init__(self, model: Type[Model], repository: Type[BaseRepository]) -> None:
        self.repository = repository(model)

    def get_by_id(self, obj_id: int) -> Model:
        return self.repository.get_by_id(obj_id)

    def get_all(self) -> QuerySet[Model]:
        return self.repository.get_all()

    def create(self, **kwargs) -> Model:
        return self.repository.create(**kwargs)

    def update(self, obj_id: int, **kwargs) -> Model:
        obj = self.get_by_id(obj_id)
        self.repository.update(obj, **kwargs)
        return obj

    def delete(self, obj_id: int) -> bool:
        obj = self.get_by_id(obj_id)
        if obj:
            self.repository.delete(obj)
            return True
        return False

    def filter_objs(self, **kwargs) -> QuerySet[Model]:
        return self.repository.filter_objs(**kwargs)
