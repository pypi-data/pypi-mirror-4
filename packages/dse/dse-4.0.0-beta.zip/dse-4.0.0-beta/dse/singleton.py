from django.db.models.loading import get_models
from dse import DSE


# credit: http://greengiraffe.posterous.com/singleton-pattern-in-python
def singleton(cls, model):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls(model)
        return instances[cls]
    return getinstance


class _Models:
    pass


Models = _Models()


for model in get_models():
    setattr(Models, model._meta.object_name, singleton(DSE, model))
