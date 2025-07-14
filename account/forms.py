from django import forms 
from django.contrib.auth.models import User 
from django.core.exceptions import ValidationError 
from .models import Profile



def ForbiddenUsers(value):
  forbidden_users = ['admin','administrator','root']
  
  if value.lower() in forbidden_users:
    raise ValidationError('Invalid name for user')
  
def InvalidUser(value):
  if '@' in value or '+' in value or '-' in value:
    raise ValidationError('This is an invalid user, do not use these characters: @,+,-')
  
def UniqueEmail(value):
  if User.objects.filter(email__iexact=value).exists():
    raise ValidationError('User with this email already exists.')
  
def UniqueUser(value):
  if User.objects.filter(username__iexact=value).exists():
    raise ValidationError('User with this username already exists.')
  
class SignupForm(forms.ModelForm):
  username = forms.CharField(widget=forms.TextInput(),min_length=6,max_length=30,required=True)
  email = forms.CharField(widget=forms.EmailInput(),max_length=300,required=True)
  first_name = forms.CharField(widget=forms.TextInput(),max_length=30,required=True)
  last_name = forms.CharField(widget=forms.TextInput(),max_length=30,required=True)
  password = forms.CharField(widget=forms.PasswordInput(),min_length=6, max_length=30,required=True)
  confirm_password = forms.CharField(widget=forms.PasswordInput(),required=True,label='Confirm Password')
  
  class Meta:
    model = User 
    fields = ['username','email','password','first_name','last_name']
    
  def __init__(self,*args,**kwargs):
    super(SignupForm,self).__init__(*args,**kwargs)
    self.fields['username'].validators.append(ForbiddenUsers)
    self.fields['username'].validators.append(InvalidUser)
    self.fields['username'].validators.append(UniqueUser)
    self.fields['email'].validators.append(UniqueEmail)
    
  def clean(self):
    super(SignupForm,self).clean()
    password = self.cleaned_data.get('password')
    confirm_password = self.cleaned_data.get('confirm_password')
    
    if password != confirm_password:
      self._errors['password'] = self.error_class(['Password do not match. Try again'])
    return self.cleaned_data
  
  
class EditProfileForm(forms.ModelForm):
  picture = forms.ImageField(required=False)
  first_name = forms.CharField(widget=forms.TextInput(),max_length=100,required=False)
  last_name = forms.CharField(widget=forms.TextInput(),max_length=100,required=False)
  location = forms.CharField(widget=forms.TextInput(),max_length=100,required=False)
  social_url = forms.URLField(widget=forms.URLInput(),required=False)
  profile_info = forms.CharField(widget=forms.TextInput(),max_length=300,required=False)
  
  class Meta:
    model = Profile 
    fields = ['picture','first_name','last_name','location','social_url','profile_info']
  