# -*- coding:utf-8 -*-
def models_to_dict(model):
    """peewee Model sequences into Dict
    :param model:peewee query model object
    :return: dict
    """
    if not model:
        raise TypeError("not find dataBase object is None")
    if hasattr(model, 'get_query_meta'):
        model_filed = model.get_query_meta()[0]
        return [{l.name: getattr(i, l.name) for l in model_filed} for i in model]
    model_filed = model.select().get_query_meta()[0]
    return {l.name: getattr(model, l.name) for l in model_filed}
