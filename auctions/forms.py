from django import forms
from .models import Listing, Comment

class ListingCreateForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title','description','starting_bid','thumbnail','category']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']