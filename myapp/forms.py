from django import forms

class UploadPDFForm(forms.Form):
    company = forms.CharField(max_length=50)
    file = forms.FileField()
    period_end_date = forms.DateField(
        required=False,           
        widget=forms.DateInput(attrs={"type": "date"}))