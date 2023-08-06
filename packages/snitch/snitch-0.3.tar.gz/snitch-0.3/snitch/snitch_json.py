import json

import raven.utils.json


class EvenBetterJSONEncoder(raven.utils.json.BetterJSONEncoder):
    """JSON Encoder that falls back to repr when serialisation fails"""
    def default(self, obj):
        try:
            return super(EvenBetterJSONEncoder, self).default(obj)
        except TypeError:
            return repr(obj)


def dumps(value):
    return json.dumps(value, cls=EvenBetterJSONEncoder)
