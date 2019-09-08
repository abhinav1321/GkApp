from django import forms

class FormStepOne(forms.Form):
    name = forms.CharField(max_length=100)


class FormStepTwo(forms.Form):
    salary = forms.CharField(max_length=100)
