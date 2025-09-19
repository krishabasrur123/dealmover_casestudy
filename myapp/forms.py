from django import forms

class UploadPDFForm(forms.Form):
    file = forms.FileField()
    period_end_date = forms.DateField(
        required=False,           
        widget=forms.DateInput(attrs={"type": "date"}))