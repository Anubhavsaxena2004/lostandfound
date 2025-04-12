from django import forms
from .models import FoundItem, LostItem, Message

class FoundItemForm(forms.ModelForm):
    brand = forms.CharField(max_length=100, required=False)
    color = forms.CharField(max_length=50, required=False)
    size = forms.CharField(max_length=50, required=False)
    storage_location = forms.CharField(max_length=255, required=False)
    found_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    unique_identifiers = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        help_text="Any unique marks, serial numbers, or identifying features"
    )
    latitude = forms.DecimalField(
        max_digits=9, 
        decimal_places=6,
        required=False,
        widget=forms.HiddenInput()
    )
    longitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = FoundItem
        fields = [
            'description', 'location', 'photo', 'found_date', 'found_time',
            'brand', 'color', 'size', 'unique_identifiers', 'storage_location',
            'submitter_name', 'submitter_contact', 'submitter_email',
            'latitude', 'longitude'
        ]
        widgets = {
            'found_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class LostItemForm(forms.ModelForm):
    brand = forms.CharField(max_length=100, required=False)
    color = forms.CharField(max_length=50, required=False) 
    size = forms.CharField(max_length=50, required=False)
    unique_identifiers = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        help_text="Any unique marks, serial numbers, or identifying features"
    )
    latitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        widget=forms.HiddenInput()
    )
    longitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = LostItem
        fields = ['description', 'location', 'photo', 'lost_date', 'brand', 'color', 'size', 'unique_identifiers', 'latitude', 'longitude']
        widgets = {
            'lost_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message here...'
            })
        }
