import ioc.loader
import os

class Extension(object):
    def load(self, config, container_builder):

        path = os.path.dirname(os.path.abspath(__file__))

        loader = ioc.loader.YamlLoader()
        loader.load("%s/resources/config/services.yml" % path, container_builder)

        container_builder.parameters.set('shirka.web.public.dir', "%s/resources/public" % path)
        