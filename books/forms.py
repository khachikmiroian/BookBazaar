from django import forms
from .models import Comments


class SearchForm(forms.Form):
    query = forms.CharField(label='Search')


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Write your comment...',
                'class': 'form-control',
            }),
        }
