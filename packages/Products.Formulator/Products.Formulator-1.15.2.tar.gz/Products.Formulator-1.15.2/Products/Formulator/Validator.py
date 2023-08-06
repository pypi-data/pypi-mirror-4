import re
from threading import Thread
from urllib import urlopen
from urlparse import urljoin
from types import StringTypes

from ZPublisher.TaintedString import TaintedString
from DateTime import DateTime

from Products.Formulator import PatternChecker
from Products.Formulator.DummyField import fields
from Products.Formulator.Errors import ValidationError
from Products.Formulator.helpers import ensure_unicode
from Products.Formulator.i18n import translate as _


try:
    from DateTime.DateTime import DateError, TimeError
    date_time_format_exceptions = (DateError, TimeError)
except ImportError:
    # uh, a host of string based exceptions
    # for DateTime errors, if Zope 2.x, x<7
    date_time_format_exceptions = ('DateTimeError',
                                   'Invalid Date Components',
                                   'TimeError')

NS_FORMULATOR = 'http://infrae.com/namespace/formulator'

class ValidatorBase:
    """Even more minimalistic base class for validators.
    """
    property_names = ['enabled']
    message_names = []

    enabled = fields.CheckBoxField(
        'enabled',
        title="Enabled",
        description=(
            "If a field is not enabled, it will considered to be not "
            "in the form during rendering or validation. Be careful "
            "when you change this state dynamically (in the TALES tab): "
            "a user could submit a field that since got disabled, or "
            "get a validation error as a field suddenly got enabled that "
            "wasn't there when the form was drawn."),
        default=1)

    def raise_error(self, error_key, field):
        raise ValidationError(error_key, field)

    def check(self, field, value, failover=False):
        return value

    def validate(self, field, key, REQUEST):
        pass # override in subclass

    def serializeValue(self, field, value, producer):
        """Given a field, a value and a sax_producer, this method sends
        sax events to the sax producer that represent the XMLified value.
        """
        pass # override in subclass

    def deserializeValue(self, field, value, context=None):
        if isinstance(value, basestring):
            data = value
        else:
            # We have an lxml node
            data = value.text
            if data is None:
                # Try for subvalues
                data = []
                for entry in value.xpath('form:value', namespaces={'form': NS_FORMULATOR}):
                    data.append(entry.text)
                if not data:
                    # Let's put an empty string it is safe.
                    data = ''
        REQUEST = {'key': data, 'key_novalidate': '1'}
        return self.validate(field, 'key', REQUEST)

    def need_validate(self, field, key, REQUEST):
        """Default behavior is always validation.
        """
        return 1


class Validator(ValidatorBase):
    """Validates input and possibly transforms it to output.
    """
    property_names = ValidatorBase.property_names + ['external_validator']
    message_names = ValidatorBase.message_names + ['external_validator_failed']

    external_validator = fields.MethodField(
        'external_validator',
        title="External Validator",
        description=(
            "When a method name is supplied, this method will be "
            "called each time this field is being validated. All other "
            "validation code is called first, however. The value (result of "
            "previous validation) and the REQUEST object will be passed as "
            "arguments to this method. Your method should return true if the "
            "validation succeeded. Anything else will cause "
            "'external_validator_failed' to be raised."),
        default="",
        required=0)


    external_validator_failed = _('The input failed the external validator.')


class StringBaseValidator(Validator):
    """Simple string validator.
    """
    property_names = Validator.property_names + ['required', 'whitespace_preserve']
    message_names = Validator.message_names + ['required_not_found']

    required = fields.CheckBoxField(
        'required',
        title='Required',
        description=(
            "Checked if the field is required; the user has to fill in some "
            "data."),
        default=1)
    whitespace_preserve = fields.CheckBoxField(
        'whitespace_preserve',
        title="Preserve whitespace",
        description=(
            "Checked if the field preserves whitespace. This means even "
            "just whitespace input is considered to be data."),
        default=0)

    required_not_found = _('Input is required but no input given.')

    def check(self, field, value, failover=False):
        if not field.get_value('whitespace_preserve'):
            value = value.strip()
        if not failover:
            if not value and field.get_value('required'):
                self.raise_error('required_not_found', field)
        return value

    def validate(self, field, key, REQUEST):
        return self.check(
            field=field,
            value=REQUEST.get(key, ""),
            failover=key + '_novalidate' in REQUEST)

    def serializeValue(self, field, value, producer):
        # if our value is not a string type, the SAX lib won't eat it,
        # therefore convert to string first
        if type(value) not in (str, unicode):
            value = str(value)
        producer.characters(value)


class StringValidator(StringBaseValidator):
    property_names = StringBaseValidator.property_names +\
                   ['unicode', 'max_length', 'truncate']
    message_names = StringBaseValidator.message_names +\
                  ['too_long']

    unicode = fields.CheckBoxField(
        'unicode',
        title='Unicode',
        description=(
            "Checked if the field delivers a unicode string instead of an "
            "8-bit string."),
        default=0)
    max_length = fields.IntegerField(
        'max_length',
        title='Maximum length',
        description=(
            "The maximum amount of characters that can be entered in this "
            "field. If set to 0 or is left empty, there is no maximum. "
            "Note that this is server side validation."),
        default="",
        required=0)
    truncate = fields.CheckBoxField(
        'truncate',
        title='Truncate',
        description=(
            "If checked, truncate the field if it receives more input than is "
            "allowed. The behavior in this case is to raise a validation "
            "error, but the text can be silently truncated instead."),
        default=0)

    too_long = _('Too much input was given.')

    def check(self, field, value, failover=False):
        value = StringBaseValidator.check(self, field, value, failover)

        # Verify encoding (using form setting)
        value = ensure_unicode(
            value,
            convert=field.get_value('unicode'),
            encoding=field.get_form_encoding())

        if not failover:
            max_length = field.get_value('max_length') or 0
            if max_length > 0 and len(value) > max_length:
                if field.get_value('truncate'):
                    value = value[:max_length]
                else:
                    self.raise_error('too_long', field)

        return value

StringValidatorInstance = StringValidator()


class EmailValidator(StringValidator):
    message_names = StringValidator.message_names + ['not_email']

    not_email = _('You did not enter an email address.')

    # This regex allows for a simple username or a username in a
    # multi-dropbox (%). The host part has to be a normal fully
    # qualified domain name, allowing for 6 characters (.museum) as a
    # TLD.  No bang paths (uucp), no dotted-ip-addresses, no angle
    # brackets around the address (we assume these would be added by
    # some custom script if needed), and of course no characters that
    # don't belong in an e-mail address.
    pattern = re.compile('^[0-9a-zA-Z_&.%+-]+@([0-9a-zA-Z]([0-9a-zA-Z-]*[0-9a-zA-Z])?\.)+[a-zA-Z]{2,6}$')

    def check(self, field, value, failover=False):
        value = StringValidator.check(self, field, value, failover)
        if not failover and value:
            if self.pattern.search(value.lower()) is None:
                self.raise_error('not_email', field)
        return value

EmailValidatorInstance = EmailValidator()


class PatternValidator(StringValidator):
    # does the real work
    checker = PatternChecker.PatternChecker()

    property_names = StringValidator.property_names + ['pattern']
    message_names = StringValidator.message_names + ['pattern_not_matched']

    pattern = fields.StringField(
        'pattern',
        title="Pattern",
        required=1,
        default="",
        description=(
            "The pattern the value should conform to. Patterns are "
            "composed of digits ('d'), alphabetic characters ('e') and "
            "alphanumeric characters ('f'). Any other character in the pattern "
            "should appear literally in the value in that place. Internal "
            "whitespace is checked as well but may be included in any amount. "
            "Example: 'dddd ee' is a Dutch zipcode (postcode). ")
        )


    pattern_not_matched = _("The entered value did not match the pattern.")

    def check(self, field, value, failover=False):
        value = StringValidator.check(self, field, value, failover)
        if not failover and value:
            result = self.checker.validate_value(
                [field.get_value('pattern')], value)
            if result is None:
                self.raise_error('pattern_not_matched', field)
            return result
        return value

PatternValidatorInstance = PatternValidator()


class BooleanValidator(Validator):
    message_names = Validator.message_names + ['not_boolean']

    not_boolean = _('You did not enter an boolean.')

    def check(self, field, value, failover=False):
        if not isinstance(value, bool):
            self.raise_error('not_boolean', field)
        return value

    def validate(self, field, key, REQUEST):
        return not not REQUEST.get(key, 0)

    def serializeValue(self, field, value, producer):
        if value:
            value_string = 'True'
        else:
            value_string = 'False'
        producer.characters(value_string)

    def deserializeValue(self, field, value, context=None):
        if not isinstance(value, basestring):
            value = value.text
        if value == 'True':
            return True
        return False

BooleanValidatorInstance = BooleanValidator()


class IntegerValidator(StringBaseValidator):
    property_names = StringBaseValidator.property_names +\
                   ['start', 'end']
    message_names = StringBaseValidator.message_names +\
                  ['not_integer', 'integer_out_of_range']

    start = fields.IntegerField(
        'start',
        title='Start',
        description=(
            "The integer entered by the user must be larger than or equal to "
            "this value. If left empty, there is no minimum."),
        default="",
        required=0)
    end = fields.IntegerField(
        'end',
        title='End',
        description=(
            "The integer entered by the user must be smaller than this "
            "value. If left empty, there is no maximum."),
        default="",
        required=0)

    not_integer = _('You did not enter an integer.')
    integer_out_of_range = _('The integer you entered was out of range.')

    def check(self, field, value, failover=False):
        if value == "":
            if not failover and field.get_value('required'):
                self.raise_error('required_not_found', field)
            return ""

        if not isinstance(value, int):
            self.raise_error('not_integer', field)

        if not failover:
            start = field.get_value('start')
            end = field.get_value('end')
            if start != "" and value < start:
                self.raise_error('integer_out_of_range', field)
            if end != "" and value >= end:
                self.raise_error('integer_out_of_range', field)
        return value

    def validate(self, field, key, REQUEST):
        value = REQUEST.get(key, "").strip()
        if value:
            try:
                value = int(value)
            except ValueError:
                self.raise_error('not_integer', field)

        return self.check(field, value, key + '_novalidate' in REQUEST)

    def serializeValue(self, field, value, producer):
        value_string = str(value)
        producer.characters(value_string)

IntegerValidatorInstance = IntegerValidator()


class FloatValidator(StringBaseValidator):
    message_names = StringBaseValidator.message_names + ['not_float']

    not_float = _("You did not enter a floating point number.")

    def check(self, field, value, failover=False):
        if value == "":
            if not failover and field.get_value('required'):
                self.raise_error('required_not_found', field)
            return ""

        if not isinstance(value, float):
            self.raise_error('not_float', field)
        return value

    def validate(self, field, key, REQUEST):
        value = REQUEST.get(key, "").strip()
        if value:
            try:
                value = float(value)
            except ValueError:
                self.raise_error('not_float', field)

        return self.check(field, value, key + '_novalidate' in REQUEST)

    def serializeValue(self, field, value, producer):
        value_string = str(value)
        producer.characters(value_string)

FloatValidatorInstance = FloatValidator()


class LinesValidator(StringBaseValidator):
    property_names = StringBaseValidator.property_names +\
                   ['unicode', 'max_lines', 'max_linelength', 'max_length']
    message_names = StringBaseValidator.message_names +\
                  ['too_many_lines', 'line_too_long', 'too_long']

    unicode = fields.CheckBoxField(
        'unicode',
        title='Unicode',
        description=(
            "Checked if the field delivers a unicode string instead of an "
            "8-bit string."),
        default=0)
    max_lines = fields.IntegerField(
        'max_lines',
        title='Maximum lines',
        description=(
            "The maximum amount of lines a user can enter. If set to 0, "
            "or is left empty, there is no maximum."),
        default="",
        required=0)
    max_linelength = fields.IntegerField(
        'max_linelength',
        title="Maximum length of line",
        description=(
            "The maximum length of a line. If set to 0 or is left empty, there "
            "is no maximum."),
        default="",
        required=0)
    max_length = fields.IntegerField(
        'max_length',
        title="Maximum length (in characters)",
        description=(
            "The maximum total length in characters that the user may enter. "
            "If set to 0 or is left empty, there is no maximum."),
        default="",
        required=0)

    too_many_lines = _('You entered too many lines.')
    line_too_long = _('A line was too long.')
    too_long = _('You entered too many characters.')

    def check(self, field, value, failover=False):
        if not isinstance(value, (list, tuple)):
            self.raise_error('not_a_list', field)

        result = []
        encoding = field.get_form_encoding()
        convert = field.get_value('unicode')
        whitespace_preserve = field.get_value('whitespace_preserve')
        if not failover:
            max_line_length = field.get_value('max_linelength') or 0
        else:
            max_line_length = 0
        for line in value:
            # Check each line
            if not whitespace_preserve:
                line = line.strip()
            if max_line_length and len(line) > max_line_length:
                self.raise_error('line_too_long', field)
            result.append(ensure_unicode(line, convert, encoding))

        # Check for input size
        if not failover:
            if not result and field.get_value('required'):
                self.raise_error('required_no_found', field)
            max_lines = field.get_value('max_lines') or 0
            if max_lines and len(result) > max_lines:
                self.raise_error('too_many_lines', field)
        return result

    def validate(self, field, key, REQUEST):
        value = REQUEST.get(key, "").strip()
        if isinstance(value, TaintedString):
            value = str(value)
        if not field.get_value('whitespace_preserve'):
            value = value.strip()

        # Check whether the entire input is too long
        max_length = field.get_value('max_length') or 0
        if max_length and len(value) > max_length:
            self.raise_error('too_long', field)

        # split input into separate lines
        value = value.split("\n")
        return self.check(field, value, key + '_novalidate' in REQUEST)

    def serializeValue(self, field, value, producer):
        value_string = '\n'.join(value)
        producer.characters(value_string)

LinesValidatorInstance = LinesValidator()


class TextValidator(LinesValidator):

    def check(self, field, value, failover=False):
        whitespace_preserve = field.get_value('whitespace_preserve')
        if not whitespace_preserve:
            value = value.strip()

        # Check for input size
        if not failover:
            if not value and field.get_value('required'):
                self.raise_error('required_not_found', field)
            max_length = field.get_value('max_length') or 0
            if max_length and len(value) > max_length:
                self.raise_error('too_long', field)

        encoding = field.get_form_encoding()
        convert = field.get_value('unicode')
        return ensure_unicode(value, convert, encoding)

    def validate(self, field, key, REQUEST):
        value = REQUEST.get(key, "").strip()
        if isinstance(value, TaintedString):
            value = str(value)

        return self.check(field, value, key + '_novalidate' in REQUEST)

    def serializeValue(self, field, value, producer):
        producer.characters(value)

TextValidatorInstance = TextValidator()


class SelectionValidator(StringBaseValidator):
    property_names = StringBaseValidator.property_names + ['unicode']
    message_names = StringBaseValidator.message_names + ['unknown_selection']

    unicode = fields.CheckBoxField(
        'unicode',
        title='Unicode',
        description=(
            "Checked if the field delivers a unicode string instead of an "
            "8-bit string."),
        default=0)

    unknown_selection = _('You selected an item that was not in the list.')

    def check(self, field, value, failover=False):
        value = StringBaseValidator.check(self, field, value, failover)
        convert = field.get_value('unicode')
        encoding = field.get_form_encoding()
        value = ensure_unicode(value, convert, encoding)

        if not failover and value:
            for item in field.get_value('items'):
                if isinstance(item, (list, tuple)):
                    _, candidate = item
                else:
                    candidate = item
                if ensure_unicode(candidate, convert, encoding) == value:
                    break
            else:
                self.raise_error('unknown_selection', field)
            value  = candidate
        return value


SelectionValidatorInstance = SelectionValidator()


class MultiSelectionValidator(Validator):
    property_names = Validator.property_names + ['required', 'unicode']
    message_names = Validator.message_names + [
        'required_not_found', 'unknown_selection']

    required = fields.CheckBoxField(
        'required',
        title='Required',
        description=(
            "Checked if the field is required; the user has to fill in some "
            "data."),
        default=1)
    unicode = fields.CheckBoxField(
        'unicode',
        title='Unicode',
        description=(
            "Checked if the field delivers a unicode string instead of an "
            "8-bit string."),
        default=0)

    required_not_found = _('Input is required but no input given.')
    unknown_selection = _('You selected an item that was not in the list.')

    def check(self, field, value, failover=False):
        if not isinstance(value, (list, tuple)):
            self.raise_error('not_a_list', field)

        # If we selected nothing and entry is required, give error, otherwise
        # give entry list
        if len(value) == 0:
            if not failover and field.get_value('required'):
                self.raise_error('required_not_found', field)
            return []

        convert = field.get_value('unicode')
        encoding = field.get_form_encoding()

        # Convert everything to unicode if necessary
        value = map(lambda v: ensure_unicode(v, convert, encoding), value)

        if not failover:
            # Possible values
            items = set()
            for item in field.get_value('items'):
                if isinstance(item, (tuple, list)):
                    _, candidate = item
                else:
                    candidate = item
                items.add(ensure_unicode(candidate, convert, encoding))

            if set(value).difference(items):
                # Some values are not valid items
                self.raise_error('unknown_selection', field)

        return value

    def validate(self, field, key, REQUEST):
        value = REQUEST.get(key, [])

        # Ensure to have a list
        if not isinstance(value, (list, tuple)):
            value = [value]

        return self.check(field, value, key + '_novalidate' in REQUEST)

    def serializeValue(self, field, values, producer):
        producer.startPrefixMapping(None, NS_FORMULATOR)
        for value in values:
            # XXX How should I handle integer types here?
            producer.startElement('value')
            producer.characters(value)
            producer.endElement('value')
        producer.endPrefixMapping(None)

MultiSelectionValidatorInstance = MultiSelectionValidator()


class FileValidator(Validator):
    property_names = Validator.property_names + ['required']
    message_names = Validator.message_names + [
        'required_not_found','incorrect_enctype']

    required_not_found = _('Input is required but no input given.')
    incorrect_enctype = _('Form enctype appears to be either unset or set to application/x-www-form-urlencoded.  For FileUpload types this needs to be set to "multipart/form-data"')

    required = fields.CheckBoxField(
        'required',
        title='Required',
        description=(
            "Checked if the field is required; the user has to supply a file."),
        default=0)

    def validate(self, field, key, REQUEST):
        f = REQUEST.get(key,None)
        if type(f) in StringTypes:
            self.raise_error('incorrect_enctype', field)
        if field.get_value('required'):
            if f.filename == '':
                #I think we can assume that if the filename part
                # of the content-disposition header is empty, then
                # no file was uploaded.  I suppose we should also check to
                # see if the file is of zero length, too.
                self.raise_error('required_not_found', field)
        return REQUEST.get(key, None)

FileValidatorInstance = FileValidator()


class LinkHelper:
    """A helper class to check if links are openable.
    """
    status = 0

    def __init__(self, link):
        self.link = link

    def open(self):
        try:
            urlopen(self.link)
        except:
            # all errors will definitely result in a failure
            pass
        else:
            # FIXME: would like to check for 404 errors and such?
            self.status = 1


class LinkValidator(StringValidator):
    property_names = StringValidator.property_names + [
        'check_link', 'check_timeout', 'link_type']
    message_names = StringValidator.message_names + ['not_link']

    check_link = fields.CheckBoxField(
        'check_link',
        title='Check Link',
        description=(
            "Check whether the link is not broken."),
        default=0)
    check_timeout = fields.FloatField(
        'check_timeout',
        title='Check Timeout',
        description=(
            "Maximum amount of seconds to check link. Required"),
        default=7.0,
        required=1)
    link_type = fields.ListField(
        'link_type',
        title='Type of Link',
        default="external",
        size=1,
        items=[('External Link', 'external'),
               ('Internal Link', 'internal'),
               ('Relative Link', 'relative')],
        description=(
            "Define the type of the link. Required."),
        required=1)

    not_link = _('The specified link is broken.')

    def validate(self, field, key, REQUEST):
        value = StringValidator.validate(self, field, key, REQUEST)
        if value == "" and not field.get_value('required'):
            return value

        link_type = field.get_value('link_type')
        if link_type == 'internal':
            value = urljoin(REQUEST['BASE0'], value)
        elif link_type == 'relative':
            value = urljoin(REQUEST['URL1'], value)
        # otherwise must be external

        # FIXME: should try regular expression to do some more checking here?

        # if we don't need to check the link, we're done now
        if not field.get_value('check_link'):
            return value

        # resolve internal links using Zope's resolve_url
        if link_type in ['internal', 'relative']:
            try:
                REQUEST.resolve_url(value)
            except:
                self.raise_error('not_link', field)

        # check whether we can open the link
        link = LinkHelper(value)
        thread = Thread(target=link.open)
        thread.start()
        thread.join(field.get_value('check_timeout'))
        del thread
        if not link.status:
            self.raise_error('not_link', field)

        return value

LinkValidatorInstance = LinkValidator()


class DateTimeValidator(Validator):
    property_names = Validator.property_names + [
        'required', 'start_datetime', 'end_datetime', 'allow_empty_time']
    message_names = Validator.message_names + [
        'required_not_found', 'not_datetime', 'datetime_out_of_range']

    required = fields.CheckBoxField(
        'required',
        title='Required',
        description=(
            "Checked if the field is required; the user has to enter something "
            "in the field."),
        default=1)
    start_datetime = fields.DateTimeField(
        'start_datetime',
        title="Start datetime",
        description=(
            "The date and time entered must be later than or equal to "
            "this date/time. If left empty, no check is performed."),
        default=None,
        input_style="text",
        required=0)
    end_datetime = fields.DateTimeField(
        'end_datetime',
        title="End datetime",
        description=(
            "The date and time entered must be earlier than "
            "this date/time. If left empty, no check is performed."),
        default=None,
        input_style="text",
        required=0)
    allow_empty_time = fields.CheckBoxField(
        'allow_empty_time',
        title="Allow empty time",
        description=(
            "Allow time to be left empty. Time will default to midnight "
            "on that date."),
        default=0)


    required_not_found = _('Input is required but no input given.')
    not_datetime = _('You did not enter a valid date and time.')
    datetime_out_of_range = _('The date and time you entered were out of range.')

    def check(self, field, value, failover=False):
        if not isinstance(value, DateTime):
            self.raise_error('not_datetime', field)

        if not failover:
            # check if things are within range
            start_datetime = field.get_value('start_datetime')
            if (start_datetime is not None and value < start_datetime):
                self.raise_error('datetime_out_of_range', field)
            end_datetime = field.get_value('end_datetime')
            if (end_datetime is not None and value >= end_datetime):
                self.raise_error('datetime_out_of_range', field)
        return value

    def validate(self, field, key, REQUEST):
        try:
            year = field.validate_sub_field('year', REQUEST)
            month = field.validate_sub_field('month', REQUEST)
            day = field.validate_sub_field('day', REQUEST)

            if field.get_value('date_only'):
                hour = 0
                minute = 0
            elif field.get_value('allow_empty_time'):
                hour = field.validate_sub_field('hour', REQUEST)
                minute = field.validate_sub_field('minute', REQUEST)
                if hour == '' and minute == '':
                    hour = 0
                    minute = 0
                elif hour == '' or minute == '':
                    raise ValidationError('not_datetime', field)
            else:
                hour = field.validate_sub_field('hour', REQUEST)
                minute = field.validate_sub_field('minute', REQUEST)
        except ValidationError:
            self.raise_error('not_datetime', field)

        # handling of completely empty sub fields
        if ((year == '' and month == '' and day == '') and
            (field.get_value('date_only') or (hour == '' and minute == '')
             or (hour == 0 and minute == 0))):
            if field.get_value('required'):
                self.raise_error('required_not_found', field)
            else:
                # field is not required, return None for no entry
                return None
        # handling of partially empty sub fields; invalid datetime
        if ((year == '' or month == '' or day == '') or
            (not field.get_value('date_only') and
             (hour == '' or minute == ''))):
            self.raise_error('not_datetime', field)


        if field.get_value('ampm_time_style'):
            ampm = field.validate_sub_field('ampm', REQUEST)
            if field.get_value('allow_empty_time'):
                if ampm == '':
                    ampm = 'am'
            hour = int(hour)
            # handling not am or pm
            # handling hour > 12
            if (not (ampm == 'am' or ampm == 'AM') and not (ampm == 'pm' or ampm == 'PM')) or (hour > 12):
                self.raise_error('not_datetime', field)
            if (ampm == 'pm' or ampm == 'PM') and (hour == 0):
                self.raise_error('not_datetime', field)
            elif (ampm == 'pm' or ampm == 'PM') and hour < 12:
                hour += 12

        try:
            result = DateTime(int(year), int(month), int(day), hour, minute)
        except date_time_format_exceptions:
            self.raise_error('not_datetime', field)

        return self.check(field, result, key + '_novalidate' in REQUEST)

    def serializeValue(self, field, value, producer):
        if value is not None:
            value_string = DateTime(value).HTML4()
            producer.characters(value_string)

    def deserializeValue(self, field, value, context=None):
        if isinstance(value, basestring):
            value = value.strip()
        else:
            value = value.text
            if value:
                value.strip()
        if value:
            return DateTime(value)
        return None

DateTimeValidatorInstance = DateTimeValidator()


class SuppressValidator(ValidatorBase):
    """A validator that is actually not used.
    """
    property_names = ValidatorBase.property_names + ['external_validator']

    external_validator = fields.MethodField(
        'external_validator',
        title="External Validator",
        description=(
            "Ignored, as a validator isn't used here."),
        default="",
        required=0,
        enabled=0)

    def need_validate(self, field, key, REQUEST):
        """Don't ever validate; suppress result in output.
        """
        return 0

SuppressValidatorInstance = SuppressValidator()
