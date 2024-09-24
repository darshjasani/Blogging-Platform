from django import forms
from .models import CommentModel

class CommentForm(forms.ModelForm):
    parent = forms.CharField(widget=forms.HiddenInput(), required=False)  # Add hidden field for parent comment
    
    class Meta:
        model = CommentModel
        fields = ['text', 'parent']  # Include 'parent' in the fields
