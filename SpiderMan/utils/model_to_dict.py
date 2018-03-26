# -*- coding:utf-8 -*-
from peewee import Field


class ModelsToDict():
    """peewee to dict
    Usage:
        >>> import ModelsToDict
        >>> query = MyModel.select().where(id=1)
        >>>ModelsToDict(query)
        {
            "id": 1,
            "name": 2
        }
        >>>querys = MyModel.select()
        >>> ModelsToDict(query, shield_field=['name'], field_name={"id": "id_"}, field_handle={"id": lambda x: str(x)}).data
        [
            {"id_": "1"},{"id_": "2"}, {"id_", :"3"}
        ]
        >>>

    :type data: object
    :type is_shield: bool
    :type shield_field: list [peewee Field, "name"]
    :type field_name: dict {filed or peewee Field: "name"}
    :type field_handle: dict {filed or peewee Field: func}
    :param data: peewee 查询对象
    :param is_shield: 是否需要屏蔽,
    :param shield_field: 屏蔽的字段, 取决于 is_shield
    :param field_handle: 对特定的字段进行处理
    :param field_name: 对特定的字段修改名称
    """

    def __bool__(self):
        if isinstance(self._data, list):
            return bool(len(self._data))
        if isinstance(self._data, dict):
            return bool(self._data)

    def __getitem__(self, item):
        print(item)

    def __init__(self, data, **kw):
        self._data = data
        self.is_shield = kw.get('is_shield', True)
        self.field_name = self._kw_handle(kw.get('field_name', {}))
        self.shield_field = self._kw_handle([] if kw.get('shield_field') is None else kw['shield_field'])
        self.field_handle = self._kw_handle({} if kw.get('field_handle') is None else kw['field_handle'])
        self._data = self._models_dict()
        if isinstance(self._data, dict):
            dict.__init__(**self._data)
        if isinstance(self._data, list):
            list.__init__(self._data)

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



