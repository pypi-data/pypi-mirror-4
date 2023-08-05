def map_single_object(clazz, json, **kwargs):
    obj = clazz()
    for k, v in json.iteritems():
        setattr(obj, k, v)
    for k, v in kwargs.iteritems():
        setattr(obj, k, v)
    return obj


def map_object(clazz, json, **kwargs):
    if list == type(json):
        result = [map_single_object(clazz, item, **kwargs) for item in json]
        return result
    else:
        return map_single_object(clazz, json, **kwargs)
