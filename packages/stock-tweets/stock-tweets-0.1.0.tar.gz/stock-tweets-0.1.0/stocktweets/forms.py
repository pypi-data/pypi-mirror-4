from django import forms

class AddSymbolForm(forms.Form):
	symbol = forms.CharField(max_length=48)
