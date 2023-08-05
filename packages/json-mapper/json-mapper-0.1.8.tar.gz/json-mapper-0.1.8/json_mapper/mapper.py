# -*- coding: utf-8 -*-


def walk_dict(a_dict, path, strict=False):
    """ Return subdict for key path, e.g. key.subkey.subsubkey """
    path_list = path.split('.')
    result = a_dict
    for p in path_list:
        if a_dict:
            if strict:
                result = result[p]
            else:
                result = result.get(p, {})
    return result


def get_loop_params(key):
    """ {loop=>name}SomeKey. Return key without {...} pattern and prop e.g. name """
    prop = key[7:key.find('}')]
    key = key[key.find('}') + 1:]
    return key, prop


def is_loop_key(key):
    """ Is loop key """
    if '{' in key and '}' in key:
        return True
    else:
        return False


def map_json(mapping_config, json_data, strict=False):
    result = {}

    for key, config in mapping_config.iteritems():
        key = key.strip().replace(' ', '')

        if dict == type(config):
            if is_loop_key(key):
                key, prop = get_loop_params(key)
                list_result = []
                list_json = walk_dict(json_data, key, strict)
                for lj in list_json:
                    list_result.append(
                        map_json(config, lj)
                    )
                result[prop] = list_result
            else:
                result.update(
                    map_json(config, walk_dict(json_data, key, strict))
                )
        elif str == type(config):
            if is_loop_key(key):
                key, prop = get_loop_params(key)
                list_result = []
                list_json = walk_dict(json_data, key, strict)
                for lj in list_json:
                    list_result.append(
                        lj[config]
                    )
                result[prop] = list_result
            else:
                result[config] = json_data[key] if strict else json_data.get(key)

    if len(result) == 1 and result.keys()[0] == '':
        return result['']
    else:
        return result
