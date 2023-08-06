#
# Copyright 2013 the original author or authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import datetime
from inspect import getmembers, ismethod, getargspec
from logging import getLogger
from json import JSONEncoder, JSONDecoder
from types import MethodType


log = getLogger(__name__)

JSON_CONVERTERS = {
}


def json_ready(original_class):
    module_and_class_name = '%s.%s' % (original_class.__module__, original_class.__name__)
    JSON_CONVERTERS[module_and_class_name] = original_class

    if not hasattr(original_class, 'to_json'):
        for method_name, method in getmembers(original_class, predicate=ismethod):
            if method_name == '__init__':
                serializers = []
                def generate_serializer(arg):
                    def serialize(self, json):
                        json[arg] = getattr(self, arg)
                    return serialize

                for arg in getargspec(method).args:
                    if arg == 'self':
                        continue

                    serializers.append(generate_serializer(arg))

                def to_json(self):
                    json = {'$class': module_and_class_name}
                    for serializer in serializers:
                        serializer(self, json)
                    return json

                original_class.to_json = MethodType(to_json, None, original_class)

                break

    return original_class


class LiveTribeJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if isinstance(o, set):
            return {'$class': '__builtin__.set', 'elements': [e for e in o]}
        try:
            return o.to_json()
        except Exception:
            log.exception('Unable to encode %r', o)
            return JSONEncoder.default(self, o)


class LiveTribeJSONDecoder(JSONDecoder):
    def __init__(self, encoding=None, parse_float=None, parse_int=None, parse_constant=None, strict=True):
        super(LiveTribeJSONDecoder, self).__init__(object_hook=_json_class_decoder, encoding=encoding, parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, strict=strict)


def _json_class_decoder(dictionary):
    if not '$class' in dictionary:
        return dictionary
    module_class = dictionary['$class']
    if module_class in JSON_CONVERTERS:
        class_object = JSON_CONVERTERS[module_class]
        parameters = dict(dictionary)
        parameters.pop('$class')
        o = class_object(**parameters)
    elif module_class == '__builtin__.set':
        o = set(dictionary['elements'])
    else:
        raise ValueError('Unable to decode %s' % module_class)
    return o
