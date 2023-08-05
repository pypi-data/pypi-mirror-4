from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from cccontact import settings as c_settings
from cccontact.signals import contact_form_is_valid


def complete(request):
    return render_to_response(
            'cccontact/complete.html',
            {},
            context_instance=RequestContext(request))

def contact(request):
    # get the forms and the model
    form_cls = c_settings.FORM

    # make the form
    form = form_cls()

    # process post
    if request.method == 'POST':
        form = form_cls(request.POST)
        if form.is_valid() and request.POST.get('message') == None:
            #form.save()
            responses = contact_form_is_valid.send(
                    sender=None,
                    request=request,
                    form=form)
            messages.success(request, 'Your message has been sent')
            return HttpResponseRedirect(reverse('cccontact:complete'))
        # not valid - set a message
        messages.error(request,
                'There are a few errors with the information you\'ve'\
                ' entered, correct them and try again')

    # return the response
    return render_to_response(
            'cccontact/contact.html',
            {'form': form},
            context_instance=RequestContext(request))
