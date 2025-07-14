from django import forms
from .models import Story, StoryStream

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)

class NewStoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['content', 'caption']
    
    content = MultipleFileField(
        required=True,
        help_text="Upload images or videos (Max 100MB each)"
    )
    tags = forms.CharField(required=False)