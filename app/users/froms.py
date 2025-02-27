from django import forms

class UserForms(forms.ModelForm):
    class Meta:
        fields = ["email", "password"]
        