# This package may contain traces of nuts
import venusian

def includeme(config):
    config.include('rebecca.todict')


def mapper_adapter(mapper):
    def todict(request, cls):
        return mapper(cls).as_dict()
    return todict


def bpmapper(cls, name=""):
    register_name = name
    def dec(mapper):
        def callback(scanner, name, ob):
            config = scanner.config
            todict_adapter = mapper_adapter(ob)
            config.set_todict(cls, todict_adapter, name=register_name)
        venusian.attach(mapper, callback, 
                        category='pyramid')
        return mapper
    return dec
    
