from flask.blueprints import Blueprint
from jqgrid import JqGrid
from views import ModuleView

READONLY_METHODS = frozenset(('GET', ))

class ModuleManager(object):

    APINAME_FORMAT = '%smodule'

    BLUEPRINTNAME_FORMAT = '%s%s'


    def __init__(self, model=None, manager=None, **kwargs):
        self.init_app(model, manager, **kwargs)

    def init_app(self, model, manager, **kwargs):
        self.app = manager.app
        self.manager = manager
        self.model = model
        manager.create_api(model, **kwargs)

    def create_module(self, *args, **kwargs):
        blueprint = self.create_module_blueprint(*args, **kwargs)
        self.app.register_blueprint(blueprint)

    def create_module_blueprint(self, model, methods=READONLY_METHODS, url_prefix='/module', module_name=None, jqgrid=None,
                               module_link=None, authentication_required=None,
                               template_name=None, template_folder=None, form=None, view=ModuleView):

        if module_name is None:
            module_name = model.__tablename__

        view_endpoint = '/%s' % module_name
        apiname = ModuleManager.APINAME_FORMAT % module_name


        if jqgrid == None:
            pager = "jqgrid_%s_pager" % module_name
            jqgrid = JqGrid(self.model, data_url='api'+view_endpoint, pager_id=pager)

        if template_name is None:
            template_name = 'core/simple_crud.html'

        view_func =  view.as_view(apiname, template_name=template_name, jqgrid=jqgrid, model=model, module_name=module_name)

        blueprintname = self._next_blueprint_name(apiname)

        if template_folder:
            blueprint = Blueprint(blueprintname, __name__, url_prefix=url_prefix, template_folder=template_folder)
        else:
            blueprint = Blueprint(blueprintname, __name__, url_prefix=url_prefix)

        # endpoint functions views
        blueprint.add_url_rule(view_endpoint+'/<method>', view_func=view_func)

        url_view = url_prefix + view_endpoint + '/view'
        if module_link:
            module_link['url'] = url_view
            self.app.config['MODULE_LIST'].append(module_link)
        else:
            module_link = {'url':url_view, 'label':module_name.title(), 'icon_class':'nails'}
            self.app.config['MODULE_LIST'].append(module_link)


        return blueprint


    def _next_blueprint_name(self, basename):
        """Returns the next name for a blueprint with the specified base name.

        This method returns a string of the form ``'{}{}'.format(basename,
        number)``, where ``number`` is the next non-negative integer not
        already used in the name of an existing blueprint.

        For example, if `basename` is ``'personapi'`` and blueprints already
        exist with names ``'personapi0'``, ``'personapi1'``, and
        ``'personapi2'``, then this function would return ``'personapi3'``. We
        expect that code which calls this function will subsequently register a
        blueprint with that name, but that is not necessary.

        """
        # blueprints is a dict whose keys are the names of the blueprints
        blueprints = self.app.blueprints
        existing = [name for name in blueprints if name.startswith(basename)]
        # if this is the first one...
        if not existing:
            next_number = 0
        else:
            # for brevity
            b = basename
            existing_numbers = [int(n.partition(b)[-1]) for n in existing]
            next_number = max(existing_numbers) + 1
        return ModuleManager.BLUEPRINTNAME_FORMAT % (basename, next_number)


class InitModule(object):

    def __init__(self, model= None, manager=None):
        self.model = model
        self.manager = manager
        self.init_app(model, manager)

    def init_app(self, model, manager):
        module = ModuleManager(model, manager)
        module.create_module(model)

