# -*- coding: utf-8 -*-


def walk_dict(a_dict, path):
    """ Возвращает значение из словаря по ключу-пути

    :param a_dict: словарь для поиска
    :param path: путь в формате 'key.sub_key.sub_sub_key'
    """
    path_list = path.split('.')
    result = a_dict
    for p in path_list:
        if a_dict:
            result = result.get(p, {})
    return result


def map_item(obj, item, mapper):
    """ Рекурсивно мапит данные из словаря по конфигу на объект

    :param obj: объект для маппинга
    :param item: словарь с данными
    :param mapper: конфиг для маппинга
    :return: промапленный объект
    """
    for map_name, field_name in mapper.iteritems():
        if dict == type(field_name):
            wd = walk_dict(item, map_name)
            if list == type(wd):
                obj['photos'] = []
                for i in wd:
                    o = map_item(dict(), i, field_name)
                    obj['photos'].append(o)
            else:
                map_item(obj, wd, field_name)
        else:
            value = item.get(map_name, None)
            if value in ('true', 'false'):
                value = True if value == 'true' else False
            obj[field_name] = value
    return obj


def mapper(mapping, json):
    """ Мапит объект clazz по данным из json'а по конфигу mapper

    :param clazz: класс с конфигом маппинга и тип для создаваемых объектов
    :param json: json данные
    :param mapper: dict-конфиг для маппинга с соответствием цепочек лючей из json'а и полей объекта
    :return: список созданных объектов
    """
    key = mapping.keys()[0]
    json = walk_dict(json, key)
    assert json, 'Key %s not found in response' % key

    obj = dict()
    obj = map_item(obj, json, mapping.get(key))
    return obj


def loop_mapper(mapping, json):
    """ Мапит циклически объект clazz по данным из json'а по конфигу mapper

    :param clazz: класс с конфигом маппинга и тип для создаваемых объектов
    :param mapper: dict-конфиг для маппинга с соответствием цепочек лючей из json'а и полей объекта
    :param json: json данные
    :return: список созданных объектов
    """
    assert mapping.keys(), 'Loop key not found in mapping <%s>' % mapping
    loop_key = mapping.keys()[0]
    json_loop = walk_dict(json, loop_key)
    assert json_loop, 'Key %s not found in response' % loop_key
    objects = []

    if dict == type(json_loop):
        obj = map_item(dict(), json_loop, mapping.get(loop_key))
        objects.append(obj)
    else:
        for item in json_loop:
            obj = map_item(dict(), item, mapping.get(loop_key))
            objects.append(obj)

    return objects