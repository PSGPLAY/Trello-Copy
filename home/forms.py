from django import forms
from .models import Task, Workspace, Board, BoardList
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'name@example.com'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Choose a username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'Create a password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'Confirm your password'})


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter your password'})
    )


class WorkspaceForm(forms.ModelForm):
    class Meta:
        model = Workspace
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Acme Engineering'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'What is this workspace for?', 'rows': 3}),
        }


class BoardForm(forms.ModelForm):
    workspace = forms.ModelChoiceField(
        queryset=Workspace.objects.none(),
        empty_label="Select a workspace",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Board
        fields = ['name', 'workspace', 'description', 'visibility', 'background']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Project Roadmap'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Brief description of this board', 'rows': 2}),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
            'background': forms.Select(choices=[
                ('gradient-ocean', 'Ocean Blue Gradient'),
                ('gradient-sunset', 'Sunset Glow'),
                ('gradient-emerald', 'Emerald Forest'),
                ('gradient-violet', 'Cosmic Violet'),
                ('gradient-midnight', 'Midnight Slate'),
                ('gradient-amber', 'Amber Sunrise'),
            ], attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['workspace'].queryset = Workspace.objects.filter(owner=user)


class BoardListForm(forms.ModelForm):
    class Meta:
        model = BoardList
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter list title...'}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'label_color']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a title for this card...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add a more detailed description...', 'rows': 3}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'label_color': forms.Select(choices=[
                ('blue', 'Blue (Info)'),
                ('green', 'Green (Complete / Low)'),
                ('amber', 'Amber (Medium)'),
                ('red', 'Red (High Priority)'),
                ('purple', 'Purple (Design)'),
                ('teal', 'Teal (Feature)'),
            ], attrs={'class': 'form-select'}),
        }