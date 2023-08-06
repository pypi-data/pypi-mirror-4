from django import forms


class WallPostForm(forms.Form):
    message = forms.CharField(max_length=200)