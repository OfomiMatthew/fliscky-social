from django import forms 
from .models import Post, Comment



# class NewPostForm(forms.ModelForm):
#   # content = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple':True}),required=True)
#   content = forms.FileField(required=True, widget=forms.FileInput(attrs={
#         'accept': 'image/*,video/*',
#         'id': 'file-upload',
       
#     }))
#   caption = forms.CharField(widget=forms.Textarea(),required=True)
#   tags = forms.CharField(widget=forms.TextInput(),required=False)
  
#   class Meta:
#     model = Post 
#     fields = ['content','caption','tags']



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

class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'tags']
    
    content = MultipleFileField(
        required=True,
        help_text="Upload images or videos (Max 100MB each)"
    )
    tags = forms.CharField(required=False)
    
    
class CommentForm(forms.ModelForm):
  text = forms.CharField(widget=forms.Textarea(),required=False)
  
  class Meta:
    model = Comment 
    fields = ['text']
    
  