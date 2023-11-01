from base.exceptions import Base4xxException


class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_by_id(self, obj_id):
        try:
            return self.model.objects.get(obj_id=obj_id)
        except self.model.DoesNotExist:
            raise Base4xxException(f"Object of <{self.model.__name__}> by this obj_id not exist.")

    def get_all(self):
        return self.model.objects.all()

    def create(self, **kwargs):
        return self.model.objects.create(**kwargs)

    def update(self, obj, **kwargs):
        for key, value in kwargs.items():
            setattr(obj, key, value)
        obj.save()

    def delete(self, obj):
        obj.delete()
