from django import forms
from django.forms import ModelForm
from .models import Book, Rating, Comment


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = [
            'name',
            'web',
            'price',
            'picture',
        ]

class RatingForm(ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']

        widgets = {
            'rating': forms.Select(choices=[(i, f'{i}/5') for i in range(1, 6)]),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'cols': 60,
                'placeholder': 'Write a comment...',
            }),
        }
        labels = {
            'text': '',
        }