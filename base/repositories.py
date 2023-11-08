from typing import Type

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model, QuerySet

from base.exceptions import BaseClientException


class BaseRepository:
    def __init__(self, model: Type[Model]) -> None:
        self.model = model

    def get_by_id(self, obj_id: int) -> Model:
        try:
            return self.model.objects.get(id=obj_id)
        except ObjectDoesNotExist:
            raise BaseClientException(
                f"Object of <{self.model.__name__}> by this obj_id not exist."
            )

    def get_all(self) -> QuerySet[Model]:
        return self.model.objects.all()

    def create(self, **kwargs) -> Model:
        return self.model.objects.create(**kwargs)

    def update(self, obj: Model, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(obj, key, value)
        obj.save()

    def delete(self, obj: Model) -> None:
        obj.delete()

    def filter_objs(self, **kwargs) -> QuerySet[Model]:
        return self.model.objects.filter(**kwargs)
