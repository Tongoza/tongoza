from django import forms
from .models import *


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'image', 'caption', 'public']


class PostUpdateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'caption', 'image', 'public']
