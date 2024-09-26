from django import forms
from .models import CommentModel
from django.shortcuts import get_object_or_404, redirect

class CommentForm(forms.ModelForm):
    parent = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = CommentModel
        fields = ['text', 'parent']

    def clean_parent(self):
        parent_id = self.cleaned_data.get('parent')
        if parent_id:
            return get_object_or_404(CommentModel, id=parent_id)
        return None

