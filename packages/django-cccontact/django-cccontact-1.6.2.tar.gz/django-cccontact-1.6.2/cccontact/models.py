from django.db import models
from cccontact import listeners
from cccontact import signals


signals.contact_form_is_valid.connect(
        listeners.send_contact_form_email,
        sender=None,
        dispatch_uid='send_contact_form_email')
