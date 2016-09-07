from django import forms

class LoginForm(forms.Form):
    user_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email')
    user_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Password")