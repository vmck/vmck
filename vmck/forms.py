from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField(label='Select archive',
                           widget=forms.FileInput(attrs={'accept': 'application/zip'}))  # noqa: E501
