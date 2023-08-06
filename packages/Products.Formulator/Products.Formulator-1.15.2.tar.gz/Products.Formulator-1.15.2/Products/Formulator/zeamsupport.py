

from Products.Formulator.Errors import ValidationError
from Products.Formulator.interfaces import IForm
from five import grok
from zeam.form.base import Field, Error, NO_VALUE
from zeam.form.base import interfaces
from zeam.form.base.markers import getValue
from zope.interface import Interface, Attribute, providedBy, implementedBy
from zope.interface.interface import Specification


class CustomizedField(object):
    """Proxy around a native Formulator field to be able to
    programmatically change values retrieved with get_value.
    """

    def __init__(self, field, defaults):
        self._field = field
        self._customizations = defaults

    def __getattr__(self, key):
        return getattr(self._field, key)

    def get_value(self, id, **kw):
        if id in self._customizations:
            return self._customizations[id]
        return self._field.get_value(id, **kw)


class IFormulatorField(interfaces.IField):

    meta_type = Attribute(u"Field meta type")

    def customize(customizations):
        """Customization formulator field values.
        """


class IFormulatorWidget(interfaces.IFieldWidget):
    pass


class FormulatorField(Field):
    grok.implements(IFormulatorField)

    def __init__(self, field, form):
        self._form = form
        self._field = field
        self._customizations = {}
        self.required = self._getValue('required', False)
        self.readonly = self._getValue('readonly', False)
        css_class = ['field']
        if self.required:
            css_class.append('field-required')
        self._customizations['css_class'] = ' '.join(css_class)
        super(FormulatorField, self).__init__(None, field.id)

    def _getValue(self, identifier, default=NO_VALUE):
        if identifier in self._customizations:
            return self._customizations[identifier]
        if identifier in self._field.values:
            return self._field.get_value(identifier)
        return default

    def getDefaultValue(self, form):
        self._getValue('default')

    @property
    def meta_type(self):
        return self._field.meta_type

    @property
    def __providedBy__(self):
        return Specification(
            (implementedBy(self.__class__), providedBy(self._field)))

    def customize(self, customizations):
        self._customizations.update(customizations)


def decode(value):
    if not isinstance(value, unicode):
        if isinstance(value, str):
            return value.decode('utf-8')
        return unicode(value)
    return value


class FormulatorWidget(object):
    """Bind a Formulator field to a data.
    """
    grok.implements(IFormulatorWidget)
    order = 0
    alternateLayout = False

    def __init__(self, component, form, request):
        field = component._field.__of__(form.context)
        if component._customizations:
            field = CustomizedField(field, component._customizations)
        self._field = field
        self.component = component
        self.form = form
        self.request = request
        self.identifier = self._field.generate_field_html_id()
        self.title = self._field.get_value('title')
        self.description = self._field.get_value('description')
        self.readonly = component.readonly
        self.required = component.required

    @property
    def error(self):
        return self.form.errors.get(self.identifier, None)

    def clone(new_identifier=None):
        raise NotImplementedError

    def htmlId(self):
        return self.identifier

    def htmlClass(self):
        return self._field.get_value('css_class')

    def isVisible(self):
        return not self._field.get_value('hidden')

    def computeValue(self):
        field = self._field
        if not getValue(self.component, 'ignoreRequest', self.form):
            if 'marker_' + self._key in self.request:
                return field._get_default(self._key, None, self.request)
        if not getValue(self.component, 'ignoreContent', self.form):
            if self.form.getContent() is not None:
                data = self.form.getContentData()
                try:
                    return data.get(self.component.identifier)
                except KeyError:
                    pass
        return field.get_value('default')

    def update(self):
        self._key = self._field.generate_field_key()
        self.value = self.computeValue()

    def render(self):
        field = self._field
        renderer = field.widget.render
        if field.get_value('hidden'):
            renderer = field.widget.render_hidden
        return (decode(renderer(field, self._key, self.value, None))+
                u' <input type="hidden" value="1" name="%s" />' % (
                'marker_' + self._key))


class FormulatorDisplayWidget(FormulatorWidget):

    def render(self):
        field = self._field
        renderer = field.widget.render_view
        return decode(renderer(field, self.value))


grok.global_adapter(
    FormulatorWidget,
    (IFormulatorField, interfaces.IFormData, Interface),
    interfaces.IWidget,
    name=u"input")
grok.global_adapter(
    FormulatorWidget,
    (IFormulatorField, interfaces.IFormData, Interface),
    interfaces.IWidget,
    name=u"hidden")
grok.global_adapter(
    FormulatorDisplayWidget,
    (IFormulatorField, interfaces.IFormData, Interface),
    interfaces.IWidget,
    name=u"display")


class FormulatorExtractor(grok.MultiAdapter):
    grok.implements(interfaces.IWidgetExtractor)
    grok.provides(interfaces.IWidgetExtractor)
    grok.adapts(
        IFormulatorField,
        interfaces.IFieldExtractionValueSetting,
        Interface)

    def __init__(self, component, form, request):
        self._field = component._field
        self.identifier = self._field.generate_field_html_id()
        self.request = request

    def extract(self):
        if not self._field.need_validate(self.request):
            return (NO_VALUE, None)
        try:
            return (self._field.validate(self.request), None)
        except ValidationError, error:
            return (None, Error(error.error_text, self.identifier))

    def extractRaw(self):
        return {}


class FormulatorFieldFactory(grok.Adapter):
    grok.implements(interfaces.IFieldFactory)
    grok.context(IForm)

    def __init__(self, form):
        self.form = form

    def produce(self):
        for field in self.form.get_fields():
            yield FormulatorField(field, self.form)
