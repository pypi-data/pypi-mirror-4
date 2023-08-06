from tg import request, config
from tg.decorators import Decoration

class expose_mobile(object):
    def __init__(self, template, content_type='text/html'):
        if template in config.get('renderers', []):
            engine, template = template, ''
        elif ':' in template:
            engine, template = template.split(':', 1)
        elif template:
            engine = config.get('default_renderer')
        else:
            engine, template = None, None

        self.template = template
        self.engine = engine
        self.content_type = content_type

    def hook_func(self, *args, **kwargs):
        if request.is_mobile:
            try:
                override_mapping = request._override_mapping
            except:
                override_mapping = request._override_mapping = {}
            override_mapping[self.func] = {self.content_type:(self.engine, self.template, [], {})}

    def __call__(self, func):
        self.func = func
        deco = Decoration.get_decoration(func)
        deco.register_hook('before_render', self.hook_func)
        return func
