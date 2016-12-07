import json
import string
import random
import inspect

from faker import Faker 
fake = Faker()


def gen_string(_len):
    ascii_chars = string.ascii_letters + "0123456789"
    return ''.join(random.choice(ascii_chars) for _ in range(_len))


def gen_int(_min=0, _max=1, _len=None):
    if _len is not None:
        return random.randint(10**(_len-1), (10**_len)-1)        
    else:
        return random.randint(_min, _max)


def gen_timestamp():
    return int(fake.date_time_this_month().strftime("%s"))


DEFAULT_GENERATORS = {
    'string': gen_string,
    'int': gen_int,
    'bool': fake.boolean,
    'text': fake.text,
    'name': fake.name,
    'email': fake.email,
    'timestamp': fake.email, #gen_timestamp,
    'datetime': fake.email, #gen_timestamp,
}


def _seanify_recursive(sean_json, generators, path=None):    
    if path is None:
        path = []

    if isinstance(sean_json, list):
        return random.choice(sean_json)

    if not isinstance(sean_json, dict):
        raise TypeError('obj not a dict, {}, path={}'.format(sean_json, path))

    stype = sean_json.get('_type', None)
    svalue = sean_json.get('_val', None)
    sformat = sean_json.get('_format', None)

    if stype is None:
        return {
            k: _seanify_recursive(v, generators, path=path + [k])
            for k, v in sean_json.items()
        }    

    elif stype == 'dict':     
        return {
            k: _seanify_recursive(v, generators, path=path+[k])
            for k, v in svalue.items()
        }

    elif stype == 'list':
        length = sean_json['_len']
        if svalue is None:
            raise KeyError('need key _val at path {}'.format(path))
        return [
            _seanify_recursive(svalue, generators, path=path) 
            for _ in range(length)
        ]

    else:
        if stype not in generators:
            raise KeyError(
                'no generator for type {} at path={}'.format(stype, path)
            )
        gen = generators[stype]
        kws = {
            k: sean_json[k] 
            for k in inspect.getargspec(gen).args
            if k in sean_json
        }
        value = gen(**kws)
        if sformat:
            return sformat.format(value)
        else:
            return value


def seanify(sean_formatted_json, generator_overrides=None):
    generators = DEFAULT_GENERATORS.copy()
    generators.update(generator_overrides or {})

    return _seanify_recursive(sean_formatted_json, generators)


