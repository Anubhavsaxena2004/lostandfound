from django import forms
from .models import VerificationQuestion

class VerificationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.questions = VerificationQuestion.objects.filter(is_active=True)
        
        for question in self.questions:
            self.fields[f'question_{question.id}'] = forms.CharField(
                label=question.question_text,
                required=True,
                widget=forms.Textarea(attrs={'rows': 2})
            )

    def clean(self):
        cleaned_data = super().clean()
        # Store questions for easy access in view
        self.questions = VerificationQuestion.objects.filter(is_active=True)
        return cleaned_data
