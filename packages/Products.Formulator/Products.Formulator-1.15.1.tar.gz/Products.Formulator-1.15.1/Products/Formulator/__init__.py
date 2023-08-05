
from Products.Formulator import Form
from Products.Formulator import StandardFields, HelperFields
from Products.Formulator.FieldRegistry import FieldRegistry
from Products.Formulator import Errors
from Products.Formulator import EmailLinesField, InterfaceField
from AccessControl import allow_module

try:
   import Products.Formulator.FSForm
except ImportError:
   # No filesystem site support
   pass

# Allow Errors to be imported TTW
allow_module('Products.Formulator.Errors')

def initialize(context):
    """Initialize the Formulator product.
    """
    # register field classes
    FieldRegistry.registerField(StandardFields.StringField,
                                'www/StringField.gif')
    FieldRegistry.registerField(StandardFields.CheckBoxField,
                                'www/CheckBoxField.gif')
    FieldRegistry.registerField(StandardFields.IntegerField,
                                'www/IntegerField.gif')
    FieldRegistry.registerField(StandardFields.TextAreaField,
                                'www/TextAreaField.gif')
    FieldRegistry.registerField(StandardFields.RawTextAreaField,
                                'www/TextAreaField.gif')
    FieldRegistry.registerField(StandardFields.LinesField,
                                'www/LinesField.gif')
    FieldRegistry.registerField(StandardFields.ListField,
                                'www/ListField.gif')
    FieldRegistry.registerField(StandardFields.MultiListField,
                                'www/MultiListField.gif')
    FieldRegistry.registerField(StandardFields.RadioField,
                                'www/RadioField.gif')
    FieldRegistry.registerField(StandardFields.MultiCheckBoxField,
                                'www/MultiCheckBoxField.gif')
    FieldRegistry.registerField(StandardFields.PasswordField,
                                'www/PasswordField.gif')
    FieldRegistry.registerField(StandardFields.EmailField,
                                'www/EmailField.gif')
    FieldRegistry.registerField(StandardFields.PatternField,
                                'www/PatternField.gif')
    FieldRegistry.registerField(StandardFields.FloatField,
                                'www/FloatField.gif')
    FieldRegistry.registerField(StandardFields.DateTimeField,
                                'www/DateTimeField.gif')
    FieldRegistry.registerField(StandardFields.FileField,
                                'www/FileField.gif')
    FieldRegistry.registerField(StandardFields.LinkField,
                                'www/LinkField.gif')
    FieldRegistry.registerField(StandardFields.LabelField,
                                'www/LabelField.gif')

    # some helper fields
    FieldRegistry.registerField(HelperFields.ListTextAreaField)
    FieldRegistry.registerField(HelperFields.MethodField)
    FieldRegistry.registerField(HelperFields.TALESField)

    # some other fields
    FieldRegistry.registerField(
       EmailLinesField.EmailLinesField, 'www/EmailField.gif')
    FieldRegistry.registerField(
       InterfaceField.InterfaceField, 'www/BasicField.gif')

    # obsolete field (same as helper; useable but not addable)
    FieldRegistry.registerField(
       StandardFields.RangedIntegerField, 'www/RangedIntegerField.gif')

    # register the form itself
    context.registerClass(
        Form.ZMIForm,
        constructors = (Form.manage_addForm,
                        Form.manage_add),
        icon = 'www/Form.gif')

    # make Dummy Fields into real fields
    FieldRegistry.initializeFields()

    # do initialization of Form class to make fields addable
    Form.initializeForm(FieldRegistry)

    # register help for the product
    context.registerHelp()

# monkey patches
from Products.Formulator import monkey
monkey.patch_all()
