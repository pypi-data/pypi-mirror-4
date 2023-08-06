import webob
import webob.dec

import jinja2
import wsgi
import environment

class main(object):

    def __init__(self, *args, **config):
        self.env = environment.parse_environment(config)
        self.config = config

    @webob.dec.wsgify
    def __call__(self, request):
        path = request.path.split("/")[1]
        if not path:
            path = "index.html"

        template = self.env.get_template(path)
        return webob.Response(template.render(**self.config))
