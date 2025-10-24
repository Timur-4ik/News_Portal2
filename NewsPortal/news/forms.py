from django import forms
from .models import Post
from django.core.exceptions import ValidationError

class PostForm(forms.ModelForm):
    title = forms.CharField(max_length = 128)
    class Meta:
       model = Post
       fields = [
           'post_category',
           'title',
           'text',

       ]

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        author = cleaned_data.get("author")

        if author == title:
            raise ValidationError(
                "Описание не должно быть идентично названию."
            )

        return cleaned_data