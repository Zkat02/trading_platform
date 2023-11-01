from base.repositories import BaseRepository


class BaseService:
    def __init__(self, model):
        self.repository = BaseRepository(model)

    def get_by_id(self, obj_id):
        return self.repository.get_by_id(obj_id)

    def get_all(self):
        return self.repository.get_all()

    def create(self, **kwargs):
        return self.repository.create(**kwargs)

    def update(self, obj_id, **kwargs):
        obj = self.get_by_id(obj_id)
        if obj:
            self.repository.update(obj, **kwargs)
            return obj
        return None

    def delete(self, obj_id):
        obj = self.get_by_id(obj_id)
        if obj:
            self.repository.delete(obj)
            return True
        return False
