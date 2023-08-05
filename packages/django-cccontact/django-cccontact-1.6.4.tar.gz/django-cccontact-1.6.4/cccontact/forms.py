from django import forms

class ContactForm(forms.Form):

    name = forms.CharField(
            widget=forms.TextInput(
                attrs={'placeholder': 'What is your name?'}))
    subject = forms.CharField(
            widget=forms.TextInput(
                attrs={'placeholder': 'What do you want to talk about?'}))
    email = forms.EmailField(
            widget=forms.TextInput(
                attrs={'placeholder': 'Where should we reply?'}))
    m = forms.CharField(
            label='Your Message',
            widget=forms.Textarea(
                attrs={'placeholder': 'What do you want to say?'}))
    phone = forms.CharField(
            required=False)
    # this field is a honeypot trap
    message = forms.CharField(
            widget=forms.Textarea(),
            required=False)
