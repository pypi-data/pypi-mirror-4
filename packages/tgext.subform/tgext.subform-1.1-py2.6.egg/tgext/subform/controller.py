import inspect
from formencode import Invalid
from tg import expose
from tgext.crud.controller import errors, CrudRestController
from tgext.crud.decorators import catch_errors, registered_validate

from sprox.formbase import AddRecordForm, EditableForm


class SubformMixin(object):


    @property
    def _model(self):
        model = self.model
        if inspect.isfunction(model):
            model = model()
        return model

    def _get_subtype(self, name):
        model = self._model
        field = self.new_form.__provider__.get_field(model, name)
        if hasattr(field, 'argument'):
            model = field.argument
        elif inspect.isfunction(target_field):
            model = target_field()
        if inspect.isfunction(model):
            return model()
        return model
    
    @catch_errors(errors)
    @expose('json')
    def subtype_post(self, *args, **kw):
        model = self._model
        if '__subtype' in kw:
            model = self._get_subtype(kw['__subtype'])
            del kw['__subtype']

        provider = self.new_form.__provider__
        obj = provider.create(model, params=kw)
        provider.session.flush()
        return provider.dictify(obj)

    @expose('json')
    def validate(self, *args, **kw):
        subtype = kw['__subtype']
        method = kw.get('__method', 'add')
        form = self.new_form
        if method == 'edit':
            form = self.edit_form
        
        widget = form.__widget__.children[subtype]
        
        try:
            widget.__subform__.validate(kw)
        except Invalid as e:
            return e.unpack_errors()
        return {}

class SubformController(CrudRestController, SubformMixin):
    pass
