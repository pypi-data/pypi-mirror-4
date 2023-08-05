from django import forms
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    username = forms.RegexField(max_length=30,
        regex=r'^[\w.@+-]+$',
        error_messages = {
            'invalid': u'This value may contain only letters, numbers and @/./+/-/_ characters.'})
    password = forms.CharField(max_length=100, required=False, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=100, required=False, widget=forms.PasswordInput(), label=u'Confirm Password')

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean(self):
        cleaned_data = self.cleaned_data
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password != password2:
            self._errors['password'] = self.error_class([u'Passwords do not match.'])
            try:
                del cleaned_data['password']
            except KeyError:
                pass
            try:
                del cleaned_data['password2']
            except KeyError:
                pass
        return cleaned_data

    def save(self, *args, **kwargs):
        password = self.cleaned_data.get('password')
        if password:
            self.instance.set_password(password)
        return super(UserForm, self).save(*args, **kwargs)
