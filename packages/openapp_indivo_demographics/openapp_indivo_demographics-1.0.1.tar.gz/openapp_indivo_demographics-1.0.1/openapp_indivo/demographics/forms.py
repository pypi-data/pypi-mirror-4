# This is the data entry form. It is a model form so much of the logic is in 
# the model.
from django import forms

import models

class DemographicsForm(forms.ModelForm):
    _errors = None
    
    class Meta:
        model = models.Demographics

    def as_django_admin(self):
        from formadmin.forms import as_django_admin
        return as_django_admin(self)
