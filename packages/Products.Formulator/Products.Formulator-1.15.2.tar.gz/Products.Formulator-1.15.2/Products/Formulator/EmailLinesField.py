
from Products.Formulator.StandardFields import LinesField
from Products.Formulator.Validator import LinesValidator

import re

# This regex allows for a simple username or a username in a
# multi-dropbox (%). The host part has to be a normal fully qualified
# domain name, allowing for 6 characters (.museum) as a TLD. No bang
# paths (uucp), no dotted-ip-addresses, no angle brackets around the
# address (we assume these would be added by some custom script if
# needed), and of course no characters that don't belong in an e-mail
# address.

pattern = re.compile('^[0-9a-zA-Z_&.%+-]+@([0-9a-zA-Z]([0-9a-zA-Z-]*[0-9a-zA-Z])?\.)+[a-zA-Z]{2,6}$')

class EmailLinesValidator(LinesValidator):

    message_names = LinesValidator.message_names + ['not_email']

    not_email = 'You did not enter valid email addresses.'

    def check(self, field, value, failover):
        if not failover:
            for line in value:
                if pattern.search(line.lower()) is None:
                    self.raise_error('not_email', field)


EmailLinesValidatorInstance = EmailLinesValidator()


class EmailLinesField(LinesField):
    meta_type = 'EmailLinesField'
    validator = EmailLinesValidatorInstance

