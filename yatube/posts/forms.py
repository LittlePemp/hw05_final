from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {'group': 'Группа', 'text': 'Текст', 'image': 'Картинка'}
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Текст поста'})}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Текст'}
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Текст комментария'})}
