# -*- coding:utf-8 -*-
import time
from collections import UserDict
from peewee import Field
from peewee import Model


class ModelsToDict(dict):
    """peewee to dict
    :type data: object
    :type is_shield: bool
    :type shield_field: list [peewee Field, "name"]
    :type field_name: dict {filed or peewee Field: "name"}
    :type field_handle: dict {filed or peewee Field: func}
    :param data: peewee query object
    :param is_shield: is shield kw filed
    :param shield_field: shield filed
    :param field_handle: apponit filed handle
    :param field_name: apponit filed Modified alias
    """

    def __bool__(self):
        if isinstance(self._data, list):
            return bool(len(self._data))
        if isinstance(self._data, dict):
            return bool(self._data)

    def __getitem__(self, item):
        print(item)

    def __init__(self, **kw):
        self._data = kw['data']
        self.is_shield = kw.get('is_shield', True)
        self.field_name = self._kw_handle(kw.get('field_name', {}))
        self.shield_field = self._kw_handle([] if kw.get('shield_field') is None else kw['shield_field'])
        self.field_handle = self._kw_handle({} if kw.get('field_handle') is None else kw['field_handle'])
        self._data = self._models_dict()
        if isinstance(self._data, dict):
            super(ModelsToDict, self).__init__(**self._data)

    @property
    def data(self):
        return self._data

    def _kw_handle(self, kw):
        if isinstance(kw, list):
            tmp_ = []
            for i in kw:
                if isinstance(i, Field):
                    tmp_.append(i.name)
                elif isinstance(i, str):
                    tmp_append(i)
                else:
                    raise TypeError("{} not peewee Field or not str".format(i))
            return tmp_
        elif isinstance(kw, dict):
            tmp_ = {}
            for i in kw:
                if isinstance(i, Field):
                    tmp_[i.name] = kw[i]
                elif isinstance(i, str):
                    tmp_[i] = kw[i]
                else:
                    raise TypeError("{} not peewee Field or not str".format(i))
            return tmp_
        else:
            raise TypeError("{} not list or not dict".fromat(kw))

    def _models_dict(self):
        if not self._data:
            return {}
        if isinstance(self._data, list):
            # all
            return_data = []
            for objects in self._data:
                fileds_object = objects.select().get_query_meta()[0]
                tmp_dict = {}
                for _filed in fileds_object:
                    if _filed.name in self.shield_field and self.is_shield:
                        continue
                    _ = getattr(objects, _filed.name)
                    _field_name = _filed.name
                    if _filed.name in self.field_handle:
                        _ = self.field_handle[_filed.name](_)
                    if _filed.name in self.field_name:
                        _field_name = self.field_name[_field_name]
                    tmp_dict[_field_name] = _
                return_data.append(tmp_dict)
            return return_data
        fileds_object = self._data.select().get_query_meta()[0]
        return_data = {}
        for _filed in fileds_object:
            if self.is_shield and _filed.name in self.shield_field:
                # shield
                continue
            _ = getattr(self._data, _filed.name)
            _field_name = _filed.name
            if _filed.name in self.field_handle:
                _ = self.field_handle[_filed.name](_)
            if _filed.name in self.field_name:
                _field_name = self.field_name[_field_name]
            return_data[_field_name] = _
        return return_data


def models_to_dict(model):
    """peewee Model sequences into Dict
    :param model:peewee query model object
    :return: dict
    """
    if not model:
        return {}
    if hasattr(model, 'get_query_meta'):
        model_filed = model.get_query_meta()[0]
        return [{l.name: getattr(i, l.name) for l in model_filed} for i in model]
    model_filed = model.select().get_query_meta()[0]
    return {l.name: getattr(model, l.name) for l in model_filed}


