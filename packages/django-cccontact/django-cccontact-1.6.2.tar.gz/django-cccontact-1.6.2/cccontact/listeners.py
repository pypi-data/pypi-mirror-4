from mailer import send_html_mail
from django.utils.html import strip_tags
from django.template import loader, Context
from cccontact import settings as c_settings

def send_contact_form_email(sender, request, form, **kwargs):
    """sends the email from the contact form"""
    data = form.cleaned_data
    # render the plain text template
    t = loader.get_template('cccontact/message.txt')
    c = Context({
        'email': data.get('email'),
        'name': data.get('name')})
        'message': data.get('m'),
        'phone': data.get('phone')})
    message = t.render(c)
    print c_settings.RECIPIENTS
    
    send_html_mail(
            data['subject'],
            strip_tags(message),
            message,
            data['email'],
            c_settings.RECIPIENTS)
