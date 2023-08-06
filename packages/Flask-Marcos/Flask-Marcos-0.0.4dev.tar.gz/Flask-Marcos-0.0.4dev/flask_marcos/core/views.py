from flask import request
from flask.ext.restless.views import ProcessingException, jsonify_status_code
from flask.templating import render_template
from flask.views import MethodView
from forms import GenericForm


class ModuleView(MethodView):

    def __init__(self, template_name, jqgrid=None, model=None,  module_name=None, form=None):
        self.template_name = template_name
        self.jqgrid = jqgrid
        self.model = model
        self.module_name = module_name
        if form == None:
            form = GenericForm(model)
            self.form = form.create_form()
        else:
            self.form = form

    def get(self, method):
        try:
            return getattr(self, method)()
        except ProcessingException, e:
            return jsonify_status_code(status_code=e.status_code,
                                       message=e.message)

    def view(self):
        return render_template(self.template_name, form=self.form(request.form), module_name=self.module_name)

    def jqgridcfg(self):
        return self.jqgrid.get_config()




