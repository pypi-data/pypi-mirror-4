import cherrypy
import logging

from mako.template import Template
from mako.lookup import TemplateLookup
from pkg_resources import ResourceManager

resource_manager = ResourceManager()

static_dir = resource_manager.resource_filename(__name__, 'templates/static')
template_dir = resource_manager.resource_filename(__name__, 'templates')

class Root:
    tmpl_lookup = TemplateLookup(directories = [template_dir, ])
    root_tmpl = Template(text = resource_manager.resource_string(__name__, "templates/template.html"), lookup = tmpl_lookup)
    #bundles_tmpl = Template(text = resource_manager.resource_string(__name__, "templates/bundles.html"), lookup = tmpl_lookup)

    def __init__(self, api, api_path):
        self.api = api
        self.api_path = api_path

    @cherrypy.expose
    def index(self):
        return self.render_template('bottles.html')


    @cherrypy.expose
    def js(self):
        cherrypy.response.headers['Content-Type'] = 'application/javascript'
        return ""

    def render_template(self, name, **kwargs):
        tmpl = self.tmpl_lookup.get_template(name)
        args = { 'api': self.api, 'api_path': self.api_path }
        return tmpl.render(**args)




def start_server(address, port, deployer, api_app, api_path = "/api"):
    log = logging.getLogger("start_server")
    log.debug("Static dir: %s", static_dir)
    global_conf = {'global': {'server.socket_host': address,
                       'server.socket_port': int(port),
                       'engine.autoreload_on': False
                       },
            }
    root_conf = {'/static': {
                        'tools.staticdir.on': True,
                        'tools.staticdir.dir': static_dir
                        }}
    cherrypy.tree.mount(Root(api_app, api_path), "/", config = root_conf)
    cherrypy.tree.graft(api_app, '/api')
    cherrypy.config.update(global_conf)
    cherrypy.engine.start()
