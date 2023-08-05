import itertools


def take_while(predicate, items):
    return list(itertools.takewhile(predicate, items))


def drop_while(predicate, items):
    return list(itertools.dropwhile(predicate, items))


def not_(func):
    return lambda *args, **kwargs: not func(*args, **kwargs)


def first(predicate, iterable):
    for item in iterable:
        if predicate(item):
            return item
    return None


def rfirst(predicate, iterable):
    return first(predicate, reversed(list(iterable)))


def rekey_dict(d, key_map):
    """
    Renames the keys in `d` based on `key_map`.
    `d` is a dictionary whose keys are a superset of the keys in `key_map`.
    `key_map` is a dictionary whose keys match at least some of the keys in `d` and whose values
              are the new key names for `d`.

    For example:
        rekey_dict({'a': 1, 'b': 2}, {'a': 'b', 'b': 'c'}) =
            {'b': 1, 'c': 2}
    """
    # Create a new dictionary containing only the remapped key names.
    new_dict = {new_key: d[old_key]
                for old_key, new_key in key_map.iteritems()
                if old_key in d}

    # Copy whatever key/value pairs were left after the remapping into the new dictionary.
    keys_left = [key for key in d.keys() if key not in new_dict]
    for key in keys_left:
        new_dict[key] = d[key]

    return new_dict


def dict_map(d, func_dict):
    return {key: func(d[key]) for key, func in func_dict.iteritems() if key in d}


def subdict_matches(d, sub):
    for key, value in sub.iteritems():
        if key not in d or d[key] != value:
            return False
    return True


def filter_dict(predicate, d):
    return {key: value for key, value in d.iteritems() if predicate(value)}
