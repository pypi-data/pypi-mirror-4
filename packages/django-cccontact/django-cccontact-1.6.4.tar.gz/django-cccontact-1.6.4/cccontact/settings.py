from django.conf import settings
from cccontact import import_thing

"""The address to send email to"""
RECIPIENTS = getattr(
        settings,
        'CCCONTACT_RECIPIENTS',
        [settings.DEFAULT_FROM_EMAIL,])


"""The form to be used"""
try:
    module, form = import_thing(settings.CCCONTACT_FORM)
except (AttributeError, ImportError):
    module, form = import_thing('cccontact.forms.ContactForm')

FORM = form
