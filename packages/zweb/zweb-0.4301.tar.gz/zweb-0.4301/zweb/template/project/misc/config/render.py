import _env
from os.path import join
from zweb.lib.mako.lookup import TemplateLookup
from misc.config import DEBUG 

_PATH = join(_env.PREFIX, 'html')
template_lookup = TemplateLookup(
    directories=_PATH,
    module_directory='/tmp/%s'%_PATH.strip('/').replace('/', '.'),
    disable_unicode=True,
    encoding_errors='ignore',
    default_filters=['str', 'h'],
    filesystem_checks=DEBUG,
    input_encoding='utf-8',
    output_encoding=''
)


def render(htm, **kwds):
    mytemplate = template_lookup.get_template(htm)
    return mytemplate.render(**kwds)
