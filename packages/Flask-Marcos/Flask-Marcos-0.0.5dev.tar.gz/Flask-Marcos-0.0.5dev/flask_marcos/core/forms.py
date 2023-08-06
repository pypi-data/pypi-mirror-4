
from wtforms_alchemy import model_form_factory


__author__ = 'eneldoserrata'


class GenericForm(object):

    def __init__(self, model):
        self.model = model

    def create_form(self):
        from flask.ext.wtf.form import Form
        class Form(model_form_factory(Form)):
            class Meta:
                model = self.model

        return Form




