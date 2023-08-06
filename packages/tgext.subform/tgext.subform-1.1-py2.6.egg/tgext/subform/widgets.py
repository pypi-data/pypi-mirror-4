import inspect
from formencode import Invalid
from formencode.validators import Email
from tw.core import Widget, JSLink, CSSLink
from tw.forms import SubmitButton, TableForm
from tw.dojo import dojo_js
from tg.decorators import without_trailing_slash

from sprox.widgets import PropertySingleSelectField
from sprox.formbase import AddRecordForm, EditableForm

select_field_with_add_js = JSLink(modname="tgext.subform",
                       filename="static/javascript/select_field_with_add.js",
                       javascript=[dojo_js,]
                       )

select_field_with_add_css = CSSLink(modname="tgext.subform",
                       filename="static/css/select_field_with_add.css",
                       )
#this needs to be defined for the tw middleware to serve the image
opener_img = CSSLink(modname="tgext.subform",
                       filename="static/images/triangle-solid-up.png",
                       )

class SubformJS(Widget):
    template="""<script type="text/javascript">
dojo.ready(function(){
    ${form_id}_helper=new SubForm({form_id:'${form_id}',
                                    subtype:'${subtype}',
                                    display_field_name:'${display_field_name}',
                                    pk_names:['${pk_names}'],
                                    related_subforms:${related_subforms}});
});
</script>
"""
    params=['form_id', 'subtype', 'display_field_name', 'pk_names', 'related_subforms']


class TableSubform(TableForm):
    template = 'mako:tgext.subform.templates.table_subform'

class AddRecordSubform(AddRecordForm):
    __base_widget_type__ = TableSubform

class EditRecordSubform(EditableForm):
    __base_widget_type__ = TableSubform

class SelectFieldWithAdd(PropertySingleSelectField):
    subform_params = ('__field_widget_types__',
                      '__field_validator_types__',
                      '__field_validators__',
                      '__base_widget_args__',
                      '__add_fields__',
                      '__omit_fields__'
        )

    params = {'__field_widget_types__':{},
              '__field_validator_types__':{}, 
              '__base_widget_args__':{},
              '__add_fields__':{},
              '__omit_fields__':None,
              'related_subforms':'',
              'add_record_form_type':''
              }
    __field_widget_types__ = {}
    __field_validator_types__ = {}
    __field_validators__ = {}
    __base_widget_args__ = {}
    __add_fields__ = {}
    __omit_fields__ = None

    javascript = [select_field_with_add_js,]
    css = [select_field_with_add_css,]
    add_record_form_type = AddRecordSubform
    
    template = "mako:tgext.subform.templates.select_field_with_add"
    
    @property
    def _target(self):
        field = self.provider.get_field(self.entity, self.field_name)
        if hasattr(field, 'argument'):
            target = field.argument
        elif inspect.isfunction(field):
            target = field()
        if inspect.isfunction(target):
            target = target()
        return target

    @property
    def _subform_id(self):
        target = self._target
        target_name = target.__name__.lower()
        return '_'.join((self.field_name, target_name, 'subform'))
        
    @property
    def __subform__(self):

        entity = self._target
        target_name = entity.__name__.lower()
        subform_id = self._subform_id

        self.__base_widget_args__.update({'id':subform_id})

        if 'submit' not in self.__add_fields__:
            self.__add_fields__['submit'] = SubmitButton('submit',
                attrs={'onclick':
                       "javascript:return function(){%s_helper.validate(); return false;}();"%subform_id})

        class ARF(self.add_record_form_type):
            __entity__ = entity

        #apply the subform params to the ARF
        for param in self.subform_params:
            setattr(ARF, param, getattr(self, param))

        subform = ARF(self.provider.session)

        return subform
    
    @property
    def _display_field_name(self):
        view_names = self.dropdown_field_names
        if view_names is None:
            view_names = ['_name', 'name', 'description', 'title']

        return self.provider.get_view_field_name(self._target, view_names)

    @property
    def _pk_names(self):
        return self.provider.get_primary_fields(self._target)

    def _update_subform(self, d):
        display_field_name = self._display_field_name
        pk_names = self._pk_names
        related_subforms=self.related_subforms
        form_id = self._subform_id

        target = self._target
        target_name = target.__name__.lower()

        if related_subforms is None:
            related_subforms = []
        else:
            related_subforms = ['%s_%s_subform'%(i, target_name) for i in related_subforms]
            related_subforms = "['%s']"%"','".join(related_subforms)

        d['subform_id'] = form_id
        d['add_form'] = self.__subform__
        d['model_name'] = self.field_name
        d['subform_js'] = SubformJS(form_id=form_id,
            subtype=self.field_name,
            pk_names="','".join(pk_names),
            related_subforms=related_subforms,
            display_field_name=display_field_name);

        return d

    def update_params(self, d):
        d = PropertySingleSelectField.update_params(self, d)

        self._update_subform(d)

        return d
