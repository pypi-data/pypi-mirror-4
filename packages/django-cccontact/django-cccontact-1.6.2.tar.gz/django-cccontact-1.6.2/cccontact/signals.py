from django.dispatch import Signal

"""send notification that the form validated"""
contact_form_is_valid = Signal(providing_args=['request','form'])
