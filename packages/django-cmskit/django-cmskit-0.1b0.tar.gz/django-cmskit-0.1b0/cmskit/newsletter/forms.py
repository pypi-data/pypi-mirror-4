# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from cmskit.newsletter.models import Subscription

class SubscriptionForm(forms.ModelForm):
    '''
    TODO:
    
    '''
    email = forms.EmailField(widget=forms.TextInput(
                attrs={'class': 'email text', 'placeholder': _('Email address')}))
    subscribed = forms.BooleanField(widget=forms.HiddenInput(), initial=True)

    class Meta:
        model = Subscription

    def clean(self):
        '''
        Essentially I don't care if the email already exists in the app.
        So I'm allowing the form to not care about existing email address.
        User XY@example.com can sign up 100x and I just keep saying "success".
        
        Otherwise this form would raise an exception since email is a
        unique field in the database.
        
        '''
        
        email = self.cleaned_data.get('email')
        if email:
            try:
                existing = Subscription.objects.get(email__exact=email)        
                pass
            except Subscription.DoesNotExist:
                pass
        
        return self.cleaned_data
        
        
        