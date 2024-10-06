from django import forms
from .models import CommentModel
from django.shortcuts import get_object_or_404, redirect

class CommentForm(forms.ModelForm):
    parent = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = CommentModel
        fields = ['text', 'parent']

